
import traceback
import shutil
import ohapi
import gzip
import json
import sys
import os


class OHError(Exception):
    pass


class OHWrapper:

    def __init__(self, master_token):

        self.OHProject = ohapi.OHProject(master_token)

    def get_all_records(self, output_directory, max_file_size='999m'):

        try:
            resp = self.OHProject.download_all(
                target_dir=output_directory,
                max_size=max_file_size
            )
            return resp

        except Exception:
            raise OHError(traceback.format_exc())

    def get_member_list(self):

        return self.OHProject.project_data

    @staticmethod
    def get_files_by_extension(extension, directory):

        file_list = []

        for subdir, dirs, files in os.walk(directory):

            for file in files:

                if file.endswith(extension):

                    file_list.append(f'{subdir}/{file}'.replace('\\', '/'))

        return file_list


    def extract_directory_files(self, files_directory):

        zipped_files = self.get_files_by_extension('.json.gz', files_directory)

        for filepath in zipped_files:

            with gzip.open(filepath, 'rb') as extract_file, \
                 open(filepath.replace('.gz', ''), 'wb') as outfile:

                    shutil.copyfileobj(extract_file, outfile, length=65536)

            os.remove(filepath)


    def rowify_json_files(self, files_directory):

        json_files = self.get_files_by_extension('.json', files_directory)

        for filepath in json_files:

            with open(filepath) as infile:

                json_list = json.load(infile)

            with open(filepath.replace('.json', '_rowified.json'), 'w') as outfile:

                for line in json_list:

                    outfile.write("%s\n" % json.dumps(line))

            os.remove(filepath)
