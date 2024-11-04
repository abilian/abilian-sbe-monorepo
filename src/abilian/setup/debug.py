from flask import Flask
from loguru import logger

from abilian.core import extensions


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
