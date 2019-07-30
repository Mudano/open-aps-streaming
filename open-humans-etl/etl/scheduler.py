from pytz import utc
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from .database import postgres_connection_string


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

app_scheduler = BlockingScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
