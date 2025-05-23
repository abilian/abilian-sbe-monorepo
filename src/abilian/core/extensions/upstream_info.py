# Copyright (c) 2012-2024, Abilian SAS

"""Extension for sending information to upstream server."""

from __future__ import annotations

import typing
from typing import Any

from flask.globals import request_ctx
from flask.signals import request_finished, request_started

from abilian.core.signals import user_loaded

if typing.TYPE_CHECKING:
    from flask import Flask
    from flask.wrappers import Response

    from abilian.core.models.subjects import User


class UpstreamInfo:
    """Extension for sending information to upstream server."""

    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        app.extensions["upstream"] = self

        request_started.connect(self.request_started, sender=app)
        request_finished.connect(self.request_finished, sender=app)
        user_loaded.connect(self.user_loaded, sender=app)

        config = app.config
        config.setdefault("ABILIAN_UPSTREAM_INFO_ENABLED", False)
        for key in ("ABILIAN_UPSTREAM_INFO_DISCARD", "ABILIAN_UPSTREAM_INFO_INCLUDE"):
            val = config.get(key, ())
            if val is not None:
                val = frozenset(val)
            config[key] = val

    def request_started(self, app: Flask) -> None:
        request_ctx.upstream_info = {"Username": "Anonymous"}

    def request_finished(self, app: Flask, response: Response) -> None:
        info = request_ctx.upstream_info
        config = app.config
        default_enabled = bool(config["ABILIAN_UPSTREAM_INFO_ENABLED"])
        disabled = config["ABILIAN_UPSTREAM_INFO_DISCARD"]
        enabled = config["ABILIAN_UPSTREAM_INFO_INCLUDE"]

        for key, val in info.items():
            if (default_enabled and key in disabled) or (
                not default_enabled and key not in enabled
            ):
                continue

            header = f"X-{key}"
            response.headers[header] = val

    def user_loaded(self, app: Flask, user: User, *args: Any, **kwargs: Any) -> None:
        request_ctx.upstream_info["Username"] = user.email


extension = UpstreamInfo()
