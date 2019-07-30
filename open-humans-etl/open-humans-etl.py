from etl.scheduler import app_scheduler
from etl.jobs import open_humans_etl_job # open_humans_etl_job
from utils.logger import Logger
from datetime import datetime
import os
import math

if __name__ == '__main__':

    logger = Logger()

    etl_interval_hours = float(os.getenv('ETL_INTERVAL_HOURS'))
    etl_interval_seconds = int(math.ceil(etl_interval_hours * 3600))

    app_scheduler.add_job(open_humans_etl_job, 'interval', seconds=etl_interval_seconds)

    try:
        logger.debug(f'{datetime.now()} - Beginning the scheduled ETL from Open Humans to Postgres.')
        app_scheduler.start()
    except (KeyboardInterrupt, SystemExit) as e:
        logger.error(f'an exception was encountered whilst running the ETL scheduler: {e}')
        pass
