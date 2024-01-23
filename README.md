# About Abilian SBE

## Introduction to Abilian SBE

Abilian SBE (Social Business Engine) is a versatile platform designed for social business applications, particularly in the realm of collaborative or enterprise 2.0 business applications. It is ideal for creating enterprise social networks (ESN) and similar applications.

### Key Features

- **Community-Centric:** Focuses on 'communities' as collaborative spaces, offering services like document management, discussions, wikis, and user timelines.
- **Robust Foundation:** Built upon the `Abilian Core` project, which integrates Flask and SQLAlchemy, providing essential services.
- **Proven Track Record:** Reliably used by several major customers in production environments since mid-2013.

## Installation

### Local (development)

You will need:

- Python 3.9 or more
- A running postgresql database (e.g. `createdb sbe-demo`)
- A redis server
- ImageMagick (for image processing)
- Poppler (for PDF processing)
- LibreOffice (for document conversion)
- Java (what?!? - yes, for Closure)
- Node + npm
- Some libraries: libpq (for Postgres), libjpeg, libxslt, libxml2, libffi, libssl, libmagic, libsqlite3, libbz2...

On Debian/Ubuntu, the following packages is a good starting point (TODO: check what is missing, what is not really needed):

```python
PACKAGES = [
    # Build deps
    "build-essential",
    "python-dev",
    "libpq-dev",
    "libxslt1-dev",
    "libjpeg-dev",
    "libffi-dev",
    "libsqlite3-dev",
    "libbz2-dev",
    # Server stuff
    "postgresql",
    "redis",
    # Other deps (external tools)
    "poppler-utils",
    "imagemagick",
    "libreoffice",
    "default-jdk-headless",
    # Other useful
    "curl",
]
```

Now, create a virtualenv and install the app and its dependencies:

```bash
poetry shell
poetry install
npm install # or npm i
```

Set up the following environment variables (you may put these in a `.env` or `.envs` file and use an environment variable manager like [direnv](https://direnv.net/).

An example of configured `.env` is available: see `example_config/dot_env` file.

```bash
export FLASK_SECRET_KEY=<your secret key>
export FLASK_SQLALCHEMY_DATABASE_URI=postgres://localhost/sbe-demo # or whatever

# For development:
export FLASK_SERVER_NAME=127.0.0.1:5000
export FLASK_DEBUG=true
export FLASK_MAIL_DEBUG=1

# Same redis URL for all variables
export FLASK_REDIS_URI=redis://localhost:6379/0 # or whatever
export FLASK_DRAMATIQ_BROKER_URL=redis://localhost:6379/0
```


Then run:

```bash
flask db initdb # Or flask db upgrade if you already have a database
flask createuser admin <some email address> <username>
flask run
```


## Production

In production, you will need additionally:

- An email server (running locally on the server, e.g. like postfix, that's probably overridable)

```bash
# TBD: not sure if it's needed anymore
export FLASK_PRODUCTION = True

export FLASK_SECRET_KEY=<your secret key>
export FLASK_SQLALCHEMY_DATABASE_URI=postgres://localhost/sbe-demo # or whatever

export FLASK_SITE_NAME="<your site name>"
export FLASK_SERVER_NAME="<your server name>" # i.e. hostname www.mydomain.com...

# TBD (not checked)
export FLASK_MAIL_SERVER=<your email server>
#export FLASK_MAIL_PORT : default 25
#export FLASK_MAIL_USE_TLS : default False
#export FLASK_MAIL_USE_SSL : default False
#export FLASK_MAIL_DEBUG : default app.debug
#export FLASK_MAIL_USERNAME : default None
#export FLASK_MAIL_PASSWORD : default None

# Same redis URL for all variables
export FLASK_REDIS_URI=redis://localhost:6379/0 # or whatever
export FLASK_DRAMATIQ_BROKER_URL=redis://localhost:6379/0
```

You can start the server with:

```bash
gunicorn 'abilian.sbe.app.create_app()'
```

If you are using a web server as a reverse proxy, for instance nginx, you can use the `proxy_pass` option to forward requests to the gunicorn server.

## Configuration example

A step by step configuration example using `honcho`, `.env` and `Python 3.12` is available in the `example_config` folder.

## On Heroku

Click on the button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/abilian/abilian-sbe-monorepo)

(Doesn't fully work - needs to be debugged).
