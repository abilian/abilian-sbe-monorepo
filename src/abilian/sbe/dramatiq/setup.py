from __future__ import annotations

from loguru import logger
from abilian.logutils.configure import connect_logger
import dramatiq
from dramatiq.brokers.redis import RedisBroker

# from .job import register_regular_jobs
from .middleware import AppContextMiddleware

connect_logger(logger)


# from .scheduler import register_cron_jobs

# use redis DB /1 for // execution with Celery:
DEFAULT_REDIS_URL = "redis://localhost:6379/1"


def init_dramatiq(app):
    redis_url = app.config.get("DRAMATIC_REDIS_URL")
    if not redis_url:
        redis_url = app.config.get("REDIS_URL")
    if not redis_url:
        redis_url = DEFAULT_REDIS_URL
    logger.info(f"Setting up Dramatiq, URL={redis_url}")
    middleware = [AppContextMiddleware(app)]
    broker = RedisBroker(url=redis_url, middleware=middleware)
    dramatiq.set_broker(broker)

    # register_cron_jobs()
    # register_regular_jobs()


# def setup_broker():
#     app = create_app()
#     init_dramatiq(app)
#     return dramatiq.get_broker()
