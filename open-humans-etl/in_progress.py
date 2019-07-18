

"""

    1. Extract records from OH

        Options:
            - download_all function
            - download_specific, based on ingestion ETL table

    2. Extract compressed .gz files

    3. For each file:

        a. Slice .json file based on index in ETL table

        b. If new records after slice, upload to db

        c. Update/add row in ETL table showing the most recent completed slice

"""

from models import Treatment, Entry, Profile, DeviceStatus, DeviceStatusMetric
from helpers import get_openaps_con
from utils.database import Database
from datetime import datetime, timedelta
import json
import os

db = Database(get_openaps_con())
BASE_DIRECTORY = 'C:/Users/Laurie Bamber/Work/open-aps-streaming/open-humans-etl/data/openaps/'
LAST_RUN = datetime.now() - timedelta(weeks=1)
MAPPER = {
    'treatment': {'object': Treatment, 'table': 'treatments'},
    'entries': {'object': Entry, 'table': 'entries'},
    'profiles': {'object': Profile, 'table': 'profile'},
    'devicestatus': {'object': DeviceStatus, 'table': 'device_status'},
    'status_metrics': {'object': DeviceStatusMetric,'table': 'device_status_metrics'}
}


def add_user_to_etl_log(user_id):

    db.execute_query(""" INSERT INTO openaps.oh_etl_log
                         (openhumans_id, treatments_last_index, entries_last_index, profile_last_index, device_last_index)
                         VALUES
                         (%(openhumans_id)s, 0,0,0,0)
                         LIMIT 1
                         """, {'openhumans_id': user_id})

    user = get_user(user_id)

    return user


def get_user(openhumans_id):

    user = db.execute_query(""" SELECT * FROM openaps.oh_etl_log WHERE openhumans_id = %(openhumans_id)s """, {'openhumans_id': openhumans_id})

    if not user:

        user = add_user_to_etl_log(ufolder)

    return user


def get_user_filepaths(user_folder):

    openhumans_files = []

    for subdirs, dirs, files in os.walk(BASE_DIRECTORY + user_folder):

        for file in files:

            if '.json' in file and file not in openhumans_files:

                openhumans_files.append(f'{subdirs}/{file}')

    return openhumans_files


user_folders = [x for x in next(os.walk(BASE_DIRECTORY))[1]]

for ufolder in user_folders:

    user = get_user(str(ufolder))
    user_files = get_user_filepaths(str(ufolder))

    for file in user_files:

        for k, v in MAPPER.items():

            if k in file:

                last_index = user[k + '_last_index']

                with open(file) as infile:

                    lines = [{**json.load(json_line), **{'user_id'}}
                             for json_line in infile.read().split('\n')[last_index:]]

                    ingest(lines, v)





