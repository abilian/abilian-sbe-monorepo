"""Logger started as a daemon (by ServerCmd).

main function: log_server
"""
from __future__ import annotations
import sys
from os import chdir, nice
from pathlib import Path

import zmq
from loguru import logger

from ..basic_server.utils import write_pid
from ..basic_server.wrapper import ServerWrapper
from .config import LOG_CONF


def log_receiver() -> None:
    write_pid(LOG_CONF["pid"])
    nice(10)
    log_file = Path(LOG_CONF["file"])
    folder = log_file.parent
    if not folder.is_dir():
        folder.mkdir(mode=0o755, parents=True)
    chdir(folder)

    socket = zmq.Context().socket(zmq.SUB)
    socket.bind(f"tcp://127.0.0.1:{LOG_CONF['port']}")
    socket.subscribe("")

    # socket.bind(f"tcp://127.0.0.1:{conf.log.port}")
    # socket.subscribe("")
    my_format = "{message}"
    logger.remove()
    logger.configure(
        handlers=[
            {
                "sink": log_file,
                "format": my_format,
                "rotation": LOG_CONF["size"],
                "retention": LOG_CONF["count"],
                "enqueue": True,
            }
        ]
    )

    while True:
        _, message = socket.recv_multipart()
        logger.info(message.decode("utf8").strip())


def log_server() -> None:
    try:
        cmd = sys.argv[1]
    except IndexError:
        cmd = "status"
    server = ServerWrapper(log_receiver, LOG_CONF["pid"])
    server.command(cmd)
