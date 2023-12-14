from __future__ import annotations

import click
from flask import current_app
from flask.cli import with_appcontext

from .scheduler import run_scheduler


@click.command()
@with_appcontext
def scheduler() -> None:
    config = dict(current_app.config)
    run_scheduler(config)
