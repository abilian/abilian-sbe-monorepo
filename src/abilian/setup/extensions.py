# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import defusedxml
import sqlalchemy as sa
import sqlalchemy.exc
from flask_migrate import Migrate
from loguru import logger

import abilian.core.util
import abilian.i18n
from abilian.core import extensions
from abilian.extensions import vite
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

if TYPE_CHECKING:
    from flask import Flask

defusedxml.defuse_stdlib()

db = extensions.db

# Silence those warnings for now.
warnings.simplefilter("ignore", category=sa.exc.SAWarning)


def init_extensions(app: Flask) -> None:
    """Initialize flask extensions, helpers and services."""

    extensions.redis.init_app(app)
    extensions.mail.init_app(app)
    extensions.deferred_js.init_app(app)
    extensions.upstream_info.extension.init_app(app)

    actions.init_app(app)

    # auth_service installs a `before_request` handler (actually, it's
    # flask-login). We want to authenticate the user ASAP, so that sentry and
    # logs can report which user encountered any error happening later,
    # in particular in a before_request handler (like csrf validator)
    auth_service.init_app(app)

    vite.init_app(app)

    # Make vite functions available in templates
    app.jinja_env.globals["vite"] = vite

    # Quick and dirty vite_asset helper for templates
    def vite_asset(path: str) -> str:
        """Generate HTML tag for Vite asset (CSS or JS)."""
        is_dev = app.config.get("DEBUG", False)

        if is_dev:
            # Development mode - use Vite dev server
            if path.endswith(".css"):
                return f'<link rel="stylesheet" href="http://localhost:5173/{path}" />'
            if path.endswith(".js"):
                return f'<script type="module" src="http://localhost:5173/{path}"></script>'
        else:
            # Production mode - use built assets
            asset_name = (
                path.split("/")[-1].replace(".css", ".css").replace(".js", ".js")
            )
            if path.endswith(".css"):
                return f'<link rel="stylesheet" href="/static/vite/{asset_name}" />'
            if path.endswith(".js"):
                return (
                    f'<script type="module" src="/static/vite/{asset_name}"></script>'
                )
        return ""

    from markupsafe import Markup

    app.jinja_env.globals["vite_asset"] = lambda path: Markup(vite_asset(path))

    # Initialize legacy assets for favicons and other static resources
    from abilian.web import assets as legacy_assets

    legacy_assets.init_app(app)

    init_babel(app)

    init_csrf(app)

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


def init_sentry(app: Flask) -> None:
    """Install Sentry handler if config defines 'SENTRY_DSN'."""
    dsn = app.config.get("SENTRY_DSN")
    if not dsn:
        return

    try:
        import sentry_sdk
    except ImportError:
        logger.error(
            'SENTRY_DSN is defined in config but package "sentry-sdk" is not installed.'
        )
        return

    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
    )
