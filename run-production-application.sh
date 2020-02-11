#!/bin/sh

get_from_ssm () {
  TEMP="$(aws ssm get-parameter --name $1 --query 'Parameter.Value')"
  TEMP=$(eval echo $TEMP)
  echo $TEMP
}


export OPEN_APS_POSTGRES_HOST=$(get_from_ssm openaps-postgres-host)


docker-compose -f docker-compose.yml -f prod.docker-compose.yml up --build \
  --force-recreate -d

volume=$(docker volume inspect --format '{{json .Mountpoint}}' open-aps-streaming_open-aps-postgres-data)

echo "\nThe Nightscout-Open Humans data solution is now running on this machine."
echo " - Postgres data stored at $volume"
echo " - service logs can be followed by calling ./attach-production-logs.sh"
echo " - The application can be stopped by calling ./stop-production.sh"


echo ""
