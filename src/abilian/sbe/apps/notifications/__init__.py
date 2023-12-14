"""Notifications."""

from __future__ import annotations

from abilian.sbe.app import Application

# Constants
TOKEN_SERIALIZER_NAME = "unsubscribe_sbe"  # noqa: S105


def register_plugin(app: Application) -> None:
    cfg = app.config.setdefault("ABILIAN_SBE", {})
    cfg.setdefault("DAILY_SOCIAL_DIGEST_SUBJECT", "Des nouvelles de vos communautés")

    # TODO: Slightly confusing. Reorg?
    # from .tasks.social import DEFAULT_DIGEST_SCHEDULE, DIGEST_TASK_NAME
    from .views import notifications, social

    # CELERYBEAT_SCHEDULE = app.config.setdefault("CELERYBEAT_SCHEDULE", {})
    # if DIGEST_TASK_NAME not in CELERYBEAT_SCHEDULE:
    #     CELERYBEAT_SCHEDULE[DIGEST_TASK_NAME] = DEFAULT_DIGEST_SCHEDULE

    app.register_blueprint(notifications)
