
from helpers import get_connection, get_google_key, get_demographics_url
from utils.upsert_ingester import UpsertIngester
from utils.google_api import Google
from utils.logger import Logger
from models import FormResponse
import traceback
import sys


def retrieve_records():

    records = google.retrieve_worksheet('Form Responses 1')

    mapper = {
        'demographics': {'entity': records, 'object': FormResponse, 'primary_keys': ['project_member_id', 'ts'], 'table': 'member_demographics'}
    }

    return mapper


def ingest(mapper):

    for k, v in mapper.items():

        temp_list = []
        try:

            for item in v['entity']:
                with v['object'](item) as t:
                    temp_list.append(vars(t))

        except Exception:
            logger.error(traceback.format_exc())
            sys.exit(1)

        if temp_list:

            try:
                ingester.add_target(target_data=temp_list,
                                    output_schema='openaps',
                                    table_name=v['table'],
                                    date_format='YYYY-MM-DD HH24:MI:SS',
                                    primary_keys=v['primary_keys']
                                    )
            except Exception:
                print(traceback.format_exc())
                break


if __name__ == '__main__':

    logger = Logger()

    try:
        google = Google(gdrive_key=get_google_key(),
                        spreadsheet_url=get_demographics_url())

        ingester = UpsertIngester(get_connection())

    except Exception:
        logger.error(traceback.format_exc())
        sys.exit(1)

    try:
        mapper = retrieve_records()
        ingest(mapper)

    except Exception:
        logger.error(traceback.format_exc())
        sys.exit(1)
