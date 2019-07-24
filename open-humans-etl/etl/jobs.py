from datetime import datetime
from .refresh_view_tables import do_tables_exist, remove_tables, create_tables
from .database import postgres_connection_string
import psycopg2


def open_humans_etl_job():

    # define names of view tables
    view_table_names = ['entries_data', 'member_demographics_cleaned']

    print(f'ETL job commencing at {datetime.now()}')

    with psycopg2.connect(postgres_connection_string) as connection:

        # refresh the 'view' tables created for metabase
        tables_exist = do_tables_exist(view_table_names, connection)

        if tables_exist:
            print('deleting existing view tables')
            tables_removed = remove_tables(view_table_names, connection)

        print('creating view tables')
        create_tables(connection)

    print(f'ETL job completed at {datetime.now()}')


