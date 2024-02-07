from __future__ import annotations


class ConversionError(Exception):
    pass


class HandlerNotFoundError(ConversionError):
    pass
