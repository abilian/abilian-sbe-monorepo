# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from datetime import datetime

from sqlalchemy import TEXT, Column, DateTime
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Mapped, backref, relationship

from abilian.core.entities import SEARCHABLE, Entity
from abilian.sbe.apps.communities.models import (
    Community,
    CommunityIdColumn,
    community_content,
)


@community_content
class Event(Entity):
    __tablename__ = "sbe_event"

    community_id = CommunityIdColumn()

    #: The community this event belongs to
    community = relationship(
        Community,
        primaryjoin=(community_id == Community.id),
        backref=backref("events", cascade="all, delete-orphan"),
    )

    # title = Column(Unicode, nullable=False, default="", info=SEARCHABLE)
    title: Mapped[str] = Column(TEXT, nullable=False, default="", info=SEARCHABLE)

    description: Mapped[str] = Column(TEXT, nullable=False, default="", info=SEARCHABLE)

    location: Mapped[str] = Column(TEXT, nullable=False, default="", info=SEARCHABLE)

    start: Mapped[datetime] = Column(DateTime, nullable=False)
    end: Mapped[datetime] = Column(DateTime)

    url: Mapped[str] = Column(TEXT, nullable=False, default="")


@listens_for(Event.title, "set", active_history=True)
def _event_sync_name_title(entity, new_value, old_value, initiator):
    if entity.name != new_value:
        entity.name = new_value
    return new_value
