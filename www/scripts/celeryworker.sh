#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

wait

if [[ -z "${DEPLOY_ENV}" ]]; then
  ENV="development.ini"
else
  ENV="${DEPLOY_ENV}"
fi

while [ ! -d /srv/photos/www.egg-info ]
do
  sleep 2
done

/srv/env/bin/celery worker -A www.celeryconf --ini $ENV
