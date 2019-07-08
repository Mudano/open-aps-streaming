"""
contains basic tests of the Postgres Schemas to be defined in the database.
Tests are ran using the database admin account.
"""
import psycopg2
from utils.database_config import test_db_admin_config


def test_public_schema_exists():
    """
    Tests that the default public schema exists in the application database.
    :return: None | AssertError
    """
    try:
        conn = psycopg2.connect(test_db_admin_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'public'")
        public_schema = cur.fetchall()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database connection failed for {test_db_admin_config.user}: " + str(e))
        public_schema = []

    assert len(public_schema) == 1


def test_register_schema_exists():
    """
    Tests that the register web-app's schema exists in the application database.
    :return: None | AssertError
    """
    try:
        conn = psycopg2.connect(test_db_admin_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'register'")
        public_schema = cur.fetchall()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database connection failed for {test_db_admin_config.user}: " + str(e))
        public_schema = []

    assert len(public_schema) == 1


def test_ns_ingest_schema_exists():
    """
    Tests that the nightscout ingest schema exists in the application database.
    :return: None | AssertError
    """
    try:
        conn = psycopg2.connect(test_db_admin_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'ns_ingest'")
        public_schema = cur.fetchall()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database connection failed for {test_db_admin_config.user}: " + str(e))
        public_schema = []

    assert len(public_schema) == 1


def test_public_schema_empty():
    """
    The public schema is not used by any component of the application. This test ensures that
    no tables are being written to it.
    :return: None | AssertError
    """
    try:
        conn = psycopg2.connect(test_db_admin_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        public_tables = cur.fetchall()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database connection failed for {test_db_admin_config.user}: " + str(e))
        public_tables = ['test forced to fail due to exception']

    assert len(public_tables) == 0

