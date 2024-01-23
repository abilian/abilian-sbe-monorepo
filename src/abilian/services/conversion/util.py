from __future__ import annotations

import contextlib
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import mkstemp

# Hack for Mac OS + homebrew
os.environ["PATH"] += ":/usr/local/bin"
# Used on SlapOS
if os.environ.get("LIBREOFFICEPATH"):
    os.environ["PATH"] += ":" + os.environ["LIBREOFFICEPATH"]

TMP_DIR = "tmp"
CACHE_DIR = "cache"


def get_tmp_dir() -> Path:
    from . import converter

    return converter.tmp_dir


# Utils
@contextmanager
def make_temp_file(
    blob: bytes | None = None,
    prefix: str = "tmp",
    suffix: str = "",
    tmp_dir: Path | None = None,
) -> Iterator[str]:
    if tmp_dir is None:
        tmp_dir = get_tmp_dir()

    fd, filename = mkstemp(dir=str(tmp_dir), prefix=prefix, suffix=suffix)
    if blob is not None:
        io = os.fdopen(fd, "wb")
        io.write(blob)
        io.close()
    else:
        os.close(fd)

    yield filename

    with contextlib.suppress(OSError):
        os.remove(filename)
