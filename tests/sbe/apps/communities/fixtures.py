from __future__ import annotations

from pytest import fixture

from abilian.core.models.subjects import User
from abilian.core.sqlalchemy import SQLAlchemy
from abilian.sbe.apps.communities.models import READER, Community
