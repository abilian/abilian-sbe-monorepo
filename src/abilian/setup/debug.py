# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from flask import Blueprint, Flask, abort
from loguru import logger

from abilian.core import extensions


def setup_debug(app: Flask) -> None:
    init_debug_toolbar(app)
    init_debug_pages(app)


def init_debug_toolbar(app: Flask) -> None:
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


def init_debug_pages(app: Flask) -> None:
    # dev helper
    # during dev, one can go to /http_error/403 to see rendering of 403
    http_error_pages = Blueprint("http_error_pages", __name__)

    @http_error_pages.route("/<int:code>")
    def error_page(code) -> None:
        """Helper for development to show 403, 404, 500..."""
        abort(code)

    app.register_blueprint(http_error_pages, url_prefix="/http_error")
