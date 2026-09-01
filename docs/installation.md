# Full Installation Guide

This guide provides a detailed walkthrough for installing software on a Ubuntu Linux server.

The following instructions are tailored for a bare-metal server setup, specifically for a server named "sbe.example.com."

(For cloud installations, the 'cloud' folder contains configuration examples for Docker, Nua, SlaoOS.)

## Create a dedicated user

A user "sbe" with `sudoer` rights.

```bash
sudo useradd -m -s /bin/bash -G sudo sbe
sudo su - sbe
```

## Packages requirements

List of packages to install with `apt`:

    default-jre
    libreoffice-java-common
    build-essential
    python-dev
    libpq-dev
    libxslt1-dev
    libjpeg-dev
    libffi-dev
    libsqlite3-dev
    libbz2-dev
    postgresql
    redis
    poppler-utils
    imagemagick
    libreoffice
    clamav
    nodejs
    npm
    honcho
    curl

Optional (if using Nginx and Letsencrypt like service):

    nginx
    certbot


## Create a Python virtual env (Python version 3.12)

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-dev python3.12-venv
```


### Installation of `pip` from sources:

```bash
sudo curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
```

### Virtual environment named "venv":

```bash
python3.12 -m venv venv
. venv/bin/activate
```

## Clone SBE source code and install

```bash
git clone --depth 1  --branch main https://github.com/abilian/abilian-sbe-monorepo.git
cd abilian-sbe-monorepo
pip install -U pip setuptools poetry
pip install .
```

## Create a Postgresql database (here named "sbe")

```bash
sudo -u postgres psql
create database sbe;
create user sbe with encrypted password 'sbe';
grant all privileges on database sbe to sbe;
```

## Start services if necessary
```bash
sudo systemctl start clamav-freshclam
sudo systemctl start clamav-daemon
sudo systemctl start redis
```

## If needed, create a few directories

### Maildir:

```bash
mkdir -p "${HOME}"/Maildir/{cur,new,tmp}
chmod 0700 "${HOME}"/Maildir/{cur,new,tmp}
```

### Local flask instance:

This should be created by Flask at first start, however in the `abilian-sbe-monorepo` directory:

```bash
mkdir -p ./src/instance
```

## Front-end assets

The CSS and JavaScript are built by Vite. From the `abilian-sbe-monorepo`
directory:

```bash
make front
```

That runs `npm install` and `npm run build` in `vite/`, and copies the result
into `src/abilian/sbe/static/vite/`.

You can skip this entirely when installing from a wheel: `pip install
abilian-sbe` ships the built assets, so a released install needs no Node at all.
Node is only required when building from a source checkout.

## Nginx proxy

If using Nginx, check you have configured `nginx` with relevant SSL keys. See example file `sbe.example.com` in this directory.

Note: older example `nginx` configurations contain a permanent redirect for
`/static/min/...`, the output directory of the webassets pipeline. That pipeline
has been removed, nothing is served under that path any more, and the rule can
be dropped. The rest of the setup is otherwise pretty standard.

## Create a local '.env' file

See 'dot_env' file in this directory. Of course `FLASK_*` variables can be declared using other Flask configuration methods.

## First initialization of SBE application

This commands are required only once:

```bash
flask initdb
flask createuser --role admin --name admin admin@example.com some_password
```

## Start the SBE application

Create a local `Procfile` containing those lines (adapt the `gunicorn` configuration)

```
worker: flask worker
scheduler: flask scheduler
web: gunicorn extranet.wsgi:app -b :8000 --workers 4 --log-file -
```

And finally start the application using `honcho`:

```bash
honcho -f Procfile start
```
