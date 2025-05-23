# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

import fileinput
import sys
from email.parser import FeedParser

import click
from flask.cli import with_appcontext
from loguru import logger

from .tasks import check_maildir, process_email


@click.command()
@with_appcontext
def inject_email(filename="-") -> None:
    """Read one email from stdin, parse it, forward it in a task to be
    persisted."""
    do_inject_email(filename)


def do_inject_email(filename="-") -> None:
    parser = FeedParser()

    try:
        # iterate over stdin
        for line in fileinput.input(filename):
            parser.feed(line)
    except KeyboardInterrupt:
        logger.info("Aborted by user, exiting.")
        sys.exit(1)
    except BaseException:
        logger.opt(exception=True).error("Error during email parsing")
        sys.exit(1)
    finally:
        # close the parser to generate a email.message
        message = parser.close()
        fileinput.close()

    if message:
        # make sure no email.errors are present
        if not message.defects:
            process_email.send(message)
        else:
            logger.error(
                "email has defects, message content:\n"
                "------ START -------\n"
                "{message}"
                "\n------ END -------\n",
                message=message,
                extra={"stack": True},
            )
    else:
        logger.error("no email was parsed from stdin", extra={"stack": True})


@click.command()
@with_appcontext
def check_email() -> None:
    """Read one email from current user Maildir, parse it, forward it in a
    task to be persisted."""

    check_maildir()
