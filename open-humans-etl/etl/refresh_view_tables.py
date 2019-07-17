

def does_table_exist(table_name, pg_connection):
    table_check_sql_string = \
        "select exists(select * from information_schema.tables where table_name=%s and table_schema='openaps')"

    try:
        with pg_connection.cursor() as cursor:
            cursor.execute(table_check_sql_string, (table_name,))
            data = cursor.fetchone()[0]
            return data
    except Exception as e:
        print(f"Error encountered checking if {table_name} exists, table removal will be attempted: {e}")
        return True


def do_tables_exist(table_names, pg_connection):

    # initialised True, will be set to false if any table checks fail to find the tables
    all_tables_exist = True

    try:
        for name in table_names:
            table_exists = does_table_exist(name, pg_connection)
            all_tables_exist = all_tables_exist and table_exists
        return all_tables_exist
    except Exception as e:
        print(f"Database connection failed checking table existence, table removal will be attempted: {e}")
        return True


def remove_table(table_name, pg_connection):
    table_remove_sql_string = "drop table %s"

    try:
        with pg_connection.cursor() as cursor:
            cursor.execute(table_remove_sql_string)
            return True
    except Exception as e:
        print(f"Error dropping {table_name}, ETL will not progress: {e}")
        return False


def remove_tables(table_names, pg_connection):

    # initialised True, will be set to false if any table deletions fail
    all_tables_dropped = True

    try:
        for name in table_names:
            table_dropped = remove_table(name, pg_connection)
            all_tables_dropped = all_tables_dropped and table_dropped
        return all_tables_dropped
    except Exception as e:
        print(f"Error encountered trying to delete a view table, ETL will not progress: {e}")
        return False



def create_tables():
    pass