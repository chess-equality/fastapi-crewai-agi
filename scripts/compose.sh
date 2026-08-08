#!/usr/bin/env bash
set -euo pipefail

# Disable Docker Compose's automatic .env loading so the reference .env file
# is never used for runtime configuration.
export COMPOSE_DISABLE_ENV_FILE=1

# Default to the local environment if not specified.
ENVIRONMENT=${ENVIRONMENT:-local}
ENV_FILE=".env.${ENVIRONMENT}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

exec docker compose --env-file "$ENV_FILE" "$@"
