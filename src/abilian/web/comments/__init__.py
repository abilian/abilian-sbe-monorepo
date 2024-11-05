# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

from typing import TYPE_CHECKING

from .extension import CommentExtension

if TYPE_CHECKING:
    from flask import Flask


def register_plugin(app: Flask):
    CommentExtension(app)
