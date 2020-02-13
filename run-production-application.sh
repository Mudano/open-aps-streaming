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
export OPEN_APS_POSTGRES_NIGHTSCOUT_USER=$(get_from_ssm postgres-nightscout-user)
export OPEN_APS_NIGHTSCOUT_PASSWORD=$(get_from_ssm postgres-nightscout-password)
export OPEN_APS_INGEST_INTERVAL_HOURS=$(get_from_ssm openaps-ingest-interval)
export OPEN_APS_POSTGRES_EXT_OPENAPS_APP_PASSWORD=$(get_from_ssm postgres-openaps-app-password)
export OPEN_APS_DOWNLOADER_EMAIL=$(get_from_ssm openaps-downloader-app-email)
export OPEN_APS_DOWNLOADER_EMAIL_PASS=$(get_from_ssm openaps-downloader-app-email-password)
export OPEN_APS_DOWNLOADER_SECRET_KEY=$(get_from_ssm openaps-downloader-secret-key)
export OPEN_APS_DOWNLOADER_SLACK_KEY=$(get_from_ssm openaps-downloader-slack-key)
export OPEN_APS_DOWNLOADER_METABASE_KEY=$(get_from_ssm openaps-downloader-metabase-key)
export OPEN_APS_DOWNLOADER_METABASE_URL=$(get_from_ssm openaps-metabase-url)
export OPEN_APS_DOWNLOADER_ADMIN_EMAIL=$(get_from_ssm openaps-downloader-admin-email)
export OPEN_APS_DOWNLOADER_PUBLIC_URL=$(get_from_ssm openaps-downloader-url)
export OPEN_APS_POSTGRES_METABASE_PASSWORD=$(get_from_ssm open-aps-metabase-password)
export OPEN_APS_POSTGRES_INGESTOR_PASSWORD=$(get_from_ssm postgres-ingestor-password)
export OPEN_APS_ETL_INTERVAL_HOURS=$(get_from_ssm openaps-etl-interval)
export OPEN_APS_OPENAPS_DEMOGRAPHICS_URL=$(get_from_ssm openaps-openaps-demographics-url)
export OPEN_APS_NIGHTSCOUT_DEMOGRAPHICS_URL=$(get_from_ssm openaps-nightscout-demographics-url)


docker-compose -f docker-compose.yml -f prod.docker-compose.yml up --build \
  --force-recreate -d

echo "\nThe Nightscout-Open Humans data solution is now running on this machine."
echo " - service logs can be followed by calling ./attach-production-logs.sh"
echo " - The application can be stopped by calling ./stop-production.sh"

echo ""
