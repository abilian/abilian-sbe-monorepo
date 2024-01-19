#
# Build
#
FROM python:3.10-slim as build

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip: \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential gcc libpq-dev \
    && rm -rf /var/cache/apt/lists

WORKDIR /app
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


#
# Run
#
FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/cache/apt/lists

RUN groupadd -g 999 flask && \
    useradd -r -u 999 -g flask flask && \
    mkdir /app && \
    chown flask:flask /app

WORKDIR /app

COPY --from=build --chown=flask:flask /app/venv ./venv
COPY --chown=flask:flask src ./src
COPY --chown=flask:flask docker ./docker
COPY --chown=flask:flask front ./front
COPY --chown=flask:flask wsgi.py .

USER 999

ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# App-specific
ENV FLASK_ENV "production"
ENV FLASK_SECRET_KEY "secret"
ENV FLASK_SQLALCHEMY_DATABASE_URI "sqlite:////app/data/db.sqlite3"
ENV FLASK_SQLALCHEMY_TRACK_MODIFICATIONS False
ENV FLASK_DEMO_PASSWORD "pour erick"

CMD [ "./docker/run.py" ]

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f https://localhost:8080/health
