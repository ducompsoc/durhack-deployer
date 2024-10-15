#!/bin/bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")

source "$SCRIPTS_DIRNAME"/project-dirname.sh
source "$PROJECT_DIRNAME"/.venv/bin/activate
PYTHONPATH="$PROJECT_DIRNAME"/src:"$PYTHONPATH"
export PYTHONPATH
