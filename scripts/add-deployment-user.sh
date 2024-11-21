#!/bin/bash

if [ -z "$1" ]; then
  echo "Missing username argument"
  echo "Usage: add-deployment-user.sh username"
  exit 1
fi

adduser "$1" --disabled-password --home /home/"$1" --comment ""
