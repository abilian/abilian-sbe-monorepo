"""Create an application instance."""

# flake8: noqa

# Fiddle with the Python path for cloud platforms that don't support Poetry
import sys

sys.path = ["src"] + sys.path

# Temps monkey patches
import werkzeug.datastructures
import werkzeug.urls

werkzeug.url_encode = werkzeug.urls.url_encode
werkzeug.FileStorage = werkzeug.datastructures.FileStorage

# Normal bootstrap
from extranet.app import create_app

app = create_app()
