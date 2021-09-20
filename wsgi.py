"""Create an application instance."""

import sys

sys.path = ["src"] + sys.path


from extranet.app import create_app

app = create_app()
