#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

initenviroment.sh

wait

if [[ -z "${DEPLOY_ENV}" ]]; then
  ENV="development.ini"
else
  ENV="${DEPLOY_ENV}"
fi

if [ ! -f /srv/photos/initdb.cfg ]; then
  /srv/env/bin/initialize_www_db $ENV
  /srv/env/bin/test_data $ENV
  echo "If this does not exist then we init the database" > initdb.cfg
fi

/srv/env/bin/pserve $ENV --reload
