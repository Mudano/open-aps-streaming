#!/bin/sh

cleanup() {
  echo "\nStopping Docker services and deleting now that tests have terminated.\n"
  docker-compose -f docker-compose.yml -f int.docker-compose.yml kill
  docker-compose -f docker-compose.yml -f int.docker-compose.yml rm -f
}

trap cleanup EXIT

docker-compose -f docker-compose.yml -f int.docker-compose.yml up --build \
  --force-recreate --exit-code-from open-aps-int
