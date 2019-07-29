from datetime import datetime
from .refresh_view_tables import do_tables_exist, remove_tables, create_tables
from demographics import ingest_demographics
from ingest import ingest_openhumans
from .database import postgres_connection_string
from utils.logger import Logger
import psycopg2


def open_humans_etl_job():

    logger = Logger()

    # define names of view tables
    view_table_names = ['entries_data', 'member_demographics_cleaned']

    logger.debug(f'ETL job commencing at {datetime.now()}')

    with psycopg2.connect(postgres_connection_string) as connection:

        # ingest data from OH to db
        ingest_openhumans(logger, connection)

        # ingest data from demographics gsheet
        ingest_demographics(logger, connection)

        # refresh the 'view' tables created for metabase
        tables_exist = do_tables_exist(view_table_names, connection)

        if tables_exist:
            logger.debug('deleting existing view tables')
            tables_removed = remove_tables(view_table_names, connection)

        logger.debug('creating view tables')
        create_tables(connection)

        logger.debug(f'ETL job completed at {datetime.now()}')
