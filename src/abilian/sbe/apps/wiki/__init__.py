# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abilian.app import Application


def register_plugin(app: Application) -> None:
    from .actions import register_actions
    from .views import wiki

    # could also test on private attribute _got_registered_once
    if not any(
        fct for fct in wiki.deferred_functions if fct.__name__ == "register_actions"
    ):
        wiki.record_once(register_actions)
    app.register_blueprint(wiki)
