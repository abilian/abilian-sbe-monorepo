# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from flask import Blueprint

notifications = Blueprint(
    "notifications",
    __name__,
    url_prefix="/notifications",
    template_folder="../templates",
)
