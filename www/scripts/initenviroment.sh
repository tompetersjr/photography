#!/usr/bin/env bash
# We need this for local development as once we mount
# the local folder it overwrites the Dockerfile copy
# of the egg folder.

DIRECTORY=/srv/photos/www.egg-info

if [ ! -d "$DIRECTORY" ]; then
  /srv/env/bin/pip install -e ".[testing]"
fi
