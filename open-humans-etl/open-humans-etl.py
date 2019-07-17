from etl.scheduler import app_scheduler
# from ingester.jobs import nightscout_ingest_job
from datetime import datetime
import os
import math

if __name__ == '__main__':

    etl_interval_hours = float(os.getenv('ETL_INTERVAL_HOURS'))
    etl_interval_seconds = int(math.ceil(etl_interval_hours * 3600))

    # app_scheduler.add_job(nightscout_ingest_job, 'interval', seconds=ingest_interval_seconds,
    #                       id='1', replace_existing=True)

    try:
        print(f'{datetime.now()} - Beginning the scheduled ETL from Open Humans to Postgres.')
        app_scheduler.start()
    except (KeyboardInterrupt, SystemExit) as e:
        print(f'an exception was encountered whilst running the ETL scheduler: {e}')
        pass

