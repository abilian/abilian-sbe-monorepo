#!/bin/bash

ME="/home/jd/gits/abilian-sbe-monorepo"

${ME}"/node_modules/.bin/lessc" --version

python -c 'import abilian.sbe' || exit 1

echo "tests ok"
##############

export DOMAIN="sbe.jeeorm.net"
export LANG="C.UTF-8"
export NODE_ENV="production"

export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_URI="redis://${REDIS_HOST}:${REDIS_PORT}/"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="sbe3"
export POSTGRES_USER="sbe3"
export POSTGRES_PASSWORD="sbe3"


export ADMIN_MAIL="jd@abilian.com"
export ADMIN_PASSWORD="azerty"

export FLASK_SERVER_NAME="${DOMAIN}"
export SESSION_COOKIE_DOMAIN="${DOMAIN}"
export FLASK_SITE_NAME="SBE server at ${DOMAIN}"
export FLASK_SECRET_KEY="azertyazerty"
export FLASK_SQLALCHEMY_DATABASE_URI="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
export FLASK_MAIL_DEBUG=0
export FLASK_MAIL_SERVER="${DOMAIN}:25"
export FLASK_MAIL_SENDER="sbe-server@${DOMAIN}"
export FLASK_DEBUG=0
export FLASK_LESS_BIN="${ME}/node_modules/.bin/lessc"
export LESS_BIN="${ME}/node_modules/.bin/lessc"

export FLASK_REDIS_URI="${REDIS_URI}0"
export FLASK_BROKER_URL="${REDIS_URI}0"

export FLASK_DRAMATIQ_BROKER="dramatiq.brokers.redis:RedisBroker"
export FLASK_DRAMATIQ_BROKER_URL="${REDIS_URI}0"
export FLASK_DRAMATIC_ABORT_REDIS_URL="${REDIS_URI}1"

export FLASK_APP_LOG_FILE="${ME}/src/instance/app.log"

export CLAMD_CONF_PATH=""

############
env

echo

mkdir -p ${ME}/src/instance
sudo /etc/init.d/clamav-freshclam start
sudo /etc/init.d/clamav-daemon start
sbe_log_server start
# echo "-----------------------------------------------------"
# celery_pid_file="${ME}/src/instance/celery.pid"
# [ -f "${celery_pid_file}" ] && {
#         kill $(cat "${celery_pid_file}")
#         rm "${celery_pid_file}"
# }
# celery -A extranet.celery_app worker -l INFO  --logfile=${ME}/src/instance/celery.log --pidfile="${celery_pid_file}" --detach
# echo "Celery pid file: ${celery_pid_file}"
echo "-----------------------------------------------------"
bash -c 'while :; do pg_isready -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -d ${POSTGRES_DB} -t 10 && break; sleep 5; done'
date
flask assets build
flask initdb
flask createuser --role admin --name admin ${ADMIN_MAIL} ${ADMIN_PASSWORD}

echo "= dramatiq ==============================="
flask worker --processes 4 --threads 1 &
flask scheduler &

echo "= gunicorn ==============================="
gu_pid_file="${ME}/src/instance/gunicorn.pid"
[ -f "${gu_pid_file}" ] && {
        kill $(cat "${gu_pid_file}")
        # rm "${gu_pid_file}"
}
gunicorn extranet.wsgi:app -b :8000  --workers 2 --log-level debug --pid "${gu_pid_file}"
