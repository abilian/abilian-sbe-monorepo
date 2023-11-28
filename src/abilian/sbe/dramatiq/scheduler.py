from __future__ import annotations

import dramatiq
import logging

# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger

from .lazy_actor import LazyActor

logger = logging.getLogger(__package__)

_actor_registry = set()


def crontab(crontab: str):
    def decorator(func):
        logger.debug("Registering cron job: {}", func.__name__)
        actor = LazyActor(func, crontab=crontab)
        _actor_registry.add(actor)
        return actor

    return decorator


def register_cron_jobs():
    logger.info("Registering cron jobs on Dramatiq")

    for actor in _actor_registry:
        logger.info("Registering cron job: {}", actor)
        broker = dramatiq.get_broker()
        actor.register(broker)


def run_scheduler():
    logger.info("run_scheduler(): pass")
    return 0
