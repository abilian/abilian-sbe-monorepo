"""Singleton for Dramatiq task manager, to permit lazy declaration of actors.
"""

from flask_dramatiq import Dramatiq

dramatiq = Dramatiq()
