from __future__ import annotations

import pytest

from abilian.web.admin.panels.geoip.ip_country_code import ip_to_country_code


def test_empty_ip():
    with pytest.raises(TypeError):
        bad = ip_to_country_code()


def test_not_string_ip():
    with pytest.raises(TypeError):
        bad = ip_to_country_code(123)


def test_any_str1():
    assert ip_to_country_code("123.123.123.123.123") == ""


def test_fr():
    assert ip_to_country_code("212.27.48.10") == "FR"
    # lru cache:
    assert ip_to_country_code("212.27.48.10") == "FR"


def test_US():
    assert ip_to_country_code("104.85.45.20") == "US"
