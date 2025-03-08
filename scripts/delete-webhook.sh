#!/usr/bin/env bash

set -e

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")

source "$SCRIPTS_DIRNAME"/identify-webhook.sh

if [ "$HOOK_URL" = "https://deploy.durhack.com/github-webhook" ]; then
  echo "that's the production webhook, not deleting that." >&2
  exit 1
fi

# GitHub CLI api
# https://cli.github.com/manual/gh_api
gh api \
  --method DELETE \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/"$REPOSITORY_FULL_NAME"/hooks/"$HOOK_ID"

source "$SCRIPTS_DIRNAME"/utils/hyperlink.sh

echo "Webhook targeting '$HOOK_URL' with ID $(hyperlink "$HOOK_ID" "$HOOK_URL") has been deleted"
