#!/usr/bin/env bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")
PROJECT_DIRNAME=$(dirname "$SCRIPTS_DIRNAME")
export PROJECT_DIRNAME
