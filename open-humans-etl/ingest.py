
from models import Treatment, Entry, Profile, DeviceStatus, DeviceStatusMetric
from utils.database import Database, Psycopg2Error
from utils.stream_ingester import StreamIngester
from oh_wrapper import OHWrapper, OHError
from json.decoder import JSONDecodeError
from helpers import get_openaps_con
from utils.logger import Logger

import traceback
import shutil
import json
import sys
import os


FILES_DIRECTORY = 'C:/Users/Laurie Bamber/Work/open-aps-streaming/open-humans-etl/data/test'
ENTITY_MAPPER = {
    'treatments': {'object': Treatment, 'table': 'treatments'},
    'entries': {'object': Entry, 'table': 'entries'},
    'profile': {'object': Profile, 'table': 'profile'},
    'device': {'object': DeviceStatus, 'table': 'device_status'},
    'status_metrics': {'object': DeviceStatusMetric,'table': 'device_status_metrics'}
}


def add_user_to_etl_log(user_id):

    db.execute_query(""" INSERT INTO openaps.oh_etl_log
                         (openaps_id, treatments_last_index, entries_last_index, profile_last_index, device_last_index)
                         VALUES
                         (%(openaps_id)s::BIGINT, 0,0,0,0)
                         LIMIT 1
                         """, {'openaps_id': user_id})


def update_user_index(user_id, entity, index):

    target_col = entity + '_last_index'

    db.execute_query(f""" UPDATE openaps.oh_etl_log
                          SET {target_col} = %(new_index)s
                          WHERE openaps_id = %(openaps_id)s::BIGINT
                          ;""",
                          {'entity': target_col, 'new_index': index, 'openaps_id': user_id})


def get_user(openhumans_id):

    db_user = db.execute_query(""" SELECT * FROM openaps.oh_etl_log WHERE openaps_id = %(openaps_id)s::BIGINT """, {'openaps_id': openhumans_id}, return_object=True)

    if not db_user:

        add_user_to_etl_log(openhumans_id)
        db_user = db.execute_query(""" SELECT * FROM openaps.oh_etl_log WHERE openaps_id = %(openaps_id)s::BIGINT """, {'openaps_id': openhumans_id}, return_object=True)

    return db_user[0]


def get_user_filepaths(user_id):

    openhumans_files = []

    for subdirs, dirs, files in os.walk(f'{FILES_DIRECTORY}/{user_id}'):

        for file in files:

            if '.json' in file and file not in openhumans_files:

                openhumans_files.append(f'{subdirs}/{file}'.replace('\\', '/'))

    return openhumans_files


from random import shuffle
def process_file_load(user_id, file, entity, slice_index):

    lines = []
    with open(file) as infile:

        if slice_index != 0:

            for i in range(slice_index - 1):
                infile.readline()

        for json_line in infile:

            lines.append({**json.loads(json_line), **{'user_id': user_id, 'source_entity': 0}})

    print(user_id, entity, str(len(lines)))

    shuffle(lines)

    ingest(lines[:1000], ENTITY_MAPPER[entity])
    update_user_index(user_id, entity, slice_index + len(lines))

    if entity == 'device':

        status_metrics = [{**device['openaps'], **{'device_status_id': device['_id']}} for device in lines[:100] if 'openaps' in device]
        ingest(status_metrics, ENTITY_MAPPER['status_metrics'])
        update_user_index(user_id, entity, slice_index + len(lines))


def ingest(lod, lod_params):

    temp_list = []
    for item in lod:
        with lod_params['object'](item) as t:
            temp_list.append(vars(t))

    if temp_list:

        ingester.add_target(
            target_data=temp_list,
            output_schema='openaps',
            table_name=lod_params['table'],
            date_format='YYYY-MM-DD HH24:MI:SS'
        )


def main(output_directory):

    user_folders = [x for x in next(os.walk(output_directory))[1]]

    for folder_id in user_folders:

        user_id = str(folder_id)

        user = get_user(user_id)

        user_files = get_user_filepaths(user_id)

        for file in user_files:

            for entity in ENTITY_MAPPER.keys():

                if entity in file:

                    last_index = user[entity + '_last_index']

                    try:
                        process_file_load(user_id, file, entity, last_index)

                    except (JSONDecodeError, TypeError):
                        logger.error(f'Incorrect json format found for user with ID {user_id} and file with name {file}. {traceback.format_exc()}')
                    except IndexError:
                        logger.error(f'Index out of sync for user with ID {user_id} and file with name {file}. {traceback.format_exc()}')
                    except Psycopg2Error:
                        logger.error(f'Insert error while working with ID {user_id} and file with name {file}. {traceback.format_exc()}')
                    except MemoryError:
                        logger.error(f'Memory maxed while working with ID {user_id} and file with name {file}. {traceback.format_exc()}')


if __name__ == '__main__':

    logger = Logger()

    try:
        db = Database(get_openaps_con())
        ingester = StreamIngester(get_openaps_con())

        users_dict = db.execute_query(""" SELECT oh_id, access_token FROM register.openhumans_openhumansmember; """, return_object=True)
        oh = OHWrapper(logger=logger,
                       files_directory=FILES_DIRECTORY,
                       users_dict=users_dict)

    except Psycopg2Error:
        logger.error(f'Error occurred while initialising classes and sourcing user records: {traceback.format_exc()}')
        sys.exit(1)

    try:
        oh.download_user_files()
        main(FILES_DIRECTORY)

    except Psycopg2Error:
        logger.error(f'Error occurred while working with DB: {traceback.format_exc()}')
        sys.exit(1)

    except Exception:
        logger.error(f'Error occurred during ingestion: {traceback.format_exc()}')
        sys.exit(1)

    finally:
        shutil.rmtree(FILES_DIRECTORY)
        os.mkdir(FILES_DIRECTORY)
