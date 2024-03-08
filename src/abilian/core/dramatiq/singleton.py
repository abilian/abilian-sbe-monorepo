"""Singleton for Dramatiq task manager, to permit lazy declaration of actors.
"""

from __future__ import annotations

from flask_dramatiq import Dramatiq

dramatiq = Dramatiq()

# Remove prmeteus from middleware list
# See:
# https://groups.io/g/dramatiq-users/topic/disabling_prometheus/80745532?p=
dramatiq.middleware = dramatiq.middleware[1:]
