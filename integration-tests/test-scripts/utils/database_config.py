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
    def from_test_env(user_env_var, pass_env_var):
        """
        fetches the test db server's host, port, and database name from fixed environment
        variables, and fetches a given username and password from given env var strings.
        Constructs and returns an instance of DatabaseConfig from these.
        :return: DatabaseConfig
        """
        test_host = os.environ['POSTGRES_HOST']
        test_port = os.environ['POSTGRES_PORT']
        test_db_name = os.environ['POSTGRES_DB']
        user = os.environ[user_env_var]
        password = os.environ[pass_env_var]
        return DatabaseConfig(test_host, test_port, test_db_name, user, password)


# below are preset users constructed from environment variables and ready to be used in tests
test_db_admin_config = DatabaseConfig.from_test_env('POSTGRES_ADMIN_USER', 'POSTGRES_ADMIN_PASSWORD')

test_db_register_config = DatabaseConfig.from_test_env('POSTGRES_REGISTER_USER', 'POSTGRES_REGISTER_PASSWORD')
