# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations


class ConversionError(Exception):
    pass


class HandlerNotFoundError(ConversionError):
    pass
