# Copyright (c) 2012-2024, Abilian SAS

"""Calendar module."""

from __future__ import annotations


def register_plugin(app) -> None:
    from .actions import register_actions
    from .views import blueprint

    blueprint.record_once(register_actions)
    app.register_blueprint(blueprint)
