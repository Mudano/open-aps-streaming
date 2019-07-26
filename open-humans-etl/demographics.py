
from utils.upsert_ingester import UpsertIngester
from utils.google_api import Google
from models import FormResponse
import traceback
import sys
import os


class DemographicsIngest:

    def __init__(self, logger, google_key, demographics_url, db_connection):

        self.logger = logger
        self.google = Google(gdrive_key=google_key,spreadsheet_url=demographics_url)
        self.ingester = UpsertIngester(db_connection)

    def retrieve_records(self):

        records = self.google.retrieve_worksheet('Form Responses 1')

        mapper = {
            'demographics': {'entity': records, 'object': FormResponse, 'primary_keys': ['project_member_id', 'ts'], 'table': 'member_demographics'}
        }
        return mapper

    def ingest(self, mapper):

        for k, v in mapper.items():

            temp_list = []
            try:

                for item in v['entity']:
                    with v['object'](item) as t:
                        temp_list.append(vars(t))

            except Exception:
                self.logger.error(traceback.format_exc())
                sys.exit(1)

            if temp_list:

                try:
                    self.ingester.add_target(target_data=temp_list,
                                        output_schema='openaps',
                                        table_name=v['table'],
                                        date_format='YYYY-MM-DD HH24:MI:SS',
                                        primary_keys=v['primary_keys']
                                        )
                except Exception:
                    print(traceback.format_exc())
                    break


def ingest_demographics(logger_class, connection):

    try:
        demo_ingestor = DemographicsIngest(
            logger=logger_class,
            google_key=os.environ['OPEN_APS_DEMOGRAPHICS_GOOGLE_KEYPATH'],
            demographics_url=os.environ['OPEN_APS_DEMOGRAPHICS_SHEET_URL'],
            db_connection=connection
        )

    except Exception:
        raise ConnectionError(f'Error while initiating Demographics Ingestor: {traceback.format_exc()}')

    try:
        mapper = demo_ingestor.retrieve_records()
        demo_ingestor.ingest(mapper)

    except Exception:
        logger_class.error(traceback.format_exc())
        pass
