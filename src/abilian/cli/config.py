""""""

from __future__ import annotations

import os

import click
from flask import current_app
from flask.cli import with_appcontext


@click.command(short_help="Show config")
@with_appcontext
def config() -> None:
    config_ = dict(sorted(current_app.config.items()))
    print("CONFIG:\n")
    for k, v in config_.items():
        if not k[0].isupper():
            continue
        try:
            print(f"{k}: {v}")
        except Exception as e:
            print(f"{k}: {e}")

    print("\nENV:\n")

    env_ = dict(sorted(os.environ.items()))
    for k, v in env_.items():
        print(f"{k}: {v}")
