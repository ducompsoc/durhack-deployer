#!/bin/bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPT_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")
PROJECT_DIRNAME=$(dirname "$SCRIPT_DIRNAME")

source "$PROJECT_DIRNAME"/.venv/bin/activate
. "$PROJECT_DIRNAME"/.env.celery
export PYTHONPATH="$PROJECT_DIRNAME"/src:"$PYTHONPATH"

python -m main_queue_worker.app
