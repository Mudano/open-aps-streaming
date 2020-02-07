#!/bin/sh

get_from_ssm () {
  TEMP="$(aws ssm get-parameter --name $1 --query 'Parameter.Value')"
  TEMP=$(eval echo $TEMP)
  echo $TEMP
}

OPEN_APS_MASTER_PASSWORD=$(get_from_ssm aurora-db-master-password) 
export PGPASSWORD=$OPEN_APS_MASTER_PASSWORD

# set environment variables from ssm store
export METABASE_PASSWORD=$(get_from_ssm open-aps-metabase-password)
export POSTGRES_NIGHTSCOUT_USER=$(get_from_ssm postgres-nightscout-user)
export POSTGRES_NIGHTSCOUT_PASSWORD=$(get_from_ssm postgres-nightscout-password)
export POSTGRES_REGISTER_USER=$(get_from_ssm postgres-register-user)
export POSTGRES_REGISTER_PASSWORD=$(get_from_ssm postgres-register-password)
export POSTGRES_INGESTOR_PASSWORD=$(get_from_ssm postgres-ingestor-password)
export POSTGRES_ADMIN_VIEWER_PASSWORD=$(get_from_ssm postgres-admin-viewer-password)
export POSTGRES_VIEWER_PASSWORD=$(get_from_ssm postgres-viewer-password)
export POSTGRES_EXT_OPENAPS_APP_PASSWORD=$(get_from_ssm postgres-openaps-app-password)
export DOWNLOADER_ADMIN_PASSWORD_HASH=$(get_from_ssm postgres-app-admin-password-hash)

ls init-scripts/*.sql | xargs cat | psql -h open-aps-aurora-db-auroradb-qkxwjngdap1l.cluster-c9tzjjvpib4n.eu-west-1.rds.amazonaws.com -U  open_aps_admin -d open_aps_db -v ON_ERROR_STOP=1 -f -

