from __future__ import annotations

import warnings

import defusedxml
import sqlalchemy as sa
import sqlalchemy.exc
from flask import Blueprint, Flask, abort
from flask_migrate import Migrate

import abilian.core.util
import abilian.i18n
from abilian.core import extensions
from abilian.services import (
    activity_service,
    antivirus,
    audit_service,
    auth_service,
    blob_store,
    conversion_service,
    index_service,
    preferences_service,
    security_service,
    session_blob_store,
    vocabularies_service,
)
from abilian.web import csrf
from abilian.web.action import actions
from abilian.web.admin import Admin

defusedxml.defuse_stdlib()

db = extensions.db

# Silence those warnings for now.
warnings.simplefilter("ignore", category=sa.exc.SAWarning)


def init_extensions(app: Flask):
    """Initialize flask extensions, helpers and services."""

    init_babel(app)
    extensions.redis.init_app(app)
    extensions.mail.init_app(app)
    extensions.deferred_js.init_app(app)
    extensions.upstream_info.extension.init_app(app)
    actions.init_app(app)

    # auth_service installs a `before_request` handler (actually it's
    # flask-login). We want to authenticate user ASAP, so that sentry and
    # logs can report which user encountered any error happening later,
    # in particular in a before_request handler (like csrf validator)
    auth_service.init_app(app)

    init_csrf(app)

    # webassets
    app.setup_asset_extension()
    app.register_base_assets()

    # Flask-Migrate
    Migrate(app, db)

    # Abilian Core services
    security_service.init_app(app)
    blob_store.init_app(app)
    session_blob_store.init_app(app)
    audit_service.init_app(app)
    index_service.init_app(app)
    activity_service.init_app(app)
    preferences_service.init_app(app)
    conversion_service.init_app(app)
    vocabularies_service.init_app(app)
    antivirus.init_app(app)

    # Admin interface
    Admin().init_app(app)


def init_babel(app: Flask) -> None:
    # Babel (for i18n)
    babel = abilian.i18n.babel
    # Temporary (?) workaround
    babel.locale_selector_func = None
    babel.timezone_selector_func = None

    babel.init_app(app)

    babel.add_translations("wtforms", translations_dir="locale", domain="wtforms")
    babel.add_translations("abilian")


def init_csrf(app: Flask) -> None:
    # CSRF by default
    if app.config.get("WTF_CSRF_ENABLED"):
        # extensions.csrf IS original wtf_csrf
        # abilian_csrf is
        # from .csrf import abilian_csrf
        # from .csrf import wtf_csrf as csrf

        extensions.csrf.init_app(app)  # double initialization
        app.extensions["csrf"] = extensions.csrf
        extensions.abilian_csrf.init_app(app)

    app.register_blueprint(csrf.csrf_blueprint)
