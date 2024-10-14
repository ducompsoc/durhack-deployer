#!/bin/bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPT_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")
PROJECT_DIRNAME=$(dirname "$SCRIPT_DIRNAME")

source "$PROJECT_DIRNAME"/.venv/bin/activate
. "$PROJECT_DIRNAME"/.env.celery
export PYTHONPATH="$PROJECT_DIRNAME"/src:"$PYTHONPATH"

celery -A "$CELERY_APP" multi stop ${CELERYD_NODES} \
  --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
  --loglevel="${CELERYD_LOG_LEVEL}" $CELERYD_OPTS
