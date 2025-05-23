# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

import contextlib
import glob
import hashlib
import mimetypes
import os
import re
import shutil
import subprocess
import threading
import traceback
from abc import ABC, abstractmethod
from base64 import b64decode, b64encode
from pathlib import Path
from typing import TYPE_CHECKING, Any
from xmlrpc.client import ServerProxy

from loguru import logger
from magic import Magic

from abilian.services.image import resize

from .exceptions import ConversionError
from .handler_lock import acquire_lock
from .util import get_tmp_dir, make_temp_file

if TYPE_CHECKING:
    from flask import Flask


def poppler_bin_util(util: str) -> str:
    if "POPPLER_BIN" not in os.environ:
        return ""
    path = Path(os.environ["POPPLER_BIN"]) / util
    if path.is_file():
        return str(path)
    return ""


# Quick check for tests
def has_pdftotext() -> bool:
    if poppler_bin_util("pdftotext"):
        return True
    result = shutil.which("pdftotext") is not None
    if not result:
        logger.warning("has_pdftotext(): {result}", result=result)
        logger.warning("has_pdftotext() PATH: {path}", path=os.environ["PATH"])
    return result


def has_libreoffice() -> bool:
    result = shutil.which("soffice") is not None
    if not result:
        logger.warning("has_libreoffice(): {result}", result=result)
        logger.warning("has_libreoffice() PATH: {path}", path=os.environ["PATH"])
    return result


HAS_PDFTOTEXT = has_pdftotext()
HAS_LIBREOFFICE = has_libreoffice()


class Handler(ABC):
    """Abstract base class for handlers."""

    accepts_mime_types: list[str] = []
    produces_mime_types: list[str] = []

    def __init__(self, *args, **kwargs) -> None:
        self.log = logger

    def init_app(self, app: Flask) -> None:
        pass

    @property
    def tmp_dir(self) -> Path:
        return get_tmp_dir()

    @property
    def mime_sniffer(self):
        return Magic(mime=True)

    @property
    def encoding_sniffer(self) -> Magic:
        return Magic(mime_encoding=True)

    def accept(self, source_mime_type: str, target_mime_type: str) -> bool:
        """Generic matcher based on patterns."""

        match_source = False
        match_target = False

        for pat in self.accepts_mime_types:
            if re.match(f"^{pat}$", source_mime_type):
                match_source = True
                break

        for pat in self.produces_mime_types:
            if re.match(f"^{pat}$", target_mime_type):
                match_target = True
                break

        return match_source and match_target

    @abstractmethod
    def convert(self, blob: bytes, **kw):
        pass


class PdfToTextHandler(Handler):
    accepts_mime_types = ["application/pdf", "application/x-pdf"]
    produces_mime_types = ["text/plain"]

    @acquire_lock("PdfToTextHandler")
    def convert(self, blob: bytes, **kw: Any) -> str:
        with make_temp_file(blob) as in_fn, make_temp_file() as out_fn:
            pdftotext = poppler_bin_util("pdftotext") or "pdftotext"
            try:
                subprocess.check_call([pdftotext, in_fn, out_fn])
            except Exception as e:
                msg = "pdftotext failed"
                raise ConversionError(msg) from e

            converted = open(out_fn, "rb").read()
            try:
                encoding = self.encoding_sniffer.from_file(out_fn)
            except Exception:
                encoding = None

        if encoding in ("binary", None):
            encoding = "ascii"
        try:
            converted_unicode = str(converted, encoding, errors="ignore")
        except Exception:
            traceback.print_exc()
            converted_unicode = str(converted, errors="ignore")

        return converted_unicode


class AbiwordTextHandler(Handler):
    accepts_mime_types = ["application/msword"]
    produces_mime_types = ["text/plain"]

    def convert(self, blob: bytes, **kw):
        tmp_dir = self.tmp_dir
        with (
            make_temp_file(blob, suffix=".doc") as in_fn,
            make_temp_file(suffix=".txt") as out_fn,
        ):
            try:
                subprocess.check_call(
                    [
                        "abiword",
                        "--to",
                        os.path.basename(out_fn),
                        os.path.basename(in_fn),
                    ],
                    cwd=bytes(tmp_dir),
                )
            except Exception as e:
                msg = "abiword failed"
                raise ConversionError(msg) from e

            converted = open(out_fn, "rb").read()
            try:
                encoding = self.encoding_sniffer.from_file(out_fn)
            except Exception:
                encoding = None

        if encoding in ("binary", None):
            encoding = "ascii"
        try:
            converted_unicode = str(converted, encoding, errors="ignore")
        except Exception:
            traceback.print_exc()
            converted_unicode = str(converted, errors="ignore")

        return converted_unicode


class AbiwordPDFHandler(Handler):
    accepts_mime_types = [
        "application/msword",
        "application/vnd.oasis.opendocument.text",
        "text/rtf",
    ]
    produces_mime_types = ["application/pdf"]

    def convert(self, blob: bytes, **kw):
        with (
            make_temp_file(blob, suffix=".doc") as in_fn,
            make_temp_file(suffix=".pdf") as out_fn,
        ):
            try:
                subprocess.check_call(
                    [
                        "abiword",
                        "--to",
                        os.path.basename(out_fn),
                        os.path.basename(in_fn),
                    ],
                    cwd=bytes(self.tmp_dir),
                )
            except Exception as e:
                msg = "abiword failed"
                raise ConversionError(msg) from e

            converted = Path(out_fn).read_bytes()
            return converted


class ImageMagickHandler(Handler):
    accepts_mime_types = ["image/.*"]
    produces_mime_types = ["application/pdf"]

    @acquire_lock("ImageMagickHandler")
    def convert(self, blob: bytes, **kw) -> bytes:
        with make_temp_file(blob) as in_fn, make_temp_file() as out_fn:
            try:
                subprocess.check_call(["convert", in_fn, f"pdf:{out_fn}"])
                converted = open(out_fn, "rb").read()
                return converted
            except Exception as e:
                msg = "convert failed"
                raise ConversionError(msg) from e


class PdfToPpmHandler(Handler):
    accepts_mime_types = ["application/pdf", "application/x-pdf"]
    produces_mime_types = ["image/jpeg"]

    @acquire_lock("PdfToPpmHandler")
    def convert(self, blob: bytes, size: int = 500, **kw) -> list[bytes]:
        """Size is the maximum horizontal size."""
        file_list: list[str] = []
        with make_temp_file(blob) as in_fn, make_temp_file() as out_fn:
            pdftoppm = poppler_bin_util("pdftoppm") or "pdftoppm"
            try:
                subprocess.check_call([pdftoppm, "-jpeg", in_fn, out_fn])
                file_list = sorted(glob.glob(f"{out_fn}-*.jpg"))

                converted_images = []
                for fn in file_list:
                    converted = resize(open(fn, "rb").read(), size, size)
                    converted_images.append(converted)
            except Exception as e:
                msg = "pdftoppm failed"
                raise ConversionError(msg) from e
            else:
                return converted_images
            finally:
                for fn in file_list:
                    with contextlib.suppress(OSError):
                        os.remove(fn)


class UnoconvPdfHandler(Handler):
    """Handles conversion from office documents (MS-Office, OOo) to PDF.

    Uses unoconv.
    """

    # TODO: add more if needed.
    accepts_mime_types = [
        "application/vnd.oasis.*",
        "application/msword",
        "application/mspowerpoint",
        "application/vnd.ms-powerpoint",
        "application/vnd.ms-excel",
        "application/vnd.ms-office",
        "application/vnd.ms-word",
        "application/ms-excel",
        "application/vnd.openxmlformats-officedocument.*",
        "text/rtf",
    ]
    produces_mime_types = ["application/pdf"]
    run_timeout = 60
    unoconv = "unoconv"
    _process: subprocess.Popen

    def init_app(self, app) -> None:
        unoconv = app.config.get("UNOCONV_LOCATION")
        found = False
        execute_ok = False

        if unoconv:
            unoconv_path = Path(unoconv)
            found = unoconv_path.is_file()
            if found:
                # make absolute path: avoid errors when running with different
                # CWD
                unoconv = os.path.abspath(unoconv)
                execute_ok = os.access(unoconv, os.X_OK)
                if not execute_ok:
                    self.log.warning(
                        'Not allowed to execute {unoconv}, fallback to "unoconv"',
                        unoconv=repr(unoconv),
                    )
            else:
                self.log.warning(
                    'Cannot find {unoconv}, fallback to "unoconv"',
                    unoconv=repr(unoconv),
                )

        if not unoconv or not found or not execute_ok:
            unoconv = "unoconv"

        self.unoconv = unoconv

    @property
    def unoconv_version(self):
        # Hack for my Mac, FIXME later
        if Path("/Applications/LibreOffice.app/Contents/program/python").exists():
            cmd = [
                "/Applications/LibreOffice.app/Contents/program/python",
                "/usr/local/bin/unoconv",
                "--version",
            ]
        else:
            cmd = [self.unoconv, "--version"]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, _err = process.communicate()
        return out

    def convert(self, blob, **kw):
        """Convert using unoconv converter."""
        timeout = self.run_timeout
        with (
            make_temp_file(blob) as in_fn,
            make_temp_file(prefix="tmp-unoconv-", suffix=".pdf") as out_fn,
        ):
            args = ["-f", "pdf", "-o", out_fn, in_fn]
            # Hack for my Mac, FIXME later
            if Path("/Applications/LibreOffice.app/Contents/program/python").exists():
                cmd = [
                    "/Applications/LibreOffice.app/Contents/program/python",
                    "/usr/local/bin/unoconv",
                    *args,
                ]
            else:
                cmd = [self.unoconv, *args]

            def run_uno() -> None:
                try:
                    self._process = subprocess.Popen(
                        cmd, close_fds=True, cwd=bytes(self.tmp_dir)
                    )
                    self._process.communicate()
                except Exception as e:
                    logger.opt(exception=True).error(
                        "run_uno error: {error}", error=str(e)
                    )
                    msg = "unoconv failed"
                    raise ConversionError(msg) from e

            run_thread = threading.Thread(target=run_uno)
            run_thread.start()
            run_thread.join(timeout)

            try:
                if run_thread.is_alive():
                    # timeout reached
                    self._process.terminate()
                    if self._process.poll() is not None:
                        try:
                            self._process.kill()
                        except OSError:
                            logger.warning(
                                "Failed to kill process {process}",
                                process=self._process,
                            )

                    msg = f"Conversion timeout ({timeout})"
                    raise ConversionError(msg)

                converted = open(out_fn).read()
                return converted
            finally:
                del self._process


class LibreOfficePdfHandler(Handler):
    """Handles conversion from office documents (MS-Office, OOo) to PDF.

    Uses LibreOffice in headless mode.
    """

    # TODO: add more if needed.
    accepts_mime_types = [
        "application/vnd.oasis.*",
        "application/msword",
        "application/mspowerpoint",
        "application/vnd.ms-powerpoint",
        "application/vnd.ms-excel",
        "application/vnd.ms-office",
        "application/ms-excel",
        "application/vnd.openxmlformats-officedocument.*",
        "text/rtf",
    ]
    produces_mime_types = ["application/pdf"]
    run_timeout = 60
    soffice = "soffice"
    _process: subprocess.Popen

    def init_app(self, app: Flask) -> None:
        soffice = app.config.get("SOFFICE_LOCATION")

        if soffice:
            # make absolute path: avoid errors when running with different CWD
            soffice_path = Path(soffice).resolve()
            found = soffice_path.is_file()
            if not found:
                self.log.error("Can't find executable {soffice}", soffice=soffice)

        elif Path("/usr/local/bin/soffice").is_file():
            soffice = "/usr/local/bin/soffice"

        elif Path("/usr/bin/soffice").is_file():
            soffice = "/usr/bin/soffice"

        elif Path("/opt/homebrew/bin/soffice").is_file():
            soffice = "/opt/homebrew/bin/soffice"

        if soffice:
            if not os.access(soffice, os.X_OK):
                self.log.warning('Not allowed to execute "{soffice}"', soffice=soffice)

        else:
            self.log.error("Can't find LibreOffice executable")
            soffice = None

        self.soffice = soffice

    @acquire_lock("LibreOfficePdfHandler")
    def convert(self, blob: bytes, **kw: Any) -> bytes:
        """Convert using soffice converter."""
        timeout = self.run_timeout
        with make_temp_file(blob, tmp_dir=self.tmp_dir) as in_fn:
            cmd = [
                self.soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(self.tmp_dir),
                str(in_fn),
            ]

            def run_soffice() -> None:
                try:
                    self._process = subprocess.Popen(
                        cmd, close_fds=True, cwd=str(self.tmp_dir)
                    )
                    self._process.communicate()
                except subprocess.CalledProcessError as e:
                    logger.debug("CalledProcessError for soffice")
                    logger.debug("returncode:{returncode}", returncode=e.returncode)
                    logger.debug("e.cmd:{cmd}", cmd=e.cmd)
                    logger.debug("stdout:{stdout}", stdout=e.stdout)
                    logger.debug("stderr:{stderr}", stderr=e.stderr)
                    raise ConversionError from e
                except Exception as e:
                    logger.opt(exception=True).error(
                        "soffice error: {error}", error=str(e)
                    )
                    raise ConversionError from e

            run_thread = threading.Thread(target=run_soffice)
            run_thread.start()
            run_thread.join(timeout)
            try:
                if run_thread.is_alive():
                    # timeout reached
                    self._process.terminate()
                    if self._process.poll() is not None:
                        try:
                            self._process.kill()
                        except OSError:
                            logger.warning(
                                "Failed to kill process {process}",
                                process=self._process,
                            )

                    msg = f"Conversion timeout ({timeout})"
                    raise ConversionError(msg)

                out_fn = f"{os.path.splitext(in_fn)[0]}.pdf"
                converted = open(out_fn, "rb").read()
                return converted
            finally:
                if hasattr(self, "_process"):
                    del self._process


class CloudoooPdfHandler(Handler):
    """Handles conversion from OOo to PDF.

    Highly inefficient since file are serialized in base64 over HTTP.

    Deactivated because it's so hard to set up.

    FIXME: needs cleanup, or removal.
    """

    accepts_mime_types = [r"application/.*"]
    produces_mime_types = ["application/pdf"]

    # Hardcoded for now
    SERVER_URL = "http://localhost:8011"

    pivot_format_map = {
        "doc": "odt",
        "docx": "odt",
        "xls": "ods",
        "xlsx": "ods",
        "ppt": "odp",
        "pptx": "odp",
    }

    def convert(self, key):
        in_fn = f"data/{key}.blob"
        in_mime_type = open(f"data/{key}.mime").read()
        file_extension = mimetypes.guess_extension(in_mime_type).strip(".")

        data = b64encode(open(in_fn, "rb").read())
        proxy = ServerProxy(self.SERVER_URL, allow_none=True)

        if in_mime_type.startswith("application/vnd.oasis.opendocument"):
            data = proxy.convertFile(data, file_extension, "pdf")
        else:
            pivot_format = self.pivot_format_map[file_extension]
            data = proxy.convertFile(data, file_extension, pivot_format)
            data = proxy.convertFile(data, pivot_format, "pdf")

        converted = b64decode(data)
        new_key = hashlib.md5(converted).hexdigest()  # noqa: S324
        Path(f"data/{new_key}.blob").write_bytes(converted)
        return new_key


class WvwareTextHandler(Handler):
    accepts_mime_types = ["application/msword"]
    produces_mime_types = ["text/plain"]

    def convert(self, blob, **kw):
        with make_temp_file(blob) as in_fn, make_temp_file() as out_fn:
            try:
                subprocess.check_call(["wvText", in_fn, out_fn])
            except Exception as e:
                msg = "wxText failed"
                raise ConversionError(msg) from e

            converted = open(out_fn, "rb").read()

            encoding = self.encoding_sniffer.from_file(out_fn)
            if encoding in ("binary", None):
                encoding = "ascii"

            try:
                converted_unicode = str(converted, encoding, errors="ignore")
            except Exception:
                traceback.print_exc()
                converted_unicode = str(converted, errors="ignore")

            return converted_unicode
