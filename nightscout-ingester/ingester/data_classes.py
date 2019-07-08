import psycopg2
from .scheduler import postgres_connection_string
from ohapi.api import oauth2_token_exchange

class OhUser:

    def __init__(self, member_code, access_token, refresh_token):
        self.member_code = member_code
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self):
        return f'{self.__class__.__name__}('f'oh_code={self.member_code!r})'

    @staticmethod
    def get_all_users():
        try:
            with psycopg2.connect(postgres_connection_string) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM register.openhumans_openhumansmember")
                    data = cursor.fetchall()
                    return [OhUser(u[0], u[1], u[2]) for u in data]
        except Exception as e:
            print(f"Database connection failed attempting to fetch registered OH users: " + str(e))

    def refresh_oh_token(self, client_id, client_secret):
        new_tokens = oauth2_token_exchange(client_id, client_secret, None,
                                           'https://www.openhumans.org/', refresh_token=self.refresh_token)
        self.update_local_tokens(new_tokens['access_token'], new_tokens['refresh_token'])
        self.save_current_tokens()

    def save_current_tokens(self):
        try:
            with psycopg2.connect(postgres_connection_string) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                         UPDATE register.openhumans_openhumansmember
                         SET (access_token, refresh_token) = 
                         (%s, %s)
                         WHERE oh_id = %s""", (self.access_token, self.refresh_token, self.member_code))
        except Exception as e:
            print(f"Database action failed attempting to update OH user tokens: " + str(e))

    def update_local_tokens(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
