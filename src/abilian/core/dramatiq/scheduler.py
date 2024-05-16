from __future__ import annotations

from collections import namedtuple
from collections.abc import Callable

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

Job = namedtuple("Job", ["actor", "key"])

DEFAULT_SCHEDULE = {
    "SCHEDULE_SEND_DAILY_SOCIAL_DIGEST": "0 10 * * *",
    "PERIODIC_CLEAN_UPLOAD_DIRECTORY": "0 * * * *",
    "SCHEDULE_CHECK_MAILDIR": "* * * * *",
}

_actor_registry = set()


def crontab(crontab: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        logger.debug("Registering cron job: {func}", func=str(func))
        job = Job(actor=func, key=crontab)
        _actor_registry.add(job)
        return func

    return decorator


def crontab_from_config(config: dict, job: Job) -> str:
    key = job.key.upper()
    if key in config:
        # schedule value can be ""
        schedule = config[key].strip()
    else:
        schedule = DEFAULT_SCHEDULE.get(key, "")
    return schedule


def run_scheduler(config: dict) -> int:
    scheduler = BlockingScheduler()
    scheduler.remove_all_jobs()

    for job in _actor_registry:
        crontab_content = crontab_from_config(config, job)
        if not crontab_content:
            logger.warning(
                "Missing crontab, NOT registering cron job: {actor}",
                actor=str(job.actor),
            )
            continue
        logger.debug(
            "Registering cron job: {actor} {crontab}",
            actor=str(job.actor),
            crontab=crontab_content,
        )

        scheduler.add_job(
            job.actor.send,
            CronTrigger.from_crontab(crontab_content),
        )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

    return 0
