"""Create an application instance."""

import os
import sys
import rich

env = {}
for k in sorted(os.environ):
    env[k] = os.environ[k]
rich.print(env)

rich.print("path=", sys.path)

sys.path = ["src"] + sys.path


from extranet.app import create_app

app = create_app()
