from __future__ import annotations

import jinja2

from abilian.sbe.app import Application
from abilian.services.preferences import preferences

from .panels.sbe_notifications import SbeNotificationsPanel


def register_plugin(app: Application) -> None:
    loader = jinja2.PackageLoader("abilian.sbe.apps.preferences")
    app.register_jinja_loaders(loader)
    preferences.register_panel(SbeNotificationsPanel(), app)
