"""Communities module."""

from __future__ import annotations

from flask import Flask


def register_plugin(app: Flask) -> None:
    # Used for side effects
    from . import events, search
    from .views import communities

    app.register_blueprint(communities)

    search.init_app(app)
