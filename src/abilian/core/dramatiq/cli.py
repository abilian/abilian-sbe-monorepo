from __future__ import annotations

import click
from flask.cli import with_appcontext

from .scheduler import run_scheduler

# from .tasks import check_maildir, process_email


@click.command()
@with_appcontext
def scheduler() -> None:
    run_scheduler()
