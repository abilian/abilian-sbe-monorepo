from __future__ import annotations

from collections import namedtuple

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

Job = namedtuple("Job", ["actor", "crontab"])
_actor_registry = set()


def crontab(crontab: str):
    def decorator(func):
        logger.debug(f"Registering cron job: {func}")
        job = Job(actor=func, crontab=crontab)
        _actor_registry.add(job)
        return func

    return decorator


def run_scheduler():
    scheduler = BlockingScheduler()

    for job in _actor_registry:
        logger.info(f"Registering cron job: {job}")

        scheduler.add_job(
            job.actor.send,
            CronTrigger.from_crontab(job.crontab),
        )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

    return 0
