from urllib.parse import urlparse
import requests


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
        if test_url.status_code != 200:
            return None
        return url


