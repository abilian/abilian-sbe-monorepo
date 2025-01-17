# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import Any

from flask import Flask
from werkzeug.datastructures import ImmutableDict

from abilian.web.action import Endpoint


class DefaultConfig:
    # Seriously: this need to be changed in production
    SECRET_KEY = "CHANGEME"  # noqa: S105

    # Need to be explicitly defined in production configs
    PRODUCTION = False

    # Security (see
    # https://blog.miguelgrinberg.com/post/cookie-security-for-flask-applications)
    # NB: SESSION_COOKIE_* are now set up by Talisman
    WTF_CSRF_ENABLED = True

    # Babel
    BABEL_ACCEPT_LANGUAGES = ["en"]
    DEFAULT_COUNTRY = None

    # Sentry
    SENTRY_SDK_URL = "https://browser.sentry-cdn.com/4.5.3/bundle.min.js"

    # SQLAlchemy
    SQLALCHEMY_POOL_RECYCLE = 1800  # 30min. default value in flask_sa is None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug settings (override default)
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Abilian-specific
    PRIVATE_SITE = False
    PLUGINS = ()
    ADMIN_PANELS = (
        "abilian.web.admin.panels.dashboard.DashboardPanel",
        "abilian.web.admin.panels.audit.AuditPanel",
        "abilian.web.admin.panels.login_sessions.LoginSessionsPanel",
        "abilian.web.admin.panels.settings.SettingsPanel",
        "abilian.web.admin.panels.users.UsersPanel",
        "abilian.web.admin.panels.groups.GroupsPanel",
        "abilian.web.admin.panels.sysinfo.SysinfoPanel",
        "abilian.web.admin.panels.impersonate.ImpersonatePanel",
        "abilian.services.vocabularies.admin.VocabularyPanel",
        "abilian.web.tags.admin.TagPanel",
    )
    LOGO_URL = Endpoint("abilian_static", filename="img/logo-abilian-32x32.png")
    ABILIAN_UPSTREAM_INFO_ENABLED = False  # upstream info extension
    TRACKING_CODE = ""  # tracking code for web analytics to insert before </body>
    MAIL_ADDRESS_TAG_CHAR = None

    DRAMATIQ_BROKER = "dramatiq.brokers.redis:RedisBroker"


default_config: dict[str, Any] = dict(Flask.default_config)
default_config.update(vars(DefaultConfig))
default_config = ImmutableDict(default_config)
