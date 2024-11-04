from __future__ import annotations

from itertools import count
from typing import Any

import jinja2
import sqlalchemy as sa
import svcs
from flask import Flask, appcontext_pushed, g, request_started
from flask_talisman import DEFAULT_CSP_POLICY, Talisman

from abilian.core import extensions, signals
from abilian.core.plugin_manager import CORE_PLUGINS
from abilian.services import settings_service
from abilian.services.security import Anonymous
from abilian.web.access_blueprint import allow_access_for_roles
from abilian.web.nav import setup_nav_and_breadcrumbs

from .blueprints import setup_blueprints
from .debug import setup_debug
from .extensions import init_extensions, init_sentry


def setup_app(app: Flask):
    # At this point we have loaded all external config files:
    # SQLALCHEMY_DATABASE_URI is definitively fixed (it cannot be defined in
    # database AFAICT), and LOGGING_FILE cannot be set in DB settings.

    svcs.flask.init_app(app)

    # Force flask to create application logger before logging
    # configuration; else, flask will overwrite our settings
    assert app.logger
    init_sentry(app)

    # time to load config bits from database: 'settings'
    # First init required stuff: db to make queries, and settings service
    extensions.db.init_app(app)
    settings_service.init_app(app)

    app.init_assets()
    init_extensions(app)

    app.register_jinja_loaders(jinja2.PackageLoader("abilian.web"))

    app.install_default_handlers()

    with app.app_context():
        if app.debug and not app.testing:
            setup_debug(app)

        # CSP
        if not app.debug:
            csp = app.config.get("CONTENT_SECURITY_POLICY", DEFAULT_CSP_POLICY)
            Talisman(app, content_security_policy=csp)

        setup_blueprints(app)

        plugins = CORE_PLUGINS + list(app.config["PLUGINS"])
        app.plugin_manager.register_plugins(plugins)

        app.add_access_controller(
            "static", allow_access_for_roles(Anonymous), endpoint=True
        )
        # debugtoolbar: this is needed to have it when not authenticated
        # on a private site. We cannot do this in init_debug_toolbar,
        # since auth service is not yet installed.
        app.add_access_controller(
            "debugtoolbar",
            allow_access_for_roles(Anonymous),
        )
        app.add_access_controller(
            "_debug_toolbar.static",
            allow_access_for_roles(Anonymous),
            endpoint=True,
        )

    app.finalize_assets_setup()

    # At this point all models should have been imported: time to configure
    # mappers. Normally Sqlalchemy does it when needed but mappers may be
    # configured inside sa.orm.class_mapper() which hides a
    # misconfiguration: if a mapper is misconfigured its exception is
    # swallowed by class_mapper(model) results in this laconic
    # (and misleading) message: "model is not mapped"
    sa.orm.configure_mappers()

    if not app.testing:
        with app.app_context():
            # Time to generate the JS API
            signals.register_js_api.send(app)

            # Initialize Abilian core services.
            # Must come after all entity classes have been declared.
            # Delegated to ServiceManager. Will need some configuration love
            # later.
            app.service_manager.start_services()

    connect_signals()


def connect_signals():
    appcontext_pushed.connect(install_id_generator)
    request_started.connect(setup_nav_and_breadcrumbs)


# TODO: remove
def install_id_generator(sender: Flask, **kwargs: Any):
    g.id_generator = count(start=1)