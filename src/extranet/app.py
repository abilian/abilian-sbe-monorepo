from __future__ import annotations

import os
from pprint import pformat

import click
import toml
from dotenv import load_dotenv
from flask import Blueprint, Response, abort, current_app, g, redirect, request
from flask.cli import AppGroup, FlaskGroup
from flask_login import current_user
from loguru import logger

import abilian.cli
from abilian.app import Application as BaseApplication
from abilian.core.dramatiq.setup import init_dramatiq_engine
from abilian.core.extensions import csrf
from abilian.i18n import _l
from abilian.logutils.configure import connect_logger
from abilian.sbe.apps.social.views.social import social
from abilian.sbe.extension import sbe
from abilian.web.action import actions
from abilian.web.nav import NavItem
from abilian.web.util import url_for

from .config import BaseConfig

# from periodiq import PeriodiqMiddleware


__all__ = ["create_app"]

HOME_ACTION = NavItem("section", "home", title=_l("Home"), endpoint="social.home")


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


def create_app(config=None, **kw):
    # global broker

    app = Application(__name__, **kw)
    app.config.from_object(BaseConfig)

    if not config:
        read_config(app)
        app.config.from_prefixed_env()

    if "DATABASE_URL" in os.environ:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

    # Setup stuff
    connect_logger(logger)

    # show all app config
    logger.info(pformat(dict(sorted(app.config.items()))))

    # We must register this before blueprint is registered
    social.url_value_preprocessor(on_home_blueprint)

    app.setup(config)

    with app.app_context():
        actions.register(HOME_ACTION)

    app.register_blueprint(MAIN)
    app.before_request(login_required)

    register_cli(app)

    init_dramatiq_engine(app)

    # Done
    return app


def read_config(app):
    load_dotenv()

    env = os.environ.get("FLASK_CONFIG", "development")

    read_toml_config(app, "base.toml")
    if env == "development":
        read_toml_config(app, "development.toml")
    else:
        read_toml_config(app, "production.toml")

    read_toml_config(app, "secrets.toml")


def read_toml_config(app, filename):
    absolute_filename = os.path.join(os.getcwd(), "config", filename)
    if os.path.exists(absolute_filename):
        app.config.from_file(absolute_filename, load=toml.load)


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


MAIN = Blueprint("main", __name__, url_prefix="")


@MAIN.route("/")
def home():
    """
    Home page. Actually there is no home page, so we redirect to the most
    appropriate place.
    """
    return redirect(url_for("social.home"))


def login_required() -> Response | None:
    """
    Before request handler to ensure login is required on any view
    """
    if current_app.config.get("NO_LOGIN"):
        return None

    if request.path.startswith(current_app.static_url_path):
        return None

    if request.url_rule and request.url_rule.endpoint == "geodata.static":
        # geodata blueprint assets
        return None

    if request.blueprint in ("login", "first_login", "projects", "notifications"):
        return None

    if request.blueprint == "_debug_toolbar" and current_app.debug:
        return None

    if not current_user.is_authenticated:
        return redirect(url_for("login.login_form", next=request.url))

    return None


def on_home_blueprint(endpoint, values):
    """
    url_value_preprocessor attached to blueprint used for 'home'
    """
    if endpoint == HOME_ACTION.endpoint.name:
        g.nav["active"] = HOME_ACTION.path
