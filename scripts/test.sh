#! /usr/bin/env sh

# Exit in case of error
set -e
set -x

./scripts/compose.sh build
./scripts/compose.sh down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
./scripts/compose.sh up -d
./scripts/compose.sh exec -T backend bash scripts/tests-start.sh "$@"
./scripts/compose.sh down -v --remove-orphans
