"""Function to fork a function as an independant daemon."""

import os
from collections.abc import Callable
from contextlib import suppress
from time import asctime
from traceback import format_exc

ENV_VAR_TRACE_FILE = "APP_TRACE_FILE"
DEFAULT_TRACE_FILE = "/tmp/app_trace.txt"  # noqa: S108


def close_file_descriptors() -> None:
    """Close file descriptors to allow clean POSIX deamon fork."""
    try:
        maxfd = os.sysconf("SC_OPEN_MAX")
    except (AttributeError, ValueError):
        maxfd = 256  # default maximum
    for file_descriptor in range(maxfd):
        with suppress(OSError):
            os.close(file_descriptor)
    # Redirect the standard file descriptors to /dev/null.
    os.open("/dev/null", os.O_RDONLY)  # standard input (0)
    os.open("/dev/null", os.O_RDWR)  # standard output (1)
    os.open("/dev/null", os.O_RDWR)  # standard error (2)


def forker(function: Callable, *args) -> None:
    """Function to fork a function, does not wait on exit."""

    def second_child():
        try:
            close_file_descriptors()
            function(*args)
        except Exception:
            out = os.environ.get(ENV_VAR_TRACE_FILE, DEFAULT_TRACE_FILE)
            with open(out, "a+", encoding="utf8") as file:
                file.write("-" * 40)
                file.write("\n")
                file.write(format_exc(50))
                file.write(asctime())
                file.write("\n")
                file.write("-" * 40)
                file.write("\n")
        finally:
            os._exit(0)

    # first, let's fork
    pid1 = os.fork()
    if pid1 == 0:
        # we are child
        os.setsid()
        # second fork
        pid2 = os.fork()
        if pid2 == 0:
            second_child()
        else:
            # still 1st child
            with suppress(Exception):
                # do not block
                os.waitpid(pid2, os.WNOHANG)
            os._exit(0)
    else:
        # we are still there, continue our duty on
        with suppress(Exception):
            # do not block
            os.waitpid(pid1, 0)
        return
