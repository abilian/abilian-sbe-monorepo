from __future__ import annotations

import dramatiq
import logging

from .lazy_actor import LazyActor

logger = logging.getLogger(__package__)

_actor_registry = set()


def job():
    def decorator(func):
        logger.debug("Registering cron job: {}", func.__name__)
        actor = LazyActor(func)
        _actor_registry.add(actor)
        return actor

    return decorator


def register_regular_jobs():
    logger.info("Registering regular jobs on Dramatiq")

    for actor in _actor_registry:
        logger.info("Registering cron job: {}", actor)
        broker = dramatiq.get_broker()
        actor.register(broker)
