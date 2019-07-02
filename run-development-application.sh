#!/bin/sh
docker-compose -f docker-compose.yml -f dev.docker-compose.yml up --build \
  --force-recreate

