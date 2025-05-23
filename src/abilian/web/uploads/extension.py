# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid1

from flask import current_app
from loguru import logger

from abilian.core import signals
from abilian.core.dramatiq.scheduler import crontab
from abilian.core.dramatiq.singleton import dramatiq
from abilian.web import url_for

from .views import ac_blueprint

if TYPE_CHECKING:
    from io import BufferedReader
    from pathlib import Path

    from abilian.app import Application
    from abilian.core.models.subjects import User

CHUNK_SIZE = 64 * 1024

DEFAULT_CONFIG = {
    "USER_QUOTA": 100 * 1024**2,  # max 100 Mb for all current files
    "USER_MAX_FILES": 1000,  # max number of files per user
    "DELETE_STALLED_AFTER": 60 * 60 * 24,  # delete files remaining after 1 day
}

# CLEANUP_SCHEDULE_ID = f"{__name__}.periodic_clean_upload_directory"
# DEFAULT_CLEANUP_SCHEDULE = {"task": CLEANUP_SCHEDULE_ID, "schedule": timedelta(hours=1)}


def is_valid_handle(handle: str) -> bool:
    try:
        UUID(handle)
    except ValueError:
        return False

    return True


class FileUploadsExtension:
    """API for Out-Of-Band file uploads.

    Allow to manage files in forms: file is uploaded to an upload url, a handle is
    returned will be used in the form to refer to this uploaded filed.

    If the form fails to validate the uploaded file is not lost.

    A periodic task cleans the temporary repository.
    """

    def __init__(self, app: Application) -> None:
        app.register_blueprint(ac_blueprint)

        app.extensions["uploads"] = self
        app.add_template_global(self, "uploads")
        signals.register_js_api.connect(self._do_register_js_api)

        self.config: dict[str, Any] = {}
        self.config.update(DEFAULT_CONFIG)
        self.config.update(app.config.get("FILE_UPLOADS", {}))
        app.config["FILE_UPLOADS"] = self.config

        path = self.UPLOAD_DIR = app.data_dir / "uploads"
        path.mkdir(mode=0o775, parents=True, exist_ok=True)
        path.resolve()

    def _do_register_js_api(self, sender: Application) -> None:
        app = sender
        js_api = app.js_api.setdefault("upload", {})
        js_api["newFileUrl"] = url_for("uploads.new_file")

    def user_dir(self, user: User) -> Path:
        if user.is_anonymous:
            user_id = "anonymous"
        else:
            user_id = str(user.id)
        return self.UPLOAD_DIR / user_id

    def add_file(self, user: User, file_obj: BufferedReader, **metadata) -> str:
        """Add a new file.

        :returns: file handle
        """
        user_dir = self.user_dir(user)
        if not user_dir.exists():
            user_dir.mkdir(mode=0o775)

        handle = str(uuid1())
        file_path = user_dir / handle

        with file_path.open("wb") as out:
            for chunk in iter(lambda: file_obj.read(CHUNK_SIZE), b""):
                out.write(chunk)

        if metadata:
            meta_file = user_dir / f"{handle}.metadata"
            with meta_file.open("wb") as out:
                metadata_json = json.dumps(metadata, skipkeys=True).encode("ascii")
                out.write(metadata_json)

        return handle

    def get_file(self, user: User, handle: str) -> Path | None:
        """Retrieve a file for a user.

        :returns: a :class:`pathlib.Path` instance to this file,
            or None if no file can be found for this handle.
        """
        user_dir = self.user_dir(user)
        if not user_dir.exists():
            return None

        if not is_valid_handle(handle):
            return None

        file_path = user_dir / handle

        if not file_path.exists() and not file_path.is_file():
            return None

        return file_path

    def get_metadata_file(self, user: User, handle: str) -> Path | None:
        content = self.get_file(user, handle)
        if content is None:
            return None

        metafile = content.parent / f"{handle}.metadata"
        if not metafile.exists():
            return None

        return metafile

    def get_metadata(self, user: User, handle: str) -> dict[str, str]:
        metafile = self.get_metadata_file(user, handle)
        if metafile is None:
            return {}

        try:
            with metafile.open("rb") as in_:
                meta = json.load(in_)
        except Exception:
            meta = {}

        return meta

    def remove_file(self, user, handle) -> None:
        paths = (self.get_file(user, handle), self.get_metadata_file(user, handle))

        for file_path in paths:
            if file_path is not None:
                try:
                    file_path.unlink()
                except Exception:
                    logger.error("Error during remove file")

    def clear_stalled_files(self) -> None:
        """Scan upload directory and delete stalled files.

        Stalled files are files uploaded more than
        `DELETE_STALLED_AFTER` seconds ago.
        """
        CLEAR_AFTER = self.config["DELETE_STALLED_AFTER"]
        minimum_age = time.time() - CLEAR_AFTER

        for user_dir in self.UPLOAD_DIR.iterdir():
            if not user_dir.is_dir():
                logger.error(
                    "Found non-directory in upload dir: {user_dir}",
                    user_dir=repr(user_dir),
                )
                continue

            for content in user_dir.iterdir():
                if not content.is_file():
                    logger.error(
                        "Found non-file in user upload dir: {content}",
                        content=repr(content),
                    )
                    continue

                if content.stat().st_ctime < minimum_age:
                    content.unlink()


# Task scheduled to run every hour:
# make it expire after 50min (at invocation) : not necessary with apscheduler:
# "By default, only one instance of each job is allowed to be run at the same
# time. This means that if the job is about to be run but the previous run
# hasnt finished yet, then the latest run is considered a misfire."
@crontab("PERIODIC_CLEAN_UPLOAD_DIRECTORY")
@dramatiq.actor()
def periodic_clean_upload_directory() -> None:
    """This task should be run periodically.

    Default config sets up schedule using
    :data:`DEFAULT_CLEANUP_SCHEDULE`. `CELERYBEAT_SCHEDULE` key is
    :data:`CLEANUP_SCHEDULE_ID`.
    """
    logger.debug("Running job: periodic_clean_upload_directory")
    with current_app.test_request_context("/tasks/periodic_clean_upload_directory"):
        uploads = current_app.extensions["uploads"]
        uploads.clear_stalled_files()
