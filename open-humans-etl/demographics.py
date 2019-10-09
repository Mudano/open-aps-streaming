
from models import OpenapsSurvey, NightscoutSurvey
from utils.upsert_ingester import UpsertIngester
from gspread.exceptions import APIError
from utils.google_api import Google
import traceback
import os


class DemographicsIngest:

    def __init__(self, logger, google_key, openaps_url, nightscout_url, db_connection):

        self.logger = logger
        self.google = Google(gdrive_key=google_key)
        self.ingester = UpsertIngester(db_connection)

        self.openaps_url = openaps_url
        self.nightscout_url = nightscout_url

    def retrieve_records(self):

        self.google.add_target_spreadsheet(self.openaps_url)
        openaps = self.google.retrieve_worksheet('Form Responses 1')

        self.google.add_target_spreadsheet(self.nightscout_url)
        nightscout = self.google.retrieve_worksheet('Form Responses 1')

        mapper = {
            'openaps': {'entity': openaps, 'object': OpenapsSurvey, 'primary_keys': ['project_member_id', 'ts'], 'table': 'member_demographics'},
            'nightscout': {'entity': nightscout, 'object': NightscoutSurvey, 'primary_keys': ['project_member_id', 'ts'], 'table': 'member_demographics'},
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
                return

            if temp_list:

                try:
                    self.ingester.add_target(target_data=temp_list,
                                        output_schema='openaps',
                                        table_name=v['table'],
                                        date_format='YYYY-MM-DD HH24:MI:SS',
                                        primary_keys=v['primary_keys']
                                        )
                except Exception:
                    self.logger.error(traceback.format_exc())
                    return


def ingest_demographics(logger_class, connection):

    try:
        demo_ingestor = DemographicsIngest(
            logger=logger_class,
            google_key='/credentials.json',
            openaps_url=os.environ['OPEN_APS_OPENAPS_DEMOGRAPHICS_URL'],
            nightscout_url=os.environ['OPEN_APS_NIGHTSCOUT_DEMOGRAPHICS_URL'],
            db_connection=connection
        )

    except Exception:
        raise ConnectionError(f'DEMOGRAPHICS: Error while initiating Demographics Ingestor: {traceback.format_exc()}')

    try:
        mapper = demo_ingestor.retrieve_records()
        demo_ingestor.ingest(mapper)

    except APIError as e:

        if e.response.json['code'] == 503:
            logger_class.error(f'DEMOGRAPHICS: Service unavailable for demographics ingest, skipping.')

        else:
            logger_class.error(f'DEMOGRAPHICS: API Error occurred during demographics ingest: {traceback.format_exc()}')

    except Exception:
        logger_class.error(f'DEMOGRAPHICS: Unexpected error while working with demographics data: {traceback.format_exc()}')
