from __future__ import annotations

from contextlib import suppress
from functools import lru_cache
from importlib import resources as rso

import maxminddb

GEOIP_DB_PATH = str(rso.files("abilian.web.admin.panels.geoip") / "ip_country.mmdb")
GEOIP_DB: list[maxminddb.Reader] = []


@lru_cache(maxsize=1024)
def ip_to_country_code(ip: str) -> str:
    """Return 2 letters country code from IP, or empty string if not found."""

    with suppress(OSError, ValueError):
        if not GEOIP_DB:
            GEOIP_DB.append(maxminddb.open_database(GEOIP_DB_PATH))
        result = GEOIP_DB[0].get(ip)
        if result:
            return result.get("country", "")
    return ""
