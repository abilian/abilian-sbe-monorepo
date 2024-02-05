"""Tag service.

Manages tags applied to taggable entities.

Cf. ATOM specs  (+ for instance this discussion:
  http://edward.oconnor.cx/2007/02/representing-tags-in-atom)
Cf. ICOM 3.6.12 (Tag) et 3.6.13 (TagApplication.

Warning: the Activity Steams spec has a notion of tagging, but it's slightly
different than what we are used to in content management:
"Indicates that the actor has associated the object with the target.
For example, if the actor specifies that a particular user appears in a photo.
The object is the user and the target is the photo."
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Unicode

from abilian.core.extensions import db
from abilian.core.models import IdMixin


class Tag(db.Model, IdMixin):
    """Persistent class representing a tag."""

    #: Unique, autogenerated id.
    id = Column(Integer, primary_key=True)

    #: The text associated to the tag
    term = Column(Unicode, nullable=False, unique=True)

    # Not sure we want the extra complexity, even though it's specified by Atom.
    # label = Column()

    # Also we might want: created_at, etc. Maybe a Tag should be an Entity?


class TagApplication(db.Model, IdMixin):
    """Persistent class representing a tag application on a taggable object."""

    #: Unique, autogenerated id.
    id = Column(Integer, primary_key=True)

    #: The actor that did the tagging.
    actor_id = Column(Integer, ForeignKey("user.id"))

    #: The entity (object) on which the tag has been applied.
    entity_id = Column(Integer)  # must point to a valid entity

    #: The time when the tag was applied.
    created_at = Column(DateTime, nullable=False)
