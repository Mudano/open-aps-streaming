"""
Contains a config helper class for easily defining a Postgres definition.
Also provides a pre-instantiated instance of the class built from the expected
environment variables.
"""
import os


class DatabaseConfig:
    """
    Helper class for holding SQL database connection configurations.
    """

    def __init__(self, host, port, db_name, user, password):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.password = password

    def get_connection_string(self):
        """
        Constructs a SQL connection string from the class parameters.
        :return: String
        """
        return f"host='{self.host}' port='{self.port}' " \
            f"dbname='{self.db_name}' user='{self.user}' password='{self.password}'"

    @staticmethod
    def __get_test_server_config_from_env():
        """
        fetches the test db server's host, port, and database name from the environment
        :return: (host, port, database_name)
        """
        test_host = os.environ['POSTGRES_HOST']
        test_port = os.environ['POSTGRES_PORT']
        test_db_name = os.environ['POSTGRES_DB']
        return test_host, test_port, test_db_name

    @staticmethod
    def from_admin_test_environment():
        """
        Uses preset environment variables to define the admin database account.
        :return: DatabaseConfig class for the test admin user.
        """
        test_host, test_port, test_db_name = DatabaseConfig.__get_test_server_config_from_env()
        admin_user = os.environ['POSTGRES_ADMIN_USER']
        admin_password = os.environ['POSTGRES_ADMIN_PASSWORD']
        return DatabaseConfig(test_host, test_port, test_db_name, admin_user, admin_password)


# below are preset users constructed from environment variables and ready to be used in tests
test_db_admin_config = DatabaseConfig.from_admin_test_environment()
