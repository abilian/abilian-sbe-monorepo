"""Create an application instance."""

# flake8: noqa

# Fiddle with the Python path for cloud platforms that don't support Poetry
import sys

sys.path = ["src"] + sys.path

# Temps monkey patches
import werkzeug.datastructures
import werkzeug.urls

werkzeug.FileStorage = werkzeug.datastructures.FileStorage

# Normal bootstrap
from flask.cli import load_dotenv

from extranet.app import create_app

load_dotenv()

app = create_app()
