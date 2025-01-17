# About Abilian SBE

Build status: [![builds.sr.ht status](https://builds.sr.ht/~sfermigier/abilian-sbe/commits/main/ubuntu-lts.yml.svg)](https://builds.sr.ht/~sfermigier/abilian-sbe/commits/main/ubuntu-lts.yml?)

<!-- toc -->

- [Introduction to Abilian SBE](#introduction-to-abilian-sbe)
- [Key Features](#key-features)
- [Installation and Deployment](#installation-and-deployment)
  * [Local (development)](#local-development)
  * [Production](#production)
  * [Configuration example](#configuration-example)
  * [On Heroku](#on-heroku)
- [Development](#development)
- [License compliance](#license-compliance)

<!-- tocstop -->

## Introduction to Abilian SBE

Abilian SBE (Social Business Engine) is a versatile platform designed for social business applications, particularly in the realm of collaborative or enterprise 2.0 business applications. It is ideal for creating enterprise social networks (ESN) and similar applications.

## Key Features

- **Community-Centric:** Focuses on 'communities' as collaborative spaces, offering services like document management, discussions, wikis, and user timelines.
- **Robust Foundation:** Built upon the `Abilian Core` project, which integrates Flask and SQLAlchemy, providing essential services.
- **Proven Track Record:** Reliably used by several major customers in production environments since mid-2013.
- **User-Centric Design:** Provides an intuitive and user-friendly interface, supporting rich profiles, conversation threads, and a social and content graph.
- **Extensibility and Flexibility:** Built with a platform approach, allowing for customization and easy extension through APIs, making it suitable for a wide range of business applications such as CRM, knowledge management, and e-learning.
- **Enterprise 2.0 Tools:** Incorporates core components of Enterprise 2.0, such as wikis, forums, mailing lists, document repositories, and activity streams, promoting collaboration and innovation within organizations.
- **Standards-Based Interoperability:** Supports ActivityStreams, OASIS CMIS (via Apache cmislib) for document management, and semantic web standards like JSON-LD, ensuring compatibility with existing enterprise systems and open standards.
- **Advanced Search and Tagging:** Features robust tagging and search capabilities to help users quickly find relevant content, improving knowledge sharing and capitalizing on collective intelligence.
- **Microservices Architecture:** Can be deployed as microservices, providing scalability and flexibility for modern enterprise environments.
- **Security and Identity Management:** Includes built-in services for identity management, security, and audit logging, ensuring compliance with enterprise-grade security requirements.
- **Document Management System (DMS):** Offers a simple yet effective DMS for organizations, integrated with collaboration tools such as forums and wikis, facilitating seamless document sharing and collaboration.

> [!NOTE]
> Join the Abilian SBE developer community and help shape the future of open-source enterprise collaboration! A first step would be to look at our **[Architecture Decision Records](notes/adrs) (ADRs)**—a collection of enhancement proposals where your expertise can make a real impact. Explore, discuss, and contribute your ideas and code enhancements to build the next generation of social business apps.


## Installation and Deployment

See also: [Installation Guide](docs/installation.md)

### Local (development)

You will need:

- Python 3.10 or more
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


### Production

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

### Configuration example

A step-by-step configuration example using `honcho`, `.env` and `Python 3.12` is available in the `example_config` folder.

### On Heroku

Click on the button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/abilian/abilian-sbe-monorepo)

(Doesn't fully work - needs to be debugged).

## Development

See:

- [Development Guide](docs/development.md)
- [Contributing Guidelines](docs/contributing.md)
- [Roadmap](docs/roadmap.md)
- [Architecture Decision Records](notes/adrs)
- [Changelog](CHANGELOG.md)


## License compliance

As of `Tue Nov  5 08:50:20 CET 2024`, this project is compliant with the REUSE Specification version 3.2.

```
* Bad licenses: 0
* Deprecated licenses: 0
* Licenses without file extension: 0
* Missing licenses: 0
* Unused licenses: 0
* Used licenses: CC-BY-4.0, LGPL-3.0-only
* Read errors: 0
* Files with copyright information: 1712 / 1712
* Files with license information: 1712 / 1712

Congratulations! Your project is compliant with version 3.2 of the REUSE Specification :-)
```
