"""Create an application instance.

(wsgi script inside the package extranet, expecting no change in sys.path)
"""

# flake8: noqa

# Fiddle with the Python path for cloud platforms that don't support Poetry
import sys

# Temps monkey patches
import werkzeug.datastructures
import werkzeug.urls

werkzeug.url_encode = werkzeug.urls.url_encode
werkzeug.FileStorage = werkzeug.datastructures.FileStorage

# Debugging
import icecream

icecream.install()

# Normal bootstrap
from flask.cli import load_dotenv

from .app import create_app

load_dotenv()

app = create_app()
