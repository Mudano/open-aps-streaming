
from constants import FILES_DIRECTORY, ENTITY_MAPPER
from utils.database import Database, Psycopg2Error
from utils.upsert_ingester import UpsertIngester
from json.decoder import JSONDecodeError
from oh_wrapper import OHWrapper

import traceback
import shutil
import json
import sys
import os


class OpenHumansETL:

    def __init__(self, logger, db_connection):

        """
        Class to initialise downloading of files from OH, convert files into lists of dictionaries, and upload to db
        :param logger: logging object passed from parent script
        :param db_connection: database connection in the form of psycopg2.connect(...)
        """

        self.logger = logger

        try:
            self.db = Database(db_connection)

            self.ingester = UpsertIngester(db_connection)

            self.oh = OHWrapper(logger=logger, files_directory=FILES_DIRECTORY)

        except Psycopg2Error:
            logger.error(f'Error occurred while initialising classes. Breaking script.: {traceback.format_exc()}')
            sys.exit(1)

        os.makedirs(FILES_DIRECTORY, exist_ok=True)

    def upload_to_db(self, directory=FILES_DIRECTORY):

        """
        Finds all user folders in a given directory, finds files in each folder, passes to processing function
        :param directory: parent directory containing user folders
        """

        user_folders = [x for x in next(os.walk(directory))[1]]

        for user_id in user_folders:

            try:

                user = self.db.get_user(user_id)
                user_files = self.oh.get_files_by_extension(f'{directory}/{user_id}', '.json')

                for filename in user_files:

                    entity_name = [k for k in ENTITY_MAPPER.keys() if k in filename][0]
                    last_index = user[entity_name + '_last_index']

                    try:
                        self.process_file_load(user_id, filename, entity_name, last_index)

                    except (JSONDecodeError, TypeError):
                        self.logger.error(
                            f'Incorrect json format found for user with ID {user_id} and file with name {filename}. {traceback.format_exc()}')
                    except IndexError:
                        self.logger.error(
                            f'Index out of sync for user with ID {user_id} and file with name {filename}. {traceback.format_exc()}')
                    except Psycopg2Error:
                        self.logger.error(
                            f'Insert error while working with ID {user_id} and file with name {filename}. {traceback.format_exc()}')
                    except MemoryError:
                        self.logger.error(
                            f'Memory maxed while working with ID {user_id} and file with name {filename}. {traceback.format_exc()}')

            except IndexError:
                continue
            except Exception:
                self.logger.error(f'Error while working with user {user_id}: {traceback.format_exc()}')
                continue

    def process_file_load(self, user_id, file, entity, slice_index):

        """
        Navigates to slice point in json file, extracts records, passes to ingest function, updates user indexes
        :param user_id: OH ID of user, same as folder name
        :param file: local file to extract records from
        :param entity: table entity, either treatments, entries, devicestatus or profile
        :param slice_index: The last line records were downloaded from in the json file
        """

        lines = []
        with open(file) as infile:

            # if slice_index != 0:
            #     for i in range(slice_index - 1):
            #         infile.readline()

            for json_line in infile:

                lines.append({**{'user_id': user_id, 'source_entity': 0}, **json.loads(json_line)})

        self.ingest(lines, ENTITY_MAPPER[entity])
        self.db.update_user_index(user_id, entity, slice_index + len(lines))

        if entity == 'devicestatus':

            status_metrics = [{**{'device_status_id': device['_id']}, **device['openaps']} for device in lines if 'openaps' in device]
            self.ingest(status_metrics, ENTITY_MAPPER['status_metrics'])

    def ingest(self, lod, lod_params):

        """
        Uses upsert_ingester.py to upload a list of dictionaries to a given table
        :param lod: List of dictionaries to be inserted
        :param lod_params: Parameters used for inserting to db, including mapped model object and table name
        """

        temp_list = []
        for item in lod:                                # for each record

            with lod_params['object'](item) as t:       # convert record to model

                temp_list.append(vars(t))               # extract defined variables from model and append to upload list

        if temp_list:

            self.ingester.add_target(
                target_data=temp_list,
                output_schema='openaps',
                table_name=lod_params['table'],
                primary_keys=lod_params['primary_keys'],
                date_format='YYYY-MM-DD HH24:MI:SS'
            )


def ingest_openhumans(logger, connection, users_dict=None):

    try:
        etl_class = OpenHumansETL(logger=logger, db_connection=connection)

        if not users_dict:
            get_users_tokens_sql = """SELECT oh_id, access_token FROM register.openhumans_openhumansmember"""
            users_dict = etl_class.db.execute_query(get_users_tokens_sql, return_object=True)

        etl_class.oh.download_user_files(users_dict)
        etl_class.upload_to_db()

    except Psycopg2Error:
        logger.error(f'Error occurred while working with DB: {traceback.format_exc()}')
        sys.exit(1)

    except Exception:
        logger.error(f'Error occurred during ingestion: {traceback.format_exc()}')
        sys.exit(1)

    finally:
        shutil.rmtree(FILES_DIRECTORY)
        os.mkdir(FILES_DIRECTORY)
