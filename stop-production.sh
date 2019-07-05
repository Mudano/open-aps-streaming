#!/bin/sh
docker-compose down

volume=$(docker volume inspect --format '{{json .Mountpoint}}' open-aps-streaming_open-aps-postgres-data)

echo "\nThe Nightscout-Open Humans data solution has now been stopped." 
echo " - Postgres data is still stored at $volume"
echo " - You can start it again by calling ./run-production-application.sh"

echo ""

