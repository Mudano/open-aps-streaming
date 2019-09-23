
from datetime import datetime, timedelta
from dateutil.parser import parse
import traceback
import requests
import shutil
import ohapi
import gzip
import json
import os
import re

class OHError(Exception):
    pass


class OHWrapper:

    def __init__(self, logger, files_directory, master_token: str=None, days_cutoff: int=7):

        """
        :param logger: The class object used for logging application errors. See utils folder
        :param files_directory: The directory for files to be downloaded to. End of path should not have leading slash
        :param master_token (optional): A token used to initialise the OHAPI Project class
        :param days_cutoff (optional): The number of days past which updated files are ignored rather than downloaded
        """

        self.logger = logger
        self.FILES_DIRECTORY = files_directory
        self.DATE_CUTOFF = datetime.now() - timedelta(days=days_cutoff)

        if not os.path.isdir(self.FILES_DIRECTORY):
            os.mkdir(self.FILES_DIRECTORY)

        if master_token:

            try:
                self.OHProject = ohapi.OHProject(master_token)
            except Exception:
                raise OHError(f'Error while initialising project class with master token: {traceback.format_exc()}')

    # Access-token functions
    def download_user_files(self, users_dict):

        """
        Iterates over a list of users, gets their download links from OH, downloads each file in turn
        :param users_dict: Takes the form of a list of dictionaries with user ids as keys and access tokens as values
        """

        for user_record in users_dict:

            try:
                user_directory = f"{self.FILES_DIRECTORY}/{user_record['oh_id']}/"
                filelist = self.get_user_filelinks(user_record['access_token'])

                self.download_files_by_links(filelist, user_directory)

            except Exception:
                self.logger.error(f"Error while downloading records for ID {user_record['oh_id']}: {traceback.format_exc()}")
                continue

    def get_user_filelinks(self, access_token):

        """
        Queries OH for user info, appends filelinks to be downloaded if the file is recently updated and the name matches a specific format
        :param access_token: Unique token for project member
        :param user_id: ID of user used for error-logging
        :return: List of download links in URL format
        """

        user_files = []
        record = ohapi.api.exchange_oauth2_member(access_token)

        for fileinfo in record['data']:
            if self.filename_checker(fileinfo['basename']):
                user_files.append({'url': fileinfo['download_url'], 'filename': fileinfo['basename']})

        return user_files

    def download_files_by_links(self, links, user_directory):

        """
        :param links: List of download links for a users files
        :param user_directory: Output directory for files to be downloaded to
        """

        os.makedirs(user_directory, exist_ok=True)

        for link in links:

            tries = 0
            while True:
                try:
                    ohapi.projects.download_file(link['url'], f"{user_directory}/{link['filename']}")
                    break

                except requests.exceptions.ConnectionError:
                    if tries < 5:
                        tries = tries + 1
                    else:
                        raise requests.exceptions.ConnectionError

    @staticmethod
    def filename_checker(filename):

        """
        Expected file-format is '<integer_ts>_<integer_user_id>_<entity_string>.json'
        """
        return bool(re.match(r"^\d+_\d+_(treatments|devicestatus|entries|profile)\.json$", filename)) or 'data_sharing_consent.txt' in filename

    # Master-token functions
    def get_all_records(self, max_file_size='999m'):

        """
        Downloads all files for an OH project to a given directory, and then unzips all files from .gz format
        :param max_file_size: Maximum size of a file allowed to be downloaded
        """

        try:
            self.OHProject.download_all(
                target_dir=self.FILES_DIRECTORY,
                max_size=max_file_size
            )
            self.extract_directory_files()

        except Exception:
            raise OHError(f'Error while downloading all files: {traceback.format_exc()}')


    # Shared
    def extract_directory_files(self):

        """
        Gets list of all .gz files in directory, unzips and copies contents to .json, removes .gz file
        """

        zipped_files = self.get_files_by_extension(self.FILES_DIRECTORY, '.json.gz')

        for filepath in zipped_files:

            with gzip.open(filepath, 'rb') as extract_file, \
                 open(filepath.replace('.gz', ''), 'wb') as outfile:

                    shutil.copyfileobj(extract_file, outfile, length=65536)

            os.remove(filepath)

    def get_files_by_extension(self, directory, extension):

        """
        Finds all files in the files directory with a given extension
        """

        file_list = []

        for subdir, dirs, files in os.walk(directory):

            for file in files:

                if file.endswith(extension):
                    file_list.append(f'{subdir}/{file}'.replace('\\', '/'))

        return file_list

    def rowify_json_files(self):

        """
        Used to convert a json array into individual records separated by '\n'
        """

        json_files = self.get_files_by_extension(self.FILES_DIRECTORY, '.json')

        for filepath in json_files:

            with open(filepath) as infile:

                json_list = json.load(infile)

            with open(filepath.replace('.json', '_rowified.json'), 'w') as outfile:

                for line in json_list:

                    outfile.write("%s\n" % json.dumps(line))

            os.remove(filepath)

    def get_user_sharing_flag(self, user_id):

        """
        Used to identify sharing permissions for each user, based on a .txt file
        """

        sharing_file = f'{self.FILES_DIRECTORY}/{user_id}/{user_id}_open_aps_data_sharing_consent.txt'

        if not os.path.isfile(sharing_file):
            return 0
        else:
            file = open(sharing_file, 'r').read()
            if 'openaps' in file:
                return 0
            elif 'nsf' in file:
                return 1
            elif 'both' in file:
                return 2
            elif 'none' in file:
                return 3
