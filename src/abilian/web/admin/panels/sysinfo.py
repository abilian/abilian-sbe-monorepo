from __future__ import annotations

import contextlib
import os
import sys
from importlib.metadata import PackageNotFoundError, distribution

with contextlib.suppress(ImportError):
    from importlib.metadata import packages_distributions

import collections
import contextlib
from operator import itemgetter

from flask import current_app, render_template

from abilian.web.admin import AdminPanel

SHORTLIST_PY39 = [
    "abilian-devtools",
    "abilian-sbe",
    "alembic",
    "APScheduler",
    "Babel",
    "click",
    "cryptography",
    "dramatiq",
    "Flask",
    "Flask-Assets",
    "Flask-Babel",
    "Flask-DebugToolbar",
    "flask-dramatiq",
    "Flask-LinkTester",
    "Flask-Login",
    "Flask-Mail",
    "Flask-Migrate",
    "Flask-SQLAlchemy",
    "flask-tailwind",
    "flask-talisman",
    "Flask-WTF",
    "Jinja2",
    "loguru",
    "lxml",
    "Mako",
    "MarkupSafe",
    "python",
    "SQLAlchemy",
    "Werkzeug",
]


def installed_packages() -> list[dict[str, str]]:
    packages: list[dict[str, str]] = []
    if sys.version_info >= (3, 10):
        packages_iterator = iter(packages_distributions())
    else:
        packages_iterator = SHORTLIST_PY39
    for key in packages_iterator:
        try:
            dist = distribution(key)
        except PackageNotFoundError:
            continue
        package = {
            "name": dist.name,
            "key": key,
            "vcs": "",
        }
        try:
            package["version"] = dist.version
        except Exception:
            package["version"] = "Unknown version"
        packages.append(package)
    return sorted(packages, key=itemgetter("key"))


class SysinfoPanel(AdminPanel):
    id = "sysinfo"
    label = "System information"
    icon = "hdd"

    def get(self) -> str:
        uname = os.popen("uname -a").read()
        python_version = sys.version.strip()

        packages = installed_packages()

        config_values = [(k, repr(v)) for k, v in sorted(current_app.config.items())]

        ctx = {
            "python_version": python_version,
            "packages": packages,
            "uname": uname,
            "config_values": config_values,
        }
        return render_template("admin/sysinfo.html", **ctx)
