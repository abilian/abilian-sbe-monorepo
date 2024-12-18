# Copyright (c) 2012-2024, Abilian SAS

"""Application settings service."""

from __future__ import annotations

from .models import register
from .service import SettingsService

__all__ = ["SettingsService", "register"]
