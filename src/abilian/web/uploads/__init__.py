# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

from typing import TYPE_CHECKING

from .extension import FileUploadsExtension

if TYPE_CHECKING:
    from abilian.app import Application


def register_plugin(app: Application):
    FileUploadsExtension(app)
