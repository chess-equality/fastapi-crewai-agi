#! /usr/bin/env bash

# Exit in case of error
set -e

./scripts/compose.sh down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error

if [ $(uname -s) = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

./scripts/compose.sh build
./scripts/compose.sh up -d
./scripts/compose.sh exec -T backend bash scripts/tests-start.sh "$@"
