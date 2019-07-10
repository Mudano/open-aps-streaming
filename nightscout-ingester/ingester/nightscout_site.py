from urllib.parse import urlparse
import requests
from .file_utilities import process_ns_entries

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

    def get_new_entries_since(self, start_datetime, end_datetime):
        """
        Get Nightscout entries data, ~60 days at a time.
        Retrieve ~60 days at a time until either (a) the start point is reached
        (after_date parameter) or (b) a run of 6 empty calls or (c) Jan 2010.
        """
        # end = arrow.get(before_date).ceil('second').timestamp * 1000
        # start_date = arrow.get('2010-01-01').floor('second').timestamp * 1000
        # if after_date:
        #    start_date = arrow.get(after_date).floor('second').timestamp * 1000

        ns_entries_url = self.url + '/api/v1/entries.json'

        ns_params = {
            'count': 1000000,
            'find[date][$gt]': start_datetime,
            'find[date][$lte]': end_datetime
        }

        try:
            new_entries_response = requests.get(ns_entries_url, params=ns_params)

            if new_entries_response.status_code == 200:
                new_processed_entries = process_ns_entries(new_entries_response)
            else:
                print(f'An error was encountered downloading new entries data from ${self.url}')
                new_processed_entries = []
        except:
            print(f'An error was encountered downloading new entries data from ${self.url}')
            new_processed_entries = []

        return new_processed_entries

        # Start a JSON array.
        # file_obj.write('[')
        # initial_entry_done = False  # Entries after initial are preceded by commas.

        # Get 8 million second chunks (~ 1/4th year) until none, or start reached.
        # complete = False
        # curr_end = end
        # curr_start = curr_end - 5000000000
        # empty_run = 0
        # retries = 0
        # while not complete:
        #     if curr_start < start_date:
        #         curr_start = start_date
        #         complete = True
        #         logger.debug('Final round (starting date reached)...')
        #     log_update(oh_member, 'Querying entries from {} to {}...'.format(
        #         arrow.get(curr_start / 1000).format(),
        #         arrow.get(curr_end / 1000).format()))
        #     ns_params = {'count': 1000000}
        #     ns_params['find[date][$lte]'] = curr_end
        #     ns_params['find[date][$gt]'] = curr_start
        #     entries_req = requests.get(ns_entries_url, params=ns_params)
        #     logger.debug('Request complete.')
        #     assert entries_req.status_code == 200 or retries < MAX_RETRIES, \
        #         'NS entries URL != 200 status'
        #     if entries_req.status_code != 200:
        #         retries += 1
        #         logger.debug("RETRY {}: Status code is {}".format(
        #             retries, entries_req.status_code))
        #         continue
        #     logger.debug('Status code 200.')
        #     retries = 0
        #     logger.debug('Retrieved {} entries...'.format(len(entries_req.json())))
        #     if entries_req.json():
        #         empty_run = 0
        #         for entry in entries_req.json():
        #             if initial_entry_done:
        #                 file_obj.write(',')  # JSON array separator
        #             else:
        #                 initial_entry_done = True
        #             json.dump(entry, file_obj)
        #         logger.debug('Wrote {} entries to file...'.format(len(entries_req.json())))
        #     else:
        #         empty_run += 1
        #         if empty_run > 6:
        #             logger.debug('>10 empty calls: ceasing entries queries.')
        #             break
        #     curr_end = curr_start
        #     curr_start = curr_end - 5000000000
        #
        # file_obj.write(']')  # End of JSON array.
        # logger.debug('Done writing entries to file.')

