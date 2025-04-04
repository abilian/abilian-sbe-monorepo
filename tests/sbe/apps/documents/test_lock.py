# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from flask_login import login_user
from pytz import UTC

from abilian.core.models.subjects import User
from abilian.sbe.apps.documents import lock
from abilian.sbe.apps.documents.lock import Lock
from tests.util import redis_available

if TYPE_CHECKING:
    from flask import Flask
    from sqlalchemy.orm import Session


def test_lock() -> None:
    date = datetime(2015, 10, 22, 14, 58, 42, tzinfo=UTC)
    l = Lock(user_id=3, user="Joe Smith", date=date)
    d = l.as_dict()
    assert d == {"user_id": 3, "user": "Joe Smith", "date": "2015-10-22T14:58:42+00:00"}

    l = Lock.from_dict(d)
    assert l.user_id == 3
    assert l.user == "Joe Smith"
    assert l.date == date


@pytest.mark.skipif(not redis_available(), reason="requires redis connection")
def test_lock2(app: Flask, session: Session) -> None:
    user = User(
        email="test@example.com", first_name="Joe", last_name="Smith", can_login=True
    )
    other = User(email="other@example.com")
    session.add(user)
    session.add(other)
    session.commit()

    # set 30s lifetime
    app.config["SBE_LOCK_LIFETIME"] = 30
    dt_patcher = mock.patch.object(lock, "utcnow", mock.Mock(wraps=lock.utcnow))
    with dt_patcher as mocked:
        created_at = datetime(2015, 10, 22, 14, 58, 42, tzinfo=UTC)
        mocked.return_value = created_at

        login_user(user)
        lock_ = Lock.new()
        assert lock_.user_id == user.id
        assert lock_.user == "Joe Smith"
        assert lock_.date == created_at
        assert lock_.is_owner()
        assert lock_.is_owner(user)
        assert not lock_.is_owner(other)

        assert lock_.lifetime == 30
        mocked.return_value = created_at + timedelta(seconds=40)
        assert lock_.expired

        mocked.return_value = created_at + timedelta(seconds=20)
        assert not lock_.expired

        login_user(other)
        assert not lock_.is_owner()
