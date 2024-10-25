#!/bin/bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")

source "$SCRIPTS_DIRNAME"/identify-webhook.sh

# GitHub CLI api
# https://cli.github.com/manual/gh_api
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/"$REPOSITORY_FULL_NAME"/hooks/"$HOOK_ID"/tests
