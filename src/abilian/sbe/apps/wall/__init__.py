from __future__ import annotations

from flask import Flask


def register_plugin(app: Flask) -> None:
    from .views import wall

    app.register_blueprint(wall)
