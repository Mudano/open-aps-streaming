#!/bin/sh

get_from_ssm () {
  TEMP="$(aws ssm get-parameter --name $1 --query 'Parameter.Value')"
  TEMP=$(eval echo $TEMP)
  echo $TEMP
}


export OPEN_APS_POSTGRES_HOST=$(get_from_ssm openaps-postgres-host)
export OPEN_APS_POSTGRES_PORT=$(get_from_ssm openaps-postgres-port)
export OPEN_APS_POSTGRES_DB=$(get_from_ssm aurora-db-name)
export OPEN_APS_POSTGRES_REGISTER_USER=$(get_from_ssm postgres-register-user)
export OPEN_APS_REGISTER_PASSWORD=$(get_from_ssm postgres-register-password)
export OPEN_APS_REGISTRATION_BASE_URL=$(get_from_ssm openaps-register-url)
export OPEN_APS_REGISTRATION_PORT=$(get_from_ssm openaps-register-port)
export OPEN_HUMANS_CLIENT_ID=$(get_from_ssm open-humans-client-id)
export OPEN_HUMANS_PROJECT_ADDRESS=$(get_from_ssm open-humans-project-address)
export OPEN_HUMANS_CLIENT_SECRET=$(get_from_ssm open-humans-client-secret)
export REGISTER_APP_DJANGO_SECRET_KEY=$(get_from_ssm openaps-register-django-key)


docker-compose -f docker-compose.yml -f prod.docker-compose.yml up --build \
  --force-recreate -d

volume=$(docker volume inspect --format '{{json .Mountpoint}}' open-aps-streaming_open-aps-postgres-data)

echo "\nThe Nightscout-Open Humans data solution is now running on this machine."
echo " - service logs can be followed by calling ./attach-production-logs.sh"
echo " - The application can be stopped by calling ./stop-production.sh"

echo ""
