#!/bin/bash

if [ -z "$1" ]; then
  echo "Missing username argument"
  echo "Usage: add-deployment-user.sh username"
  exit 1
fi

# create the user account
adduser "$1" --disabled-password --home /home/"$1" --comment ""

# enable the `ssh-agent` user-service on the new account
systemd-run --wait --collect --user --machine="$1"@ systemctl enable --user ssh-agent
