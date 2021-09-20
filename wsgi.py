"""Create an application instance."""

# flake8: noqa

import sys

sys.path = ["src"] + sys.path


from extranet.app import create_app

app = create_app()
