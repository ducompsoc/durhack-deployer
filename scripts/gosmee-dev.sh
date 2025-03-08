#!/usr/bin/env bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")

source "$SCRIPTS_DIRNAME"/project-dirname.sh
source "$PROJECT_DIRNAME"/.env

if [ -z "$WEBHOOK_PROXY_URL" ]; then
  echo "WEBHOOK_PROXY_URL is unset"
  exit 1
fi

gosmee client \
  "$WEBHOOK_PROXY_URL" \
  "http://deploy.durhack-dev.com/github-webhook"
