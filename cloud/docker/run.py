#!/usr/bin/env python

import os


def sh(cmd):
    print(cmd)
    assert os.system(cmd) == 0
    print()


# sh("flask config")
# sh("flask healthcheck")
sh("gunicorn --bind 0.0.0.0:8080 -w 2 'app.flask.main:create_app()'")
