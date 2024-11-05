# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


def register_plugin(app: Flask) -> None:
    from .views import wall

    app.register_blueprint(wall)
