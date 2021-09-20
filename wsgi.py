"""Create an application instance."""

import os

from extranet.app import create_app

os.environ["PYTHONPATH"] = "src"

app = create_app()
