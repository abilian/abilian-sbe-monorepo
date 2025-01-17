# Copyright (c) 2012-2024, Abilian SAS

"""Lightweight integration and denormalisation using events (signals)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from blinker import ANY

from abilian.core.signals import activity
from abilian.sbe.apps.documents.models import Document

from .models import Community

if TYPE_CHECKING:
    from abilian.core.entities import Entity
    from abilian.core.models.subjects import User


@activity.connect_via(ANY)
def update_community(
    sender: Any, verb: str, actor: User, object: Entity, target: Entity | None = None
) -> None:
    if isinstance(object, Community):
        object.touch()
        return

    if isinstance(target, Community):
        community = target
        community.touch()

        if isinstance(object, Document):
            if verb == "post":
                community.document_count += 1
            elif verb == "delete":
                community.document_count -= 1
