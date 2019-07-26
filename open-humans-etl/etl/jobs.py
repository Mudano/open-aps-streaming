from datetime import datetime
from .refresh_view_tables import do_tables_exist, remove_tables, create_tables
from demographics import ingest_demographics
from ingest import ingest_openhumans
from .database import postgres_connection_string
import psycopg2


def prep_open_humans_etl_job(logger_class):
    def open_humans_etl_job():

        # define names of view tables
        view_table_names = ['entries_data', 'member_demographics_cleaned']

        logger_class.debug(f'ETL job commencing at {datetime.now()}')

        with psycopg2.connect(postgres_connection_string) as connection:

            # ingest data from OH to db
            ingest_openhumans(logger_class, connection)

            # ingest data from demographics gsheet
            ingest_demographics(logger_class, connection)

            # refresh the 'view' tables created for metabase
            tables_exist = do_tables_exist(view_table_names, connection)

        if tables_exist:
            logger_class.debug('deleting existing view tables')
            tables_removed = remove_tables(view_table_names, connection)

            logger_class.debug('creating view tables')
            create_tables(connection)

        logger_class.debug(f'ETL job completed at {datetime.now()}')

    return open_humans_etl_job
