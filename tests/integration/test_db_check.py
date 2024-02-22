import re


def test_supported_db(app):
    # Not really a test, just a check that the test suite is configured
    # with a supported DB
    config = app.config
    sqla_uri = config["SQLALCHEMY_DATABASE_URI"]
    assert re.match("(sqlite|postgres|mysql)://.*", sqla_uri)
