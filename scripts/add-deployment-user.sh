#!/bin/bash

if [ -z "$1" ]; then
  echo "Missing username argument"
  echo "Usage: add-deployment-user.sh username"
  exit 1
fi

# script should exit if any command fails
grep -F e <<< "$-"; errexit_unset=$?
((errexit_unset)) && set -o errexit

# create the user account
adduser "$1" --disabled-password --home /home/"$1" --gecos ""

# enable the `ssh-agent` user-service on the new account
systemd-run --wait --collect --user --machine="$1"@ systemctl enable --user ssh-agent

# restore unmodified options
((errexit_unset)) && set +o errexit
