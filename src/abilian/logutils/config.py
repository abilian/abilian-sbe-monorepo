"""Fixme: hardcoded config for tests.
"""

LOG_CONF = {
    "pid": "/tmp/app_log_daemon.pid",  # noqa S108
    "port": 25023,
    "file": "/var/tmp/sbe/sbe.log",  # noqa S108
    "size": 2_000_000,  # about 2 MB
    "count": 32,
}
