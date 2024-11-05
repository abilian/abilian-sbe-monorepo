# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

from flask import Flask

from .extension import CommentExtension


def register_plugin(app: Flask):
    CommentExtension(app)
