"""
contains basic connection tests for all users of the application database.
"""
import psycopg2
from utils.database_config import test_db_admin_config, test_db_register_config


def database_connection_test_builder(db_config):
    """
    Takes a DatabaseConfig class instance and returns a database connection test function
    :return: None => None | AssertError
    """
    def internal_builder():
        try:
            psycopg2.connect(db_config.get_connection_string())
            conn_successful = True
        except Exception as e:
            print(f"Database connection failed for {db_config.user}: " + str(e))
            conn_successful = False
        assert conn_successful
    return internal_builder


# Uses the database admin account to run a basic connectivity test.
def test_admin_database_connection():
    database_connection_test_builder(test_db_admin_config)()


# uses the database register web-page account to run a basic connectivity test
def test_register_database_connection():
    database_connection_test_builder(test_db_register_config)()
