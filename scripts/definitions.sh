#!/usr/bin/env bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")
PROJECT_DIRNAME=$(dirname "$SCRIPTS_DIRNAME")
declare -r PROJECT_DIRNAME
export PROJECT_DIRNAME

REPOSITORY_FULL_NAME="ducompsoc/durhack-deployer"
declare -r REPOSITORY_FULL_NAME
export REPOSITORY_FULL_NAME

function get_webhook_proxy_url() {
  source "$PROJECT_DIRNAME"/.env

  if [ -z "$WEBHOOK_PROXY_URL" ]; then
    echo "WEBHOOK_PROXY_URL is unset; add it to your .env" >&2
    return 1
  fi

  echo "$WEBHOOK_PROXY_URL"
}
export get_webhook_proxy_url
