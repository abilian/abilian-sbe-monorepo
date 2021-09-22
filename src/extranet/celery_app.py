"""Create an application instance."""

# flake8: noqa

# Temps monkey patches
import werkzeug.datastructures
import werkzeug.urls

werkzeug.url_encode = werkzeug.urls.url_encode
werkzeug.FileStorage = werkzeug.datastructures.FileStorage

# Normal bootstrap
from flask.cli import load_dotenv

from abilian.core.celery import FlaskCelery as BaseCelery
from abilian.core.celery import FlaskLoader as CeleryBaseLoader

load_dotenv()


# loader to be used by celery workers
class CeleryLoader(CeleryBaseLoader):
    flask_app_factory = "extranet.app.create_app"


celery = BaseCelery(loader=CeleryLoader)

__all__ = (celery,)
