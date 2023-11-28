"""Base Flask application class, used by tests or to be extended in real
applications."""
from __future__ import annotations

# Temps monkey patches
import json
import urllib.parse

import flask.json
import jinja2
import werkzeug.datastructures
import werkzeug.security
import werkzeug.urls
from markupsafe import Markup, escape

from abilian.backports import safe_str_cmp

# Monkey patching werkzeug, jinja2 and flask to keep working with old version
# of some libraries.
werkzeug.url_encode = urllib.parse.urlencode
werkzeug.FileStorage = werkzeug.datastructures.FileStorage

# Is this still needed? Tests seem to pass without them:
werkzeug.urls.url_encode = urllib.parse.urlencode
werkzeug.urls.url_decode = urllib.parse.parse_qs
werkzeug.security.safe_str_cmp = safe_str_cmp
jinja2.Markup = Markup
jinja2.escape = escape
flask.json.JSONEncoder = json.JSONEncoder

# Rest of the imports
import logging.config
import warnings
from collections.abc import Callable, Collection
from functools import partial
from itertools import count
from pathlib import Path
from typing import Any

import defusedxml
import sqlalchemy as sa
import sqlalchemy.exc
from flask import Blueprint, Flask, abort, g
from flask.config import ConfigAttribute
from flask.helpers import locked_cached_property
from flask_migrate import Migrate

import abilian.core.util
import abilian.i18n
from abilian.config import default_config
from abilian.core import extensions
from abilian.core.celery import FlaskCelery
from abilian.services import auth_service
from abilian.services.security import Anonymous
from abilian.services.security.models import Role
from abilian.web import csrf
from abilian.web.action import actions
from abilian.web.admin import Admin
from abilian.web.assets import AssetManagerMixin
from abilian.web.blueprints import allow_access_for_roles
from abilian.web.errors import ErrorManagerMixin
from abilian.web.jinja import JinjaManagerMixin
from abilian.web.util import send_file_from_directory
from abilian.web.views import Registry as ViewRegistry

from .mixins import PluginManager, ServiceManager
from .setup.main import setup_app
from .setup.services import init_services

defusedxml.defuse_stdlib()

logger = logging.getLogger(__name__)
db = extensions.db
__all__ = ["create_app", "Application", "ServiceManager"]

# Silence those warnings for now.
warnings.simplefilter("ignore", category=sa.exc.SAWarning)


class Application(
    ServiceManager,
    PluginManager,
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

    #: celery app class
    celery_app_cls = FlaskCelery

    def __init__(self, name: Any | None = None, *args: Any, **kwargs: Any):
        name = name or __name__

        Flask.__init__(self, name, *args, **kwargs)

        ServiceManager.__init__(self)
        PluginManager.__init__(self)
        JinjaManagerMixin.__init__(self)

        self.default_view = ViewRegistry()
        self.js_api = {}

    # TODO: remove
    def install_id_generator(self, sender: Flask, **kwargs: Any):
        g.id_generator = count(start=1)

    @locked_cached_property
    def data_dir(self) -> Path:
        path = Path(self.instance_path, "data")
        if not path.exists():
            path.mkdir(0o775, parents=True)

        return path

    def init_extensions(self):
        """Initialize flask extensions, helpers and services."""
        extensions.redis.init_app(self)
        extensions.mail.init_app(self)
        extensions.deferred_js.init_app(self)
        extensions.upstream_info.extension.init_app(self)
        actions.init_app(self)

        # auth_service installs a `before_request` handler (actually it's
        # flask-login). We want to authenticate user ASAP, so that sentry and
        # logs can report which user encountered any error happening later,
        # in particular in a before_request handler (like csrf validator)
        auth_service.init_app(self)

        # webassets
        self.setup_asset_extension()
        self.register_base_assets()

        # Babel (for i18n)
        babel = abilian.i18n.babel
        # Temporary (?) workaround
        babel.locale_selector_func = None
        babel.timezone_selector_func = None

        babel.init_app(self)
        babel.add_translations("wtforms", translations_dir="locale", domain="wtforms")
        babel.add_translations("abilian")
        babel.localeselector(abilian.i18n.localeselector)
        babel.timezoneselector(abilian.i18n.timezoneselector)

        # Flask-Migrate
        Migrate(self, db)

        # CSRF by default
        if self.config.get("WTF_CSRF_ENABLED"):
            extensions.csrf.init_app(self)
            self.extensions["csrf"] = extensions.csrf
            extensions.abilian_csrf.init_app(self)

        self.register_blueprint(csrf.blueprint)

        # images blueprint
        from .web.views.images import blueprint as images_bp

        self.register_blueprint(images_bp)

        init_services(self)

        from .web.coreviews import users

        self.register_blueprint(users.blueprint)

        # Admin interface
        Admin().init_app(self)

        # Celery async service
        # this allows all shared tasks to use this celery app
        if getattr(self, "celery_app_cls", None):
            celery_app = self.extensions["celery"] = self.celery_app_cls()
            # force reading celery conf now - default celery app will
            # also update our config with default settings
            assert celery_app.conf
            celery_app.set_default()

        # dev helper
        if self.debug:
            # during dev, one can go to /http_error/403 to see rendering of 403
            http_error_pages = Blueprint("http_error_pages", __name__)

            @http_error_pages.route("/<int:code>")
            def error_page(code):
                """Helper for development to show 403, 404, 500..."""
                abort(code)

            self.register_blueprint(http_error_pages, url_prefix="/http_error")

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


def create_app(
    config: type | None = None, app_class: type = Application, **kw: Any
) -> Application:
    app = app_class(**kw)
    setup_app(app, config)
    return app
