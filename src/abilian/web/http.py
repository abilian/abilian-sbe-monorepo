# Copyright (c) 2012-2024, Abilian SAS

"""View decorators for controlling some aspect of HTTP, mainly: Cache
headers."""

from __future__ import annotations

from functools import wraps

from flask import make_response


def nocache(view):
    @wraps(view)
    def _nocache(*args, **kwargs):
        resp = make_response(view(*args, **kwargs))
        resp.headers["Cache-Control"] = "no-cache"
        return resp

    return _nocache
