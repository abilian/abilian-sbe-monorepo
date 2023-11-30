"""ServerWrapper class to manage a function as a server."""
from __future__ import annotations

import types
from collections.abc import Callable
from contextlib import suppress
from os import kill
from pathlib import Path
from time import sleep

from .forker import forker
from .utils import read_pid


class ServerWrapper:
    """Class to manage a function as a server."""

    def __init__(self, function: Callable, pid_file: Path | str):
        assert isinstance("pid_file", (str, Path))
        assert isinstance(function, Callable)
        self.pid_file = Path(pid_file)
        self.main_function = function
        self.name = function.__name__
        folder = self.pid_file.parent
        if not folder.is_dir():
            folder.mkdir(mode=0o755, parents=True)

    def is_running(self) -> int:
        if not self.pid_file.exists():
            return 0
        running = 0
        daem_pid = read_pid(self.pid_file)
        if daem_pid:
            with suppress(OSError):
                kill(daem_pid, 0)
                running = daem_pid
        return running

    def start(self) -> None:
        print(f"Starting daemon for '{self.name}'")
        running = self.is_running()
        if running:
            print("Already running with pid", running)
            raise SystemExit(0)
        print(f"Forking '{self.name}' process")
        forker(self.main_function)

    def test(self) -> None:
        print(f"Starting test mode for '{self.name}'")
        running = self.is_running()
        if running:
            print("Already running with pid", running)
            raise SystemExit(0)
        print(f"Run in foreground '{self.name}' process")
        self.main_function()

    def stop(self) -> None:
        print(f"Stop daemon from pid file '{self.pid_file.name}'")
        pid = read_pid(self.pid_file)
        if not pid:
            print("No pid file: not running ?")
            return
        running = self.is_running()
        if not running:
            print("Not running, removing old lock if needed")
            with suppress(OSError):
                self.pid_file.unlink()
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
            self.pid_file.unlink()
        print("Stopped.")

    def status(self) -> None:
        running = self.is_running()
        if running:
            print("Running with pid", running)
        else:
            print("Not running")

    def command(self, cmd="") -> None:
        if cmd == "stop":
            self.stop()
            raise SystemExit(0)
        if cmd == "restart":
            self.stop()
            sleep(0.5)
            self.start()
        elif cmd == "status":
            self.status()
        elif cmd == "test":
            self.stop()
            sleep(0.5)
            self.test()
        else:  # start
            self.start()
