"""
contains basic tests of the Postgres tables to be defined in the database.
"""
import psycopg2
from utils.database_config import test_db_admin_config


def table_exists_test_builder(table_name, schema_name):
    """
    Takes a Database table name and schema and returns a test function of whether that table is defined in the
    given schema.
    :return: None => None | AssertError
    """
    def internal_builder():
        try:
            conn = psycopg2.connect(test_db_admin_config.get_connection_string())
            cur = conn.cursor()
            cur.execute("""SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s AND
                table_name = %s""", (schema_name, table_name))
            user_response = cur.fetchall()

            cur.close()
            conn.close()
        except Exception as e:
            print(f"Database connection failed for {test_db_admin_config.user}: " + str(e))
            user_response = []

        assert len(user_response) == 1
    return internal_builder


# checks that the registration app has initialised the OH users table
def test_oh_users_table_exists():
    table_exists_test_builder('openhumans_openhumansmember', 'register')()
