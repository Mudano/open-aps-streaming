"""
contains basic tests of the Postgres Users to be defined in the database.
Also defines tests of these user's permissions.
"""
import psycopg2
from utils.database_config import test_db_admin_config, test_db_register_config, test_db_ns_config


def user_exists_test_builder(user_name):
    """
    Takes a Database username and returns a test function of whether that user is defined in the database.
    :return: None => None | AssertError
    """
    def internal_builder():
        try:
            conn = psycopg2.connect(test_db_admin_config.get_connection_string())
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (user_name, ))
            user_response = cur.fetchall()

            cur.close()
            conn.close()
        except Exception as e:
            print(f"Database connection failed for {test_db_admin_config.user}: " + str(e))
            user_response = []

        assert len(user_response) == 1
    return internal_builder


# checks that the admin user exists in the database
def test_admin_user_exists():
    user_exists_test_builder(test_db_admin_config.user)()


# checks that the registration web-app user exists in the database
def test_register_user_exists():
    user_exists_test_builder(test_db_register_config.user)()

# checks that the nightscout ingest user exists in the database
def test_ns_ingest_user_exists():
    user_exists_test_builder(test_db_register_config.user)()


def test_register_user_cannot_create_public():
    """
    Attempts to create a table in the public schema as the register user, test passes if this is met
    by an exception, else the test fails.
    :return: None | AssertError
    """
    try:
        conn = psycopg2.connect(test_db_register_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("create table public.testing(test integer)")
        blocked = False
        print("registration user was permitted to create a new table in the public schema")

        cur.close()
        conn.close()
    except Exception as e:
        blocked = True

    assert blocked


def test_register_user_can_create_register():
    """
    Attempts to create a table in the register schema as the register user, test passes if this is
    a success, else the test fails.
    :return: None | AssertError
    """
    try:
        conn = psycopg2.connect(test_db_register_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("create table register.testing(test integer)")
        created = True

        cur.close()
        conn.close()
    except Exception as e:
        created = False
        print("registration user was not permitted to create a new table in the register schema")

    assert created


def test_ns_ingest_user_cannot_create_public():
    """
    Attempts to create a table in the public schema as the ns ingest user, test passes if this is met
    by an exception, else the test fails.
    :return: None | AssertError
    """
    try:
        conn = psycopg2.connect(test_db_ns_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("create table public.testing(test integer)")
        blocked = False
        print("registration user was permitted to create a new table in the public schema")

        cur.close()
        conn.close()
    except Exception as e:
        blocked = True

    assert blocked


def test_ns_ingest_user_can_create_ns_ingest():
    """
    Attempts to create a table in the ns_ingest schema as the ns_ingest user, test passes if this is
    a success, else the test fails.
    :return: None | AssertError
    """
    try:
        conn = psycopg2.connect(test_db_ns_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("create table ns_ingest.testing(test integer)")
        created = True

        cur.close()
        conn.close()
    except Exception as e:
        created = False
        print("ns_ingest user was not permitted to create a new table in the ns_ingest schema")

    assert created


def test_ns_ingest_user_can_select_openhumansmember():
    """
    Attempts to select from the register.openhumans_openhumansmember table as the ns_ingest user,
    as this user needs to be able to access the OH user details of registered users. Test passes if this is
    a success, else the test fails.
    :return: None | AssertError
    """

    # custom failure needed because the fetchall response will be empty list which evals as false
    user_response = 'custom failure'
    try:
        conn = psycopg2.connect(test_db_ns_config.get_connection_string())
        cur = conn.cursor()
        cur.execute("select * from register.openhumans_openhumansmember")
        user_response = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print("ns_ingest user was not permitted to select from openhumans_openhumansmember")

    assert user_response != 'custom failure'

