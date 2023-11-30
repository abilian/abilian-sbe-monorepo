"""Client logging."""

import zmq
from zmq.log.handlers import PUBHandler

from .config import LOG_CONF


def connect_logger(logger: object, prefix: str = ""):
    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.connect(f"tcp://127.0.0.1:{LOG_CONF['port']}")
    handler = PUBHandler(pub)
    logger.remove()
    if prefix:
        base = (
            "{time:YY-MM-DD HH:mm:ss.SSS} - "
            "{level:<6.6} - __prefix__ - {name} - {message}"
        )
        logformat = base.replace("__prefix__", prefix)
    else:
        logformat = "{time:YY-MM-DD HH:mm:ss.SSS} - {level:<6.6} - {name} - {message}"
    logger.add(handler, format=logformat)
