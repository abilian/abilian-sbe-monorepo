"""Register extensions as a plugin.

NOTE: panels are currently loaded and registered manually. This may change
in the future.
"""

from __future__ import annotations

from flask import Flask


def register_plugin(app: Flask) -> None:
    from .main import blueprint

    app.register_blueprint(blueprint)
