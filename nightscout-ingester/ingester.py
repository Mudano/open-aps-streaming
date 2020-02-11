from ingester.scheduler import app_scheduler
from ingester.jobs import nightscout_ingest_job
from datetime import datetime
import os
import math
import boto3

# set up ssm client for config
ssm = boto3.client('ssm', region_name='eu-west-1')


def get_ssm_value(param_name):
    return ssm.get_parameter(Name = param_name)['Parameter']['Value']


if __name__ == '__main__':

    ingest_interval_hours = float(get_ssm_value('openaps-ingest-interval'))
    ingest_interval_seconds = int(math.ceil(ingest_interval_hours * 3600))

    app_scheduler.add_job(nightscout_ingest_job, 'interval', seconds=ingest_interval_seconds,
                          id='1', replace_existing=True)

    try:
        print(f'{datetime.now()} - Beginning the scheduled Nightscout ingest service.')
        app_scheduler.start()
    except (KeyboardInterrupt, SystemExit) as e:
        print(f'an exception was encountered whilst running the scheduler: {e}')
        pass

