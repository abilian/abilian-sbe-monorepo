# Copyright (c) 2012-2024, Abilian SAS

import re

from abilian.app import Application


def test_supported_db(app: Application):
    # Not really a test, just a check that the test suite is configured
    # with a supported DB
    config = app.config
    sqla_uri = config["SQLALCHEMY_DATABASE_URI"]
    assert re.match("(sqlite|postgres|mysql)://.*", sqla_uri)
