#!/bin/sh
docker-compose -f ../int.docker-compose.yml --project-directory ../ kill
docker-compose -f ../int.docker-compose.yml --project-directory ../ rm -f
