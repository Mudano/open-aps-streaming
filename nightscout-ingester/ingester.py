from ingester.scheduler import app_scheduler
from ingester.jobs import nightscout_ingest_job
from datetime import datetime

if __name__ == '__main__':
    app_scheduler.add_job(nightscout_ingest_job, 'interval', seconds=10, id='1', replace_existing=True)

    try:
        print(f'{datetime.now()} - Beginning the scheduled Nightscout ingest job.')
        app_scheduler.start()
    except (KeyboardInterrupt, SystemExit) as e:
        print(f'an exception was encountered whilst running the scheduler: {e}')
        pass
else:
    print('why am I not main?')
