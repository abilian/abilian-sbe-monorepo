""""""
from __future__ import annotations

import io
import logging
import os
from pathlib import Path
import re

from abilian.core.models.blob import Blob

from ..base import Service

logger = logging.getLogger(__name__)

try:
    from clamd import ClamdError, ClamdUnixSocket

    found_clamd = True
except ImportError:
    found_clamd = False

DEBUG = True
CLAMD_CONF = {}
CLAMD_CONF_DEFAULT = {
    "StreamMaxLength": 26214400,
    "MaxFileSize": 26214400,
    "LocalSocket": "/run/clamav/clamd.sock",
}


def _size_to_int(size_str):
    multiplier = 0
    if not size_str:
        return 0

    unit = size_str[-1].lower()
    if unit in ("k", "m"):
        size_str = size_str[:-1]
        multiplier = 1024
        if unit == "m":
            multiplier *= 1024

    if not size_str:
        return 0

    size = int(size_str)
    if multiplier:
        size *= multiplier

    return size


def _update_clamd_conf():
    """Parse clamd.conf file from ENV[CLAMD_CONF_PATH] or use
    defaults if not found."""
    if not found_clamd:
        return
    conf_path = Path(os.environ.get("CLAMD_CONF_PATH") or "/etc/clamav/clamd.conf")
    if DEBUG:
        logger.warning(
            f"AntiVirusService: CLAMD_CONF_PATH {os.environ.get('CLAMD_CONF_PATH')}"
        )
        logger.warning(f"AntiVirusService: {conf_path=}")
    if not conf_path.exists():
        return
    conf_lines = [line.strip() for line in conf_path.open("rt").readlines()]
    conf_lines = [line for line in conf_lines if line and not line.startswith("#")]
    parsed_config = dict(re.split(r"\s+", line, 1) for line in conf_lines)
    for key in ("StreamMaxLength", "MaxFileSize"):
        if key not in parsed_config:
            continue
        parsed_config[key] = _size_to_int(parsed_config[key])
    CLAMD_CONF.update(parsed_config)
    if DEBUG:
        logger.warning(f"AntiVirusService: updated {CLAMD_CONF=}")


class AntiVirusService(Service):
    """Antivirus service."""

    name = "antivirus"

    def scan(self, file_or_stream):
        """
        :param file_or_stream: :class:`Blob` instance, filename or file object

        :returns: True if file is 'clean', False if a virus is detected, None if
        file could not be scanned.

        If `file_or_stream` is a Blob, scan result is stored in
        Blob.meta['antivirus'].
        """
        if DEBUG:
            self.logger.warning(f"AntiVirusService: {found_clamd=}")
            self.logger.warning(f"AntiVirusService: {CLAMD_CONF=}")
        if not found_clamd:
            return None

        if not CLAMD_CONF:
            _update_clamd_conf()

        config = CLAMD_CONF_DEFAULT | CLAMD_CONF

        res = self._scan(file_or_stream, config)
        if isinstance(file_or_stream, Blob):
            file_or_stream.meta["antivirus"] = res
        return res

    def _scan(self, file_or_stream, config):
        content = file_or_stream

        if isinstance(file_or_stream, Blob):
            # py3 compat: bytes == py2 str(). Pathlib uses os.fsencode()
            file_or_stream = bytes(file_or_stream.file)
        elif isinstance(file_or_stream, str):
            file_or_stream = file_or_stream.encode(os.fsencode)

        if isinstance(file_or_stream, bytes):
            content = open(file_or_stream, "rb")

        if content.seekable():
            max_size = config["StreamMaxLength"]
            pos = content.tell()
            content.seek(0, io.SEEK_END)
            size = content.tell()
            content.seek(pos)

            if size > max_size:
                logger.error(
                    f"Content size exceed antivirus size limit, size={size}, limit={max_size}",
                    extra={"stack": True},
                )
                return None

        # use stream scan. When using scan by filename, clamd runnnig user must have
        # access to file, which we cannot guarantee
        socket_file = config["LocalSocket"]
        if DEBUG:
            self.logger.warning(f"AntiVirusService: {config=}")
            self.logger.warning(f"AntiVirusService: {socket_file=}")
            self.logger.warning(
                f"AntiVirusService: socket file exists: {Path(socket_file).exists()}"
            )
        scan_socket = ClamdUnixSocket(socket_file, timeout=60)
        scan = scan_socket.instream
        try:
            res = scan(content)
        except ClamdError as e:
            self.logger.warning("Error during content scan: %s", repr(e))
            return None

        if "stream" not in res:
            # may happen if file doesn't exists
            return False

        res = res["stream"]
        return res[0] == "OK"


service = AntiVirusService()
