
from psycopg2.extras import RealDictCursor
import traceback


class Psycopg2Error(Exception):

    pass


class Database:

    def __init__(self, helpers_connection):

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

    def close(self):

        self.cur.close()
        self.con.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass