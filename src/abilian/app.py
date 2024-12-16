# Copyright (c) 2012-2024, Abilian SAS

"""Base Flask application class, used by tests or to be extended in real
applications."""

from __future__ import annotations

import errno
import os
import sys
import warnings
from functools import cached_property, partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

import defusedxml
import sqlalchemy as sa
import sqlalchemy.exc
from flask import Flask
from flask.config import ConfigAttribute
from loguru import logger

import abilian.core.util
import abilian.i18n
from abilian.config import default_config
from abilian.core import extensions, signals
from abilian.core.plugin_manager import PluginManager
from abilian.core.service_manager import ServiceManager
from abilian.lib.scanner import scan_package
from abilian.services import auth_service
from abilian.services.security import ANONYMOUS
from abilian.setup import setup_app
from abilian.web.access_blueprint import allow_access_for_roles
from abilian.web.errors import ErrorManagerMixin
from abilian.web.jinja import JinjaManagerMixin
from abilian.web.util import send_file_from_directory
from abilian.web.views import Registry as ViewRegistry

if TYPE_CHECKING:
    from collections.abc import Callable, Collection

    from abilian.services.security.models import Role

__all__ = ["Application", "create_app"]

defusedxml.defuse_stdlib()
# Silence those warnings for now.
warnings.simplefilter("ignore", category=sa.exc.SAWarning)

db = extensions.db


def create_app(config: type | None = None, plugins=None, **kw: Any) -> Application:
    app = Application(**kw)

    # 1: Ensure app.config is properly set up
    app.configure(config)
    app.check_instance_folder(create=True)

    # 2: Scan to pre-register callbacks, services, etc.
    scan_package("abilian.cli")

    # 3: Perform registrations on app
    setup_app(app, plugins=plugins)

    # 4: Perform post-registration actions
    signals.components_registered.send(app)

    return app


class Application(
    # AssetManagerMixin,
    ErrorManagerMixin,
    JinjaManagerMixin,
    Flask,
):
    """Base application class.

    Extend it in your own app.
    """

    default_config = default_config

    #: If True all views will require by default an authenticated user, unless
    #: Anonymous role is authorized. Static assets are always public.
    private_site = ConfigAttribute("PRIVATE_SITE")

    #: instance of :class:`.web.views.registry.Registry`.
    default_view: ViewRegistry

    #: json serializable dict to land in Javascript under Abilian.api
    js_api: dict[str, Any]

    def __init__(self, name: Any | None = None, *args: Any, **kwargs: Any):
        name = name or __name__

        Flask.__init__(self, name, *args, **kwargs)

        self.service_manager = ServiceManager()
        self.plugin_manager = PluginManager(self)

        JinjaManagerMixin.__init__(self)

        self.default_view = ViewRegistry()
        self.js_api = {}

    @cached_property
    def data_dir(self) -> Path:
        path = Path(self.instance_path, "data")
        if not path.exists():
            path.mkdir(0o775, parents=True)

        return path

    def configure(self, config: type | None):
        if config:
            # This is usually the case for tests
            self.config.from_object(config)
        else:
            self.config.from_prefixed_env()

        # Setup babel config
        languages = self.config["BABEL_ACCEPT_LANGUAGES"]
        languages = tuple(
            lang for lang in languages if lang in abilian.i18n.VALID_LANGUAGES_CODE
        )
        self.config["BABEL_ACCEPT_LANGUAGES"] = languages

        # This needs to be done dynamically
        if not self.config.get("SESSION_COOKIE_NAME"):
            self.config["SESSION_COOKIE_NAME"] = f"{self.name}-session"

        if not self.config.get("FAVICO_URL"):
            self.config["FAVICO_URL"] = self.config.get("LOGO_URL")

        if not self.debug and self.config["SECRET_KEY"] == "CHANGEME":  # noqa: S105
            logger.error("You must change the default secret config ('SECRET_KEY')")
            sys.exit()

    def check_instance_folder(self, create=False):
        """Verify instance folder exists, is a directory, and has necessary
        permissions.

        :param:create: if `True`, creates directory hierarchy

        :raises: OSError with relevant errno if something is wrong.
        """
        path = Path(self.instance_path)
        err = None
        eno = 0

        if not path.exists():
            if create:
                logger.info("Create instance folder: {path}", path=str(path))
                path.mkdir(0o775, parents=True)
            else:
                err = "Instance folder does not exists"
                eno = errno.ENOENT
        elif not path.is_dir():
            err = "Instance folder is not a directory"
            eno = errno.ENOTDIR
        elif not os.access(path, os.R_OK | os.W_OK | os.X_OK):
            err = 'Require "rwx" access rights, please verify permissions'
            eno = errno.EPERM

        if err:
            raise OSError(eno, err, str(path))

    def add_url_rule_with_role(
        self,
        rule: str,
        endpoint: str,
        view_func: Callable,
        roles: Collection[Role] = (),
        **options: Any,
    ):
        """See :meth:`Flask.add_url_rule`.

        If `roles` parameter is present, it must be a
        :class:`abilian.service.security.models.Role` instance, or a list of
        Role instances.
        """
        self.add_url_rule(rule, endpoint, view_func, **options)

        if roles:
            self.add_access_controller(
                endpoint, allow_access_for_roles(roles), endpoint=True
            )

    def add_access_controller(self, name: str, func: Callable, endpoint: bool = False):
        """Add an access controller.

        If `name` is None it is added at application level, else if is
        considered as a blueprint name. If `endpoint` is True then it is
        considered as an endpoint.
        """
        auth_state = self.extensions[auth_service.name]

        if endpoint:
            if not isinstance(name, str):
                msg = f"{name!r} is not a valid endpoint name"
                raise ValueError(msg)

            auth_state.add_endpoint_access_controller(name, func)
        else:
            auth_state.add_bp_access_controller(name, func)

    def add_static_url(
        self, url_path: str, directory: str, endpoint: str, roles: Collection[Role] = ()
    ):
        """Add a new url rule for static files.

        :param url_path: subpath from application static url path. No heading
            or trailing slash.
        :param directory: directory to serve content from.
        :param endpoint: flask endpoint name for this url rule.

        Example::

            app.add_static_url(
                'myplugin',
                '/path/to/myplugin/resources',
                endpoint='myplugin_static')

        With default setup it will serve content from directory
        `/path/to/myplugin/resources` from url `http://.../static/myplugin`
        """
        url_path = f"{self.static_url_path}/{url_path}/<path:filename>"
        self.add_url_rule_with_role(
            url_path,
            endpoint=endpoint,
            view_func=partial(send_file_from_directory, directory=directory),
            roles=roles,
        )
        self.add_access_controller(
            endpoint, allow_access_for_roles(ANONYMOUS), endpoint=True
        )
