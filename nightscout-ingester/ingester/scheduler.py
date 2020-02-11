from pytz import utc

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import os
import boto3

# set up ssm client for config
ssm = boto3.client('ssm', region_name='eu-west-1')


def get_ssm_value(param_name):
    return ssm.get_parameter(Name = param_name)['Parameter']['Value']


pg_host = get_ssm_value('openaps-postgres-host')
pg_port = get_ssm_value('openaps-postgres-port')
pg_db = get_ssm_value('aurora-db-name')
pg_user = get_ssm_value('postgres-nightscout-user')
pg_pass = get_ssm_value('postgres-nightscout-password')
postgres_connection_string = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'


job_stores = {
    'default': SQLAlchemyJobStore(url=postgres_connection_string)
}
executors = {
    'default': ThreadPoolExecutor(20)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 5
}

app_scheduler = BlockingScheduler(jobstores=job_stores, executors=executors, job_defaults=job_defaults, timezone=utc)
