from __future__ import annotations

import logging
import os
from pathlib import Path

import click
from flask import Blueprint, abort, current_app, g, redirect, request
from flask.cli import AppGroup, FlaskGroup
from flask_env import MetaFlaskEnv
from flask_login import current_user

import abilian.cli
from abilian.app import Application as BaseApplication
from abilian.core.celery import FlaskCelery as BaseCelery
from abilian.core.celery import FlaskLoader as CeleryBaseLoader
from abilian.core.extensions import csrf
from abilian.i18n import _l
from abilian.sbe.apps.social.views.social import social
from abilian.sbe.extension import sbe
from abilian.web.action import actions
from abilian.web.nav import NavItem
from abilian.web.util import url_for

# from abilian.cli import *  # noqa


__all__ = ["create_app"]

logger = logging.getLogger(__name__)

HOME_ACTION = NavItem("section", "home", title=_l("Home"), endpoint="social.home")


class Config(metaclass=MetaFlaskEnv):
    ENV_PREFIX = "FLASK_"

    MAIL_ASCII_ATTACHMENTS = True
    # False: it's ok if antivirus task was run but service
    # couldn't get a result
    ANTIVIRUS_CHECK_REQUIRED = True
    BABEL_ACCEPT_LANGUAGES = ("fr", "en")

    CONTENT_SECURITY_POLICY = {
        "default-src": "'self' https://stats.abilian.com/ https://sentry.io/",
        "child-src": "'self' blob:",
        "img-src": "* data:",
        "style-src": [
            "'self'",
            "https://cdn.rawgit.com/novus/",
            "https://cdnjs.cloudflare.com/",
            "'unsafe-inline'",
        ],
        "object-src": "'self'",
        "script-src": [
            "'self'",
            "https://browser.sentry-cdn.com/",
            "https://stats.abilian.com/",
            "https://cdnjs.cloudflare.com/",
            "'unsafe-inline'",
            "'unsafe-eval'",
        ],
        "worker-src": "'self' blob:",
    }

    DEBUG = False
    PRODUCTION = True


def create_app(config=None, **kw):
    app = Application(__name__, **kw)
    app.config.from_object(Config)

    if not config:
        config_path = Path(app.instance_path) / "config.py"
        if config_path.exists():
            app.config.from_pyfile(str(config_path))

    for k in os.environ:
        if k.startswith("FLASK_"):
            app.config[k[len("FLASK_") :]] = os.environ[k]

    if "DATABASE_URL" in os.environ:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

    # Setup stuff

    # We must register this before blueprint is registered
    social.url_value_preprocessor(on_home_blueprint)

    app.setup(config)

    with app.app_context():
        actions.register(HOME_ACTION)

    app.register_blueprint(MAIN)
    app.before_request(login_required)

    register_cli(app)

    # Done
    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the labster application."""


def register_cli(app):
    for obj in vars(abilian.cli).values():
        if isinstance(obj, (click.core.Command, AppGroup)):
            app.cli.add_command(obj)


@csrf.error_handler
def csrf_error_response(reason):
    # let sentry be aware of csrf failures. They might show app is broken
    # somewhere
    logger.error("Csrf error report, reason: %s", reason, extra={"stack": True})
    return abort(400, reason)


# loader to be used by celery workers
class CeleryLoader(CeleryBaseLoader):
    flask_app_factory = "extranet.app.create_app"


celery = BaseCelery(loader=CeleryLoader)

MAIN = Blueprint("main", __name__, url_prefix="")


@MAIN.route("/")
def home():
    """
    Home page. Actually there is no home page, so we redirect to the most
    appropriate place.
    """
    return redirect(url_for("social.home"))


class Application(BaseApplication):
    APP_PLUGINS = BaseApplication.APP_PLUGINS + [
        "abilian.sbe.apps.notifications",
        "abilian.sbe.apps.wiki",
        "abilian.sbe.apps.wall",
        "abilian.sbe.apps.documents",
        "abilian.sbe.apps.forum",
        "abilian.sbe.apps.communities",
        "abilian.sbe.apps.social",
        "abilian.sbe.apps.preferences",
    ]

    def init_extensions(self):
        super().init_extensions()

        sbe.init_app(self)


def login_required():
    """
    Before request handler to ensure login is required on any view
    """
    if current_app.config.get("NO_LOGIN"):
        return

    if request.path.startswith(current_app.static_url_path):
        return

    if request.url_rule and request.url_rule.endpoint == "geodata.static":
        # geodata blueprint assets
        return

    if request.blueprint in ("login", "first_login", "projects", "notifications"):
        return

    if request.blueprint == "_debug_toolbar" and current_app.debug:
        return

    if not current_user.is_authenticated:
        return redirect(url_for("login.login_form", next=request.url))


def on_home_blueprint(endpoint, values):
    """
    url_value_preprocessor attached to blueprint used for 'home'
    """
    if endpoint == HOME_ACTION.endpoint.name:
        g.nav["active"] = HOME_ACTION.path
