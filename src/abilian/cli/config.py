""""""
from __future__ import annotations

from flask import current_app
from flask.cli import AppGroup
from loguru import logger

config_commands = AppGroup("config")


@config_commands.command()
def show(only_path=False):
    """Show the current config."""
    infos = ["\n", f'Instance path: "{current_app.instance_path}"']

    logger.info("\n  ".join(infos))
