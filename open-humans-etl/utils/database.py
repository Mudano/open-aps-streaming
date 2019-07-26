
from psycopg2.extras import RealDictCursor
import traceback


class Psycopg2Error(Exception):

    pass


class Database:

    def __init__(self, helpers_connection):

        """
        Database wrapper used for psycopg2
        :param helpers_connection: connection in the form of 'psycopg2.connect(...)'
        """

        try:

            self.con = helpers_connection
            self.con.set_client_encoding('UTF8')

            self.cur = self.con.cursor(cursor_factory=RealDictCursor)

        except Exception:

            raise Psycopg2Error(traceback.format_exc())

    def execute_query(self, query, args=None, multiple=False, return_object=False):

        try:
            if not multiple and not return_object:

                self.cur.execute(query, args)

            elif multiple:

                self.cur.executemany(query, args)

            elif return_object:

                self.cur.execute(query, args)
                query_object = self.cur.fetchall()

                self.con.commit()

                return query_object

            self.con.commit()

        except Exception:

            self.con.rollback()
            raise Psycopg2Error(traceback.format_exc())


    def get_user(self, openhumans_id):

        db_user = self.execute_query(""" SELECT * FROM openaps.oh_etl_log WHERE openaps_id = %(openaps_id)s::BIGINT """, {'openaps_id': openhumans_id}, return_object=True)

        if not db_user:

            self.add_user_to_etl_log(openhumans_id)
            db_user = self.execute_query(""" SELECT * FROM openaps.oh_etl_log WHERE openaps_id = %(openaps_id)s::BIGINT """, {'openaps_id': openhumans_id}, return_object=True)

        return db_user[0]


    def add_user_to_etl_log(self, user_id):

        self.execute_query(""" INSERT INTO openaps.oh_etl_log
                               (openaps_id, treatments_last_index, entries_last_index, profile_last_index, devicestatus_last_index)
                               VALUES
                               (%(openaps_id)s::BIGINT, 0,0,0,0)
                               LIMIT 1
                               ;
                               """, {'openaps_id': user_id})


    def update_user_index(self, user_id, entity, index):

        target_col = entity + '_last_index'

        self.execute_query(f""" UPDATE       openaps.oh_etl_log
                                SET          {target_col} = %(new_index)s
                                WHERE        openaps_id = %(openaps_id)s::BIGINT
                                ;
                                """, {'entity': target_col, 'new_index': index, 'openaps_id': user_id})

    def close(self):

        self.cur.close()
        self.con.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass
