# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

from abilian.app import Application

from .extension import FileUploadsExtension


def register_plugin(app: Application):
    FileUploadsExtension(app)
