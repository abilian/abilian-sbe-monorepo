"""Register extensions as a plugin.

NOTE: panels are currently loaded and registered manually. This may change
in the future.
"""

from __future__ import annotations

from abilian.sbe.app import Application


def register_plugin(app: Application) -> None:
    from .main import blueprint

    app.register_blueprint(blueprint)
