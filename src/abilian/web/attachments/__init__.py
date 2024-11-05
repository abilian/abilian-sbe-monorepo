# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import TYPE_CHECKING

from .extension import AttachmentExtension, AttachmentsManager
from .forms import AttachmentForm

if TYPE_CHECKING:
    from flask import Flask


def register_plugin(app: Flask):
    AttachmentExtension(app)
