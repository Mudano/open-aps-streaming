
from datetime import datetime, timedelta
from dateutil.parser import parse
import traceback
import shutil
import ohapi
import gzip
import json
import os


class OHError(Exception):
    pass


class OHWrapper:

    def __init__(self, master_token: str=None, users_dict: dict=None, days_cutoff: int=7):

        """
        :param master_token: The master access token for an OH project
        :param users_dict: Takes the form of a list of dictionaries with user ids as keys and access tokens as values
        :param days_cutoff: The number of days past which updated files are ignored rather than downloaded
        """

        if users_dict:

            self.users_dict = users_dict
            self.date_cutoff = datetime.now() - timedelta(days=days_cutoff)

        elif master_token:

            self.OHProject = ohapi.OHProject(master_token)

        else:
            raise OHError('No master token/access-token dictionary specified.')

    # Access-token functions
    def download_user_files(self, outdirectory):

        for user_id, access_token in self.users_dict.items():

            try:
                user_directory = f'{outdirectory}/{user_id}'
                filelist = self.get_user_filelinks(access_token)

                self.download_files_by_links(filelist, user_directory)

            except Exception:
                print(traceback.format_exc())
                continue

        self.extract_directory_files(outdirectory)

    def get_user_filelinks(self, access_token):

        user_files = []
        record = ohapi.api.exchange_oauth2_member(access_token)

        for fileinfo in record['data']:

            if parse(fileinfo['created']) > self.date_cutoff and '.json' in fileinfo['basename']:

                user_files.append(fileinfo['download_url'])

        return user_files

    def download_files_by_links(self, links, directory):

        os.makedirs(directory, exist_ok=True)

        for link in links:

            ohapi.projects.download_file(link, directory)


    # Master-token functions
    def get_all_records(self, output_directory, max_file_size='999m'):

        try:
            self.OHProject.download_all(
                target_dir=output_directory,
                max_size=max_file_size
            )
            self.extract_directory_files(output_directory)

        except Exception:
            raise OHError(traceback.format_exc())


    # Shared
    def extract_directory_files(self, files_directory):

        zipped_files = self.get_files_by_extension('.json.gz', files_directory)

        for filepath in zipped_files:

            with gzip.open(filepath, 'rb') as extract_file, \
                 open(filepath.replace('.gz', ''), 'wb') as outfile:

                    shutil.copyfileobj(extract_file, outfile, length=65536)

            os.remove(filepath)

    @staticmethod
    def get_files_by_extension(extension, directory):

        file_list = []

        for subdir, dirs, files in os.walk(directory):

            for file in files:

                if file.endswith(extension):
                    file_list.append(f'{subdir}/{file}'.replace('\\', '/'))

        return file_list

    def rowify_json_files(self, files_directory):

        json_files = self.get_files_by_extension('.json', files_directory)

        for filepath in json_files:

            with open(filepath) as infile:

                json_list = json.load(infile)

            with open(filepath.replace('.json', '_rowified.json'), 'w') as outfile:

                for line in json_list:

                    outfile.write("%s\n" % json.dumps(line))

            os.remove(filepath)
