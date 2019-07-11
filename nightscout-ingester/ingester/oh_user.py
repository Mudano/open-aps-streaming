import psycopg2
from .scheduler import postgres_connection_string
from ohapi.api import oauth2_token_exchange
import requests
from .oh_file_info import OhFileInfo
from datetime import datetime, timedelta
import os


class OhUser:
    """
    Represents a given Open Humans user as stored by this application.
    """

    def __init__(self, member_code, access_token, refresh_token, token_expires):
        self.member_code = member_code
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires = token_expires

    def __repr__(self):
        return f'{self.__class__.__name__}('f'oh_code={self.member_code!r})'

    @staticmethod
    def get_all_users():
        """
        Fetches all registered users from the application database, and builds each into an OhUser class.

        :return: Array of OhUser classes
        """
        try:
            with psycopg2.connect(postgres_connection_string) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM register.openhumans_openhumansmember")
                    data = cursor.fetchall()
                    return [OhUser(u[0], u[1], u[2], u[3]) for u in data]
        except Exception as e:
            print(f"Database connection failed attempting to fetch registered OH users: " + str(e))
            return []

    def refresh_oh_token(self, client_id, client_secret):
        """
        Refreshes the applications saved access and refresh tokens for this user.

        :param client_id: The OpenHumans project client ID.
        :param client_secret: The OpenHumans project secret.
        :return: None
        """
        new_tokens = oauth2_token_exchange(client_id, client_secret, None,
                                           'https://www.openhumans.org/', refresh_token=self.refresh_token)

        self.update_local_tokens(new_tokens['access_token'], new_tokens['refresh_token'],
                                 self.__calculate_expiry_datetime(new_tokens['expires_in']))
        self.save_current_tokens()

    def save_current_tokens(self):
        """
        Persists the classes current tokens and token expiration field to the application database.

        :return: None
        """
        try:
            with psycopg2.connect(postgres_connection_string) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                         UPDATE register.openhumans_openhumansmember
                         SET (access_token, refresh_token, token_expires) = 
                         (%s, %s, %s)
                         WHERE oh_id = %s""",
                                   (self.access_token, self.refresh_token, self.token_expires, self.member_code))
        except Exception as e:
            print(f"Database action failed attempting to update OH user tokens: " + str(e))

    def update_local_tokens(self, access_token, refresh_token, token_expires):
        """
        Updates the class's access and refresh tokens, and expiration time, for this user.

        :param access_token: The new user access token to store in the class.
        :param refresh_token: The new user refresh token to store in the class.
        :param token_expires: The date at which the given access token expires.
        :return: None
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires = token_expires

    def fetch_ns_url(self):
        """
        Looks in the user's OpenHumans account and checks if it has a nightscout URL file with the expected name.
        If a matching file is found it is fetched, and it's contents returned as a string by this function. If no
        matching files (or more than one) are found  then None is returned.

        :return: String | None
        """
        all_file_info = self.fetch_all_file_info()
        ns_url_files = [f for f in all_file_info if f.basename == f'{self.member_code}_open_aps_nightscout_url.txt']

        if len(ns_url_files) > 1:
            print(f'Found multiple Nightscout files for user {self.member_code}, '
                  f'this is not supported and data will not be fetched.')
            return None
        elif len(ns_url_files) < 1:
            print(f'No Nightscout files found for user {self.member_code}, no data will be fetched.')
            return None
        else:
            return ns_url_files[0].get_text_contents()

    def fetch_last_recorded_at(self):
        """
        Looks in the user's OpenHumans account and checks if it has a last updated at file with the expected name.
        If a matching file is found it is fetched, and it's contents returned as a string by this function. If no
        matching files (or more than one) are found the date approximately 5 days ago is returned.

        :return: String | None
        """
        all_file_info = self.fetch_all_file_info()
        last_updated_files = [f for f in all_file_info
                              if f.basename == f'{self.member_code}_last_nightscout_ingest.txt']

        if len(last_updated_files) > 1:
            print(f'Found multiple last ingest files for user {self.member_code}, '
                  f'this is not supported and data will not be fetched.')
            return None
        elif len(last_updated_files) < 1:
            print(f'No last recorded files found for user {self.member_code}, will fetch for last five days.')
            return int(datetime.timestamp(datetime.now() - timedelta(days=5))) * 1000
        else:
            return last_updated_files[0].get_text_contents()

    def fetch_all_file_info(self):
        """
        Fetches the file info for all files stored in OpenHumans by this member.

        :return: An array of OhFileInfo classes.
        """
        file_info_url = \
            f'https://www.openhumans.org/api/direct-sharing/project/exchange-member/?access_token={self.access_token}'

        file_info_response = requests.get(file_info_url)

        if file_info_response.status_code == 200:
            file_info_array = file_info_response.json()["data"]
        else:
            print(f'Request for file information from OpenHumans for user {self.member_code} failed.')
            file_info_array = []

        file_info_objects = [
            OhFileInfo(f['id'], f['basename'], f['created'],
                       f['download_url'], f['metadata']['tags'],
                       f['metadata']['description'], f['source'])
            for f in file_info_array]

        return file_info_objects

    def fetch_and_write_data_file(self, file_type):
        """
        For a given Nightscout file type (e.g. entries), this function will pull all instances of this file on the
        users OpenHumans account with the expected name. If multiple files are found for a given type this represents
        an impossible application state and this users data update will not be carried out.

        If no file of this format is found one will be created with the appropriate name (and with the first segment
        of the file name, which represents the unix time of the last data update, set as 0).

        Whether one file is fetched, or a new one is created locally, the function will return the absolute path
        of this file.

        :param file_type: String giving the Nightscout filetype to download and write to disk.
        :return: The absolute path of the downloaded and written file | None
        """
        all_file_info = self.fetch_all_file_info()
        data_file_end = f'{self.member_code}_{file_type}.json'
        ns_data_files = [f for f in all_file_info if f.basename.endswith(data_file_end)]

        if len(ns_data_files) > 1:
            print(f'Found multiple Nightscout {file_type} files for user {self.member_code}, '
                  f'this is not supported and data will not be fetched.')
            return None
        elif len(ns_data_files) < 1:
            print(f'No {file_type} files found for user {self.member_code}, an initial temp file will be created.')
            unix_time_start = 0
            new_file_name = f'{unix_time_start}_{data_file_end}'
            open(new_file_name, 'a').close()
            return os.path.abspath(new_file_name)
        else:
            file_location = ns_data_files[0].download_file()
            return os.path.abspath(file_location)

    @staticmethod
    def __calculate_expiry_datetime(expires_in_seconds):
        """
        Given the duration of a token in seconds this returns the time (from time of the function being ran) at
        which that token will expire.

        :param expires_in_seconds: The number of seconds in which the token will expire
        :return: A datetime object giving the time at which the token will expire.
        """
        return datetime.now() + timedelta(seconds=expires_in_seconds)



