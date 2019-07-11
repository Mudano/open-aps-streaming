import requests
import shutil


class OhFileInfo:
    """
    Represents the file information that the OpenHumans API returns for a given user. Each instance
    corresponds to a file in OpenHumans
    """

    def __init__(self, file_id, basename, created, download_url, tags, description, source):
        self.file_id = file_id
        self.basename = basename
        self.created = created
        self.download_url = download_url
        self.tags = tags
        self.description = description
        self.source = source

    def __repr__(self):
        return f'{self.__class__.__name__}('f'file_id={self.file_id!r}, download_url={self.download_url})'

    def get_text_contents(self):
        """
        Attempts to download the contents of the corresponding file and encode the contents as text.

        :return: The contents of the file as a String | None
        """
        file_download_url = self.download_url
        response = requests.get(file_download_url)

        if response.status_code == 200:
            return response.text
        else:
            print(f'Request for contents of {self.download_url} from OpenHumans failed.')
            return None

    def download_file(self):
        local_filename = self.basename
        with requests.get(self.download_url, stream=True) as r:
            with open(local_filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return local_filename
