"""

"""
import psycopg2



def test_database_connection():
    try:
        conn = psycopg2.connect("host='open-aps-db' dbname='open_aps' user='int_test_admin' password='just_a_testing_password'")
        conn_successful = True
    except Exception as e:
        print("Database connection failed: " + str(e))
        conn_successful = False
    assert conn_successful


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4

