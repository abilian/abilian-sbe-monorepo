"""Base Flask application class, used by tests or to be extended in real
applications."""

from __future__ import annotations

import errno

# Temps monkey patches
import os
import sys
import warnings
from collections.abc import Callable, Collection
from functools import cached_property, partial
from itertools import count
from pathlib import Path
from typing import Any

import defusedxml
import jinja2
import sqlalchemy as sa
import sqlalchemy.exc
import svcs
from attrs import field, frozen
from flask import Flask, appcontext_pushed, g, request_started
from flask.config import ConfigAttribute
from loguru import logger

import abilian.core.util
import abilian.i18n
from abilian.config import default_config
from abilian.core import extensions, signals
from abilian.core.plugin_manager import CORE_PLUGINS, PluginManager
from abilian.services import Service, auth_service, settings_service
from abilian.services.security import Anonymous
from abilian.services.security.models import Role
from abilian.setup import setup
from abilian.web.access_blueprint import allow_access_for_roles
from abilian.web.assets import AssetManagerMixin
from abilian.web.errors import ErrorManagerMixin
from abilian.web.jinja import JinjaManagerMixin
from abilian.web.nav import setup_nav_and_breadcrumbs
from abilian.web.util import send_file_from_directory
from abilian.web.views import Registry as ViewRegistry

defusedxml.defuse_stdlib()

db = extensions.db
__all__ = ["Application", "ServiceManager", "create_app"]

# Silence those warnings for now.
warnings.simplefilter("ignore", category=sa.exc.SAWarning)


@frozen
class ServiceManager:
    """Provides lifecycle (register/start/stop) support for services."""

    services: dict[str, Service] = field(factory=dict)

    def add_service(self, name: str, service: Service):
        self.services[name] = service

    def get_service(self, name: str) -> Service:
        return self.services[name]

    def start_services(self, services: list[str] | None = None):
        """Start all services. If a service is already running, nothing happens."""
        if services is None:
            services = self.services.values()
        for service in services:
            if not service.running:
                service.start()

    def stop_services(self):
        """Stop all services. If a service is not running, nothing happens."""
        for service in self.services.values():
            if service.running:
                service.stop()

    def list_services(self):
        return self.services.values()


class Application(
    AssetManagerMixin,
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

    def setup(self, config: type | None):
        self.configure(config)

        svcs.flask.init_app(self)

        # At this point we have loaded all external config files:
        # SQLALCHEMY_DATABASE_URI is definitively fixed (it cannot be defined in
        # database AFAICT), and LOGGING_FILE cannot be set in DB settings.
        self.setup_logging()

        if not self.testing:
            self.init_sentry()

        # time to load config bits from database: 'settings'
        # First init required stuff: db to make queries, and settings service
        extensions.db.init_app(self)
        settings_service.init_app(self)

        self.register_jinja_loaders(jinja2.PackageLoader("abilian.web"))
        self.init_assets()
        self.install_default_handlers()

        with self.app_context():
            setup(self)

            plugins = CORE_PLUGINS + list(self.config["PLUGINS"])
            self.plugin_manager.register_plugins(plugins)

            self.add_access_controller(
                "static", allow_access_for_roles(Anonymous), endpoint=True
            )
            # debugtoolbar: this is needed to have it when not authenticated
            # on a private site. We cannot do this in init_debug_toolbar,
            # since auth service is not yet installed.
            self.add_access_controller(
                "debugtoolbar", allow_access_for_roles(Anonymous)
            )
            self.add_access_controller(
                "_debug_toolbar.static",
                allow_access_for_roles(Anonymous),
                endpoint=True,
            )

        self._finalize_assets_setup()

        # At this point all models should have been imported: time to configure
        # mappers. Normally Sqlalchemy does it when needed but mappers may be
        # configured inside sa.orm.class_mapper() which hides a
        # misconfiguration: if a mapper is misconfigured its exception is
        # swallowed by class_mapper(model) results in this laconic
        # (and misleading) message: "model is not mapped"
        sa.orm.configure_mappers()

        signals.components_registered.send(self)

        with self.app_context():
            if not self.testing:
                signals.register_js_api.send(self)

        # Initialize Abilian core services.
        # Must come after all entity classes have been declared.
        # Delegated to ServiceManager. Will need some configuration love
        # later.
        if not self.testing:
            with self.app_context():
                self.service_manager.start_services()

        self.connect_signals()

    def connect_signals(self):
        appcontext_pushed.connect(self.install_id_generator)
        request_started.connect(setup_nav_and_breadcrumbs)

    # TODO: remove
    def install_id_generator(self, sender: Flask, **kwargs: Any):
        g.id_generator = count(start=1)

    def configure(self, config: type | None):
        if config:
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
        elif not os.access(str(path), os.R_OK | os.W_OK | os.X_OK):
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

           app.add_static_url('myplugin',
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
            endpoint, allow_access_for_roles(Anonymous), endpoint=True
        )


# def setup(app: Flask):
#     config = app.config
#
#     # CSP
#     if not app.debug:
#         csp = config.get("CONTENT_SECURITY_POLICY", DEFAULT_CSP_POLICY)
#         Talisman(app, content_security_policy=csp)
#
#     # Tailwind(app)
#
#     # Debug Toolbar
#     init_debug_toolbar(app)


def create_app(config: type | None = None, **kw: Any) -> Application:
    app = Application(**kw)
    app.setup(config=config)
    return app
