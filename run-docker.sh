#!/bin/sh
if [ -z "$DISCORD_TOKEN" ]; then
  echo "Environment variable DISCORD_TOKEN is not set."
  exit 1
fi

echo "$DISCORD_TOKEN" > token
pipenv run bot
