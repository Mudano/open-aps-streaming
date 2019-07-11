from urllib.parse import urlparse
import requests
from .utility_functions import process_ns_data
from datetime import datetime

class NightscoutSite:
    """
    Represents a given Nightscout Site
    """

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return f'{self.__class__.__name__}('f'url={self.url!r})'

    def validate_url(self):
        url_test_result = self.__normalize_and_test_url()
        if url_test_result:
            self.url = url_test_result
        else:
            print(f"Error encountered when validating Nightscout URL {self.url}, class url not changed.")

    def __normalize_and_test_url(self):
        """
        Return URL with scheme + netloc only, e.g. 'https://www.example.com'.
        If no scheme is specified, try https, fall back to http.
        Return None if a GET to the normalized URL doesn't return a 200 status.
        """
        working_url = self.url
        if not working_url.startswith('http'):
            working_url = f'https://{working_url}'
        parsed = urlparse(working_url)
        url = parsed.scheme + '://' + parsed.netloc
        try:
            test_url = requests.get(url)
        except requests.exceptions.SSLError:
            url = 'http://' + parsed.netloc
            test_url = requests.get(url)
        except:
            return None
        if test_url.status_code != 200:
            return None
        return url

    def get_new_data_since(self, nightscout_data_type, start_datetime, end_datetime):
        """

        :param nightscout_data_type: The NightscoutDataTpe class for the data to be fetched from NS (e.g. entries)
        :param start_datetime: Unix timestamp (ms). Data fetched will have a date greater than this.
        :param end_datetime: Unix timestamp (ms). Data fetched will have a date lesser than or equal to this.
        :return: String containing the processed data as json objects separated by linebreaks.
        """
        ns_data_url = f'{self.url}/api/v1/{nightscout_data_type.name}.json'

        if nightscout_data_type.time_filter_name == 'created_at':
            start_datetime = datetime.utcfromtimestamp(start_datetime / 1000).isoformat()
            end_datetime = datetime.utcfromtimestamp(end_datetime / 1000).isoformat()

        ns_params = {
            'count': 1000,
            f'find[{nightscout_data_type.time_filter_name}][$gt]': start_datetime,
            f'find[{nightscout_data_type.time_filter_name}][$lte]': end_datetime
        }

        try:
            new_data_response = requests.get(ns_data_url, params=ns_params)

            if new_data_response.status_code == 200:
                new_processed_data = process_ns_data(new_data_response, nightscout_data_type.sensitive_keys)
            else:
                print(f'An error was encountered downloading new {nightscout_data_type.name} data from ${self.url}')
                new_processed_data = []
        except Exception as e:
            print(f'An error was encountered downloading new {nightscout_data_type.name} data from ${self.url}: {e}')
            new_processed_data = []
        return new_processed_data


