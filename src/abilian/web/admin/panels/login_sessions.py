""""""

from __future__ import annotations

import contextlib

import pygeoip
from flask import render_template

from abilian.i18n import _
from abilian.services.auth.models import LoginSession
from abilian.web.admin import AdminPanel

DATA_FILES = ("/usr/share/GeoIP/GeoIP.dat", "/usr/share/GeoIP/GeoIPv6.dat")


class LoginSessionsPanel(AdminPanel):
    id = "login_sessions"
    label = "Session log"
    icon = "log-in"

    def get(self) -> str:
        geoips = []
        for filename in DATA_FILES:
            with contextlib.suppress(pygeoip.GeoIPError, OSError):
                geoips.append(pygeoip.GeoIP(filename))

        sessions = LoginSession.query.order_by(LoginSession.id.desc()).limit(50).all()
        unknown_country = _("Country unknown")

        def update_country(session):
            if session.ip_address:
                # if several IPs, only use last IP in the list, most likely the
                # public address
                ip_address = session.ip_address.rpartition(",")[-1]
                for geo_data in geoips:
                    try:
                        country = geo_data.country_name_by_addr(ip_address)
                    except Exception:  # noqa
                        continue

                    if country:
                        break
                else:
                    country = unknown_country

                session.country = country

        if geoips:
            for session in sessions:
                update_country(session)

        ctx = {"sessions": sessions}
        return render_template("admin/login_sessions.html", **ctx)
