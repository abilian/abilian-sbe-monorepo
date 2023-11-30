"""Some functions to start/stop a server daemon."""
from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from functools import cache
from os import getpid, kill
from pathlib import Path

from .forker import forker


@cache
def lock_dir() -> Path:
    for path in ("/run/lock", "/run", "/tmp", "/var/tmp"):  # noqa: S108
        if Path(path).is_dir():
            return Path(path)
    raise RuntimeError("No lock dir found")


def write_pid(pid_file: Path | str) -> int:
    pid = getpid()
    path = Path(pid_file)
    if not path.parent.exists():
        path.parent.mkdir(mode=0o755, exist_ok=True, parents=True)
    path.write_text(str(pid), encoding="utf8")
    return pid


def read_pid(pid_file: Path | str) -> int:
    pid = 0
    try:
        if Path(pid_file).exists():
            pid = int(Path(pid_file).read_text(encoding="utf8"))
    except (OSError, ValueError):
        pid = 0
    return pid


def is_running(pid_filename: Path | str) -> int:
    """Return the pid if running (or 0)."""
    pid_file = lock_dir() / pid_filename
    if not pid_file.exists():
        return 0
    running = 0
    daem_pid = read_pid(pid_file)
    if daem_pid:
        with suppress(OSError):
            kill(daem_pid, 0)
            running = daem_pid
    return running


def start(main_function: Callable, pid_filename: Path | str) -> None:
    name = main_function.__name__
    print(f"Starting daemon for '{name}'")
    running = is_running(pid_filename)
    if running:
        print("Already running with pid", running)
        raise SystemExit(0)
    print(f"Forking '{name}' process")
    forker(main_function)


def test(main_function: Callable, pid_filename: Path | str) -> None:
    name = main_function.__name__
    print(f"Starting test mode for '{name}'")
    running = is_running(pid_filename)
    if running:
        print("Already running with pid", running)
        raise SystemExit(0)
    print(f"Run in foreground '{name}' process")
    main_function()


def stop(pid_filename: Path | str) -> None:
    print(f"Stop daemon from pid file '{pid_filename}'")
    pid_file = lock_dir() / pid_filename
    pid = read_pid(pid_file)
    if not pid:
        print("No pid file: not running ?")
        return
    fail = False
    try:
        kill(pid, 15)
    except OSError:
        print("Fail of kill -15, will try kill -9")
        fail = True
    if fail:
        try:
            kill(pid, 9)
            fail = False
        except OSError:
            fail = True
    if fail:
        print("kill -9 failed !?")
    with suppress(OSError):
        pid_file.unlink()
    print("Stopped.")


def status(pid_filename: Path | str) -> None:
    running = is_running(pid_filename)
    if running:
        print("Running with pid", running)
    else:
        print("Not running")


def server(main_function: Callable, pid_filename: Path | str, cmd: str = "") -> None:
    if cmd == "stop":
        stop(pid_filename)
        raise SystemExit(0)
    if cmd == "restart":
        stop(pid_filename)
        start(main_function, pid_filename)
    elif cmd == "status":
        status(pid_filename)
    elif cmd == "test":
        stop(pid_filename)
        test(main_function, pid_filename)
    else:  # start
        start(main_function, pid_filename)
