"""Folders / Documents module."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from abilian.sbe.app import Application


def register_plugin(app: Application) -> None:
    from . import lock, signals
    from .cli import antivirus
    from .models import setup_listener
    from .views import community_blueprint

    app.register_blueprint(community_blueprint)
    setup_listener()

    # set default lock lifetime
    app.config.setdefault("SBE_LOCK_LIFETIME", lock.DEFAULT_LIFETIME)

    app.cli.add_command(antivirus)
