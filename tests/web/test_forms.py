# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from unittest import mock

import pytz
from wtforms import Form

from abilian.core.entities import Entity
from abilian.services.security import ANONYMOUS, OWNER, READ, WRITE, Role
from abilian.web.forms import FormPermissions, fields, filters

if TYPE_CHECKING:
    from abilian.app import Application

NNSP = "\u202f"  # narrow no-break space


def user_tz() -> str:
    # This one is GMT+8 and has no DST (tests should pass any time in year)
    return "Asia/Hong_Kong"


USER_TZ = pytz.timezone(user_tz())


# test filters
def test_strip() -> None:
    strip = filters.strip
    assert strip(None) == ""
    assert strip(4) == 4
    assert strip(" a string ") == "a string"
    assert strip(" voilà ") == "voilà"


def test_uppercase() -> None:
    uppercase = filters.uppercase
    assert uppercase(None) is None
    assert uppercase(4) == 4
    assert uppercase(" a string ") == " A STRING "
    assert uppercase(" Voilà ") == " VOILÀ "


def test_lowercase() -> None:
    lowercase = filters.lowercase
    assert lowercase(None) is None
    assert lowercase(4) == 4
    assert lowercase(" A STRING ") == " a string "
    assert lowercase(" VOILÀ ") == " voilà "


# FormPermissions
# @pytest.mark.skip(reason="Need to be updated")
def test_form_permissions_controller() -> None:
    security_mock = mock.Mock()
    has_role = security_mock.has_role = mock.Mock()
    has_role.return_value = True

    current_app_mock = mock.Mock()
    current_app_mock.services = {"security": security_mock}

    MarkRole = Role("tests:mark-role")
    _MARK = object()
    _ENTITY_MARK = Entity()

    with mock.patch("abilian.services.current_app", current_app_mock):
        # default role
        fp = FormPermissions()
        assert fp.has_permission(READ)
        assert fp.has_permission(READ, obj=_MARK)
        assert fp.has_permission(READ, obj=_ENTITY_MARK)

        # change default
        fp = FormPermissions(default=MarkRole)
        assert fp.has_permission(READ)
        assert fp.has_permission(READ, field="test")

        fp = FormPermissions(default=MarkRole, read=ANONYMOUS)
        assert fp.has_permission(READ)
        assert fp.has_permission(READ, field="test")
        assert fp.has_permission(WRITE)

        # field roles
        fp = FormPermissions(
            default=MarkRole, read=ANONYMOUS, fields_read={"test": {OWNER}}
        )
        assert fp.has_permission(READ)
        assert fp.has_permission(READ, field="test")
        assert fp.has_permission(READ, field="test")

        # dynamic roles
        dyn_roles = mock.Mock()
        dyn_roles.return_value = [MarkRole]
        fp = FormPermissions(read=dyn_roles)
        assert fp.has_permission(READ)
        assert dyn_roles.call_args == [{"permission": READ, "field": None, "obj": None}]

        dyn_roles.reset_mock()
        fp = FormPermissions(read=[OWNER, dyn_roles])
        assert fp.has_permission(READ)
        assert dyn_roles.call_args == [{"permission": READ, "field": None, "obj": None}]


def patch_babel(app: Application) -> None:
    app.extensions["babel"].timezone_selector_func = None
    app.extensions["babel"].timezoneselector(user_tz)


def test_datetime_field(app: Application) -> None:
    """Test fields supports date with year < 1900."""

    assert "fr" in app.config["BABEL_ACCEPT_LANGUAGES"]

    patch_babel(app)

    obj = mock.Mock()

    headers = {"Accept-Language": "fr-FR,fr;q=0.8"}
    with app.test_request_context(headers=headers):
        field = fields.DateTimeField(use_naive=False).bind(Form(), "dt")
        field.process_formdata(["17/06/1789 | 10:42"])
        # 1789: applied offset for HongKong is equal to LMT+7:37:00,
        # thus we compare with tzinfo=user_tz
        expected_datetime = datetime.datetime(1789, 6, 17, 10, 42, tzinfo=USER_TZ)
        assert field.data == expected_datetime
        # UTC stored
        assert field.data.tzinfo is pytz.UTC
        # displayed in user current timezone
        assert field._value() == "17/06/1789 10:42"

        # non-naive mode: test process_data change TZ to user's TZ
        field.process_data(field.data)
        assert field.data.tzinfo is USER_TZ
        assert field.data == expected_datetime

        field.populate_obj(obj, "dt")
        assert obj.dt == expected_datetime

        # test more recent date: offset is GMT+8
        field.process_formdata(["23/01/2011 | 10:42"])
        expected_datetime = datetime.datetime(2011, 1, 23, 2, 42, tzinfo=pytz.utc)
        assert field.data == expected_datetime


def test_datetime_field_naive(app: Application) -> None:
    """Test fields supports date with year < 1900."""
    patch_babel(app)

    obj = mock.Mock()

    headers = {"Accept-Language": "fr-FR,fr;q=0.8"}
    with app.test_request_context(headers=headers):
        # NAIVE mode: dates without timezone. Those are the problematic ones
        # when year < 1900: strptime will raise an Exception use naive dates; by
        # default
        field = fields.DateTimeField().bind(Form(), "dt")
        field.process_formdata(["17/06/1789 | 10:42"])

        # UTC stored
        assert field.data.tzinfo is pytz.UTC
        expected_datetime = datetime.datetime(1789, 6, 17, 10, 42, tzinfo=pytz.UTC)
        assert field.data == expected_datetime

        # naive stored
        field.populate_obj(obj, "dt")
        assert obj.dt == datetime.datetime(1789, 6, 17, 10, 42)


def test_datetime_field_force_4digit_year(app: Application) -> None:
    # use 'en': short date pattern is 'M/d/yy'
    patch_babel(app)

    headers = {"Accept-Language": "en"}
    with app.test_request_context(headers=headers):
        field = fields.DateTimeField().bind(Form(), "dt")
        field.data = datetime.datetime(2011, 1, 23, 10, 42, tzinfo=pytz.utc)
        assert field._value() == f"1/23/2011, 6:42{NNSP}PM"


def test_date_field(app: Application) -> None:
    """Test fields supports date with year < 1900."""
    patch_babel(app)

    headers = {"Accept-Language": "fr-FR,fr;q=0.8"}
    with app.test_request_context(headers=headers):
        field = fields.DateField().bind(Form(), "dt")
        field.process_formdata(["17/06/1789"])
        assert field.data == datetime.date(1789, 6, 17)
        assert field._value() == "17/06/1789"


def test_datefield_force_4digit_year(app: Application) -> None:
    patch_babel(app)

    # use 'en': short date pattern is 'M/d/yy'
    headers = {"Accept-Language": "en"}
    with app.test_request_context(headers=headers):
        field = fields.DateField().bind(Form(), "dt")
        field.data = datetime.date(2011, 1, 23)
        assert field._value() == "1/23/2011"
