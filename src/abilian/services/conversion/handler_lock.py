# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

import functools
from pathlib import Path
from typing import TYPE_CHECKING

from filelock import FileLock, Timeout

from .exceptions import ConversionError

if TYPE_CHECKING:
    from collections.abc import Callable

LOCK_EXPIRE = 1800  # 30 min, in case many request in //
LOCK_DIR = []
LOCK_FILES = {}


def init_conversion_lock_dir(instance_path: str) -> None:
    lock_dir = Path(instance_path) / "lock"
    lock_dir.mkdir(parents=True, exist_ok=True)
    LOCK_DIR.append(lock_dir)


def get_lock_file(name: str) -> FileLock:
    if lock := LOCK_FILES.get(name):
        return lock
    lock = FileLock(LOCK_DIR[0] / f"{name}.lock", timeout=LOCK_EXPIRE)
    LOCK_FILES[name] = lock
    return lock


def acquire_lock(name: str) -> Callable:
    """Ensure the decorated function is alone to run by using a lock file."""

    def locked(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock = get_lock_file(name)
            try:
                lock.acquire()
                return func(*args, **kwargs)
            except Timeout as e:
                raise ConversionError from e
            finally:
                lock.release()

        return wrapper

    return locked
