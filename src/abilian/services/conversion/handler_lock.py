import functools
import os
from collections.abc import Callable
from pathlib import Path

from filelock import FileLock, Timeout

from .exceptions import ConversionError

LOCK_EXPIRE = 1800  # 30 min, in case many request in //


@functools.cache
def _find_lock_directory() -> Path:
    lock_dir = Path(os.environ.get("INSTANCE_VAR_RUN", "/var/lock/sbe"))
    if not lock_dir.exists():
        lock_dir.mkdir(parents=True, exist_ok=True)
    return lock_dir


def acquire_lock(name: str) -> Callable:
    """Ensure the decorated function is alone to run by using a lock file."""
    lock = FileLock(_find_lock_directory() / f"{name}.lock", timeout=LOCK_EXPIRE)

    def locked(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                lock.acquire()
                return func(*args, **kwargs)
            except Timeout as e:
                raise ConversionError from e
            finally:
                lock.release()

        return wrapper

    return locked
