#!/usr/bin/env bash

# https://stackoverflow.com/a/77663806/11045433
SCRIPTS_DIRNAME=$(dirname "$( readlink -f "${BASH_SOURCE[0]:-"$( command -v -- "$0" )"}" )")

source "$SCRIPTS_DIRNAME"/definitions.sh

# shellcheck disable=SC2155 # Intended dynamic declaration
declare -A hook_options="($(
  # GitHub CLI api
  # https://cli.github.com/manual/gh_api
  gh api \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    --jq '.[] | "[\(.id | tostring | @sh)]=\(.config.url | @sh)"' \
    /repos/"$REPOSITORY_FULL_NAME"/hooks
))"

# hook_options is an associative array of { [webhook url]: webhook id }
#declare -p hook_options

declare -i hook_options_count
hook_options_count=${#hook_options[@]}

if [ "$hook_options_count" -eq 0 ]; then
  echo "${REPOSITORY_FULL_NAME} has no webhooks configured"
  exit 1
elif [ "$hook_options_count" -eq 1 ]; then
  echo "Selected ${REPOSITORY_FULL_NAME}'s only webhook, '${hook_options[*]}' with ID ${!hook_options[*]}"
  HOOK_ID="${!hook_options[*]}"
else
  declare -a hook_ids
  hook_ids=("${!hook_options[@]}")

  echo "${REPOSITORY_FULL_NAME} has ${hook_options_count} webhooks:"
  for ((i = 0; i < ${#hook_ids[@]}; i++)); do
    hook_id=${hook_ids[i]}
    echo "  ($((i+1))) ID ${hook_id}; URL ${hook_options[$hook_id]}"
  done

  read -rp "Select webhook (1-${hook_options_count}): " opt
  if [[ ! -v hook_ids[$((opt-1))] ]]; then
    echo "$opt is outside the allowed range of inputs"
    exit 1
  fi
  HOOK_ID=${hook_ids[$((opt-1))]}
fi

HOOK_URL="${hook_options[$HOOK_ID]}"

export HOOK_ID
export HOOK_URL
