#!/usr/bin/env bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")

source "$SCRIPTS_DIRNAME"/definitions.sh
webhook_proxy_url="$(get_webhook_proxy_url)"

gosmee client \
  "$webhook_proxy_url" \
  "http://deploy.durhack-dev.com/github-webhook"
