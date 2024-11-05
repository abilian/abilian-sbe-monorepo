# Copyright (c) 2012-2024, Abilian SAS

"""Create all standard extensions."""

# Note: Because of issues with circular dependencies, Abilian-specific
# extensions are created later.
from __future__ import annotations

from . import upstream_info
from .csrf import abilian_csrf, wtf_csrf as csrf
from .jinjaext import DeferredJS
from .login import login_manager
from .mail import mail
from .redis import Redis
from .sqlalchemy import db

__all__ = (
    "csrf",
    "db",
    "login_manager",
    "mail",
    "redis",
    "upstream_info",
)

redis = Redis()

deferred_js = DeferredJS()
