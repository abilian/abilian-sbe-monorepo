"""Create an application instance.

(wsgi script inside the package extranet, expecting no change in sys.path)
"""

from .app import create_app

app = create_app()
