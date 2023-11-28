"""
Setup code for the Abilian Flask application.

TODO:

- finish moving code from abilian.app.Application to here
- split into multiple files
"""
from __future__ import annotations

import errno
import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2
import sqlalchemy as sa
import sqlalchemy.orm
from flask import Flask, appcontext_pushed, request_started
from flask_tailwind import Tailwind
from flask_talisman import DEFAULT_CSP_POLICY, Talisman

from abilian.core import extensions, signals
from abilian.i18n import VALID_LANGUAGES_CODE
from abilian.services import settings_service
from abilian.services.security import Anonymous
from abilian.setup.nav import setup_nav_and_breadcrumbs
from abilian.web.blueprints import allow_access_for_roles
from abilian.web.hooks import init_hooks

if TYPE_CHECKING:
    from abilian.app import Application

logger = logging.getLogger(__name__)


def configure_app(app: Application, config: type | None):
    if config:
        app.config.from_object(config)
    else:
        app.config.from_prefixed_env()

    # Setup babel config
    languages = app.config["BABEL_ACCEPT_LANGUAGES"]
    languages = tuple(lang for lang in languages if lang in VALID_LANGUAGES_CODE)
    app.config["BABEL_ACCEPT_LANGUAGES"] = languages

    # This needs to be done dynamically
    if not app.config.get("SESSION_COOKIE_NAME"):
        app.config["SESSION_COOKIE_NAME"] = f"{app.name}-session"

    if not app.config.get("FAVICO_URL"):
        app.config["FAVICO_URL"] = app.config.get("LOGO_URL")

    if not app.debug and app.config["SECRET_KEY"] == "CHANGEME":  # noqa: S105
        logger.error("You must change the default secret config ('SECRET_KEY')")
        sys.exit()


def setup_app(app: Application, config: type | None):
    configure_app(app, config)

    # At this point we have loaded all external config files:
    # SQLALCHEMY_DATABASE_URI is definitively fixed (it cannot be defined in
    # database AFAICT), and LOGGING_FILE cannot be set in DB settings.
    app.setup_logging()

    appcontext_pushed.connect(app.install_id_generator)

    if not app.testing:
        app.init_sentry()

    # time to load config bits from database: 'settings'
    # First init required stuff: db to make queries, and settings service
    extensions.db.init_app(app)
    settings_service.init_app(app)

    app.register_jinja_loaders(jinja2.PackageLoader("abilian.web"))
    app.init_assets()
    app.install_default_handlers()

    with app.app_context():
        app.init_extensions()
        app.register_plugins()
        app.add_access_controller(
            "static", allow_access_for_roles(Anonymous), endpoint=True
        )

        # debugtoolbar: this is needed to have it when not authenticated
        # on a private site. We cannot do this in init_debug_toolbar,
        # since auth service is not yet installed.
        app.add_access_controller("debugtoolbar", allow_access_for_roles(Anonymous))
        app.add_access_controller(
            "_debug_toolbar.static",
            allow_access_for_roles(Anonymous),
            endpoint=True,
        )

    app._finalize_assets_setup()

    # At this point all models should have been imported: time to configure
    # mappers. Normally Sqlalchemy does it when needed but mappers may be
    # configured inside sa.orm.class_mapper() which hides a
    # misconfiguration: if a mapper is misconfigured its exception is
    # swallowed by class_mapper(model) results in this laconic
    # (and misleading) message: "model is not mapped"
    sa.orm.configure_mappers()

    signals.components_registered.send(app)

    request_started.connect(setup_nav_and_breadcrumbs)
    init_hooks(app)

    # Initialize Abilian core services.
    # Must come after all entity classes have been declared.
    # Inherited from ServiceManager. Will need some configuration love
    # later.
    if not app.testing:
        with app.app_context():
            app.start_services()

    extra_setup(app)


def extra_setup(app: Flask):
    # TODO: rename to something more explicit / group with other similar setup code
    config = app.config

    # CSP
    if not app.debug:
        csp = config.get("CONTENT_SECURITY_POLICY", DEFAULT_CSP_POLICY)
        Talisman(app, content_security_policy=csp)

    Tailwind(app)

    # Debug Toolbar
    init_debug_toolbar(app)


def check_instance_folder(app: Flask, create=False):
    """Verify instance folder exists, is a directory, and has necessary
    permissions.

    :param:create: if `True`, creates directory hierarchy

    :raises: OSError with relevant errno if something is wrong.
    """
    path = Path(app.instance_path)
    err = None
    eno = 0

    if not path.exists():
        if create:
            logger.info("Create instance folder: %s", path)
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


def init_debug_toolbar(app: Flask):
    if not app.debug or app.testing:
        return

    try:
        from flask_debugtoolbar import DebugToolbarExtension
    except ImportError:
        logger.warning("Running in debug mode but flask_debugtoolbar is not installed.")
        return

    dbt = DebugToolbarExtension()
    default_config = dbt._default_config(app)
    init_dbt = dbt.init_app

    if "DEBUG_TB_PANELS" not in app.config:
        # add our panels to default ones
        app.config["DEBUG_TB_PANELS"] = list(default_config["DEBUG_TB_PANELS"])
    init_dbt(app)
    for view_name in app.view_functions:
        if view_name.startswith("debugtoolbar."):
            extensions.csrf.exempt(app.view_functions[view_name])
