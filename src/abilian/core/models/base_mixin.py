"""BaseMixin class."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm.util import class_mapper

from .base import IdMixin, TimestampedMixin
from .owned import OwnedMixin


class BaseMixin(IdMixin, TimestampedMixin, OwnedMixin):
    name: str

    def __init__(self):
        OwnedMixin.__init__(self)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"instance at 0x{id(self):x} name={self.name!r} id={self.id}>"
        )

    def __str__(self):
        return self.name or ""

    @property
    def column_names(self) -> list[str]:
        return [col.name for col in class_mapper(self.__class__).persist_selectable.c]

    def to_dict(self) -> dict[str, Any]:
        if hasattr(self, "__exportable__"):
            exported = self.__exportable__ + ["id"]
        else:
            exported = self.column_names
        result: dict[str, Any] = {}
        for key in exported:
            value = getattr(self, key)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[key] = value
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def _icon(self, size: int = 12) -> str:
        class_name = self.__class__.__name__.lower()
        return f"/static/icons/{class_name}-{size}.png"

    # FIXME: we can do better than that
    @property
    def _name(self):
        if hasattr(self, "title"):
            return self.title
        elif hasattr(self, "name"):
            return self.name
        else:
            raise NotImplementedError
