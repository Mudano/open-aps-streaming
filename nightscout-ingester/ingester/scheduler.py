from pytz import utc

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import os


pg_host = os.environ['POSTGRES_HOST']
pg_port = os.environ['POSTGRES_PORT']
pg_db = os.environ['POSTGRES_DB']
pg_user = os.environ['POSTGRES_USER']
pg_pass = os.environ['POSTGRES_PASSWORD']
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
