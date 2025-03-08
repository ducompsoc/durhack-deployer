#!/usr/bin/env bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")

source "$SCRIPTS_DIRNAME"/definitions.sh
webhook_proxy_url="$(get_webhook_proxy_url)"
webhook_secret="$(openssl rand -base64 48)"

gh_api_response="$(
  # GitHub CLI api
  # https://cli.github.com/manual/gh_api
  gh api \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    /repos/"$REPOSITORY_FULL_NAME"/hooks \
      -f "name=web" -F "active=true" -f "events[]=push" \
      -f "config[content_type]=json" \
      -f "config[insecure_ssl]=0" \
      -f "config[url]=$webhook_proxy_url" \
      -f "config[secret]=$webhook_secret"
)"

# shellcheck disable=SC2155 # Intended dynamic declaration
declare -A hook="($(echo "$gh_api_response" | jq -r '. | "[\(.id | tostring | @sh)]=\(.config.url | @sh)"'))"

declare -i hook_count
hook_count=${#hook[@]}

if [ "$hook_count" -ne 1 ]; then
  echo "something odd happened" >&2
  echo "$gh_api_response" >&2
  exit 1
fi

source "$SCRIPTS_DIRNAME"/utils/hyperlink.sh

hook_url="$(echo "$gh_api_response" | jq -r '.url')"
echo "$hook_url"
echo "New webhook targeting '${hook[*]}' has been created, its ID is $(hyperlink "${!hook[*]}" "$hook_url")"
echo "Its secret is '$webhook_secret'; update your $(hyperlink "config/local.toml" "file://$(realpath "$PROJECT_DIRNAME"/config/local.toml)") accordingly"
