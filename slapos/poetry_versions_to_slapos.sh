#!/bin/sh
#
# This utility converts python requirements from project managed by poetry
# to a versions.cfg content suitable for SlapOS. The result is intended to
# be a basis for a version list
#
# Warning about format:
# - remove '[]' extensions of dependanes (ie: sentry-sdk[flask] -> sentry-sdk)
# - add the ':whl' suffix for all packages

project_path=$1
[ -z "${project_path}" ] && project_path="."

cd "${project_path}"

poetry_reqs () {
   poetry export -f requirements.txt --without-hashes --without-urls
}

echo "[versions]"
poetry_reqs | sed 's/ *;.*//' | sed 's/\(.*\)==\(.*\)/\1 = \2:whl/'
