"""Create an application instance."""

import os

os.environ["PYTHONPATH"] = "src"


from extranet.app import create_app

app = create_app()
