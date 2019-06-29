#!/bin/sh

docker-compose -f ../int.docker-compose.yml --project-directory ../ rm -f && \
  docker-compose -f ../int.docker-compose.yml --project-directory ../ build --no-cache && \
docker-compose -f ../int.docker-compose.yml --project-directory ../ up --force-recreate -d
