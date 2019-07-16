
import traceback
import shutil
import ohapi
import gzip
import sys
import os


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
            print(traceback)
            sys.exit(1)

    def get_member_list(self):

        return self.OHProject.project_data

    @staticmethod
    def extract_directory_files(directory):

        zipped_files = []

        for subdir, dirs, files in os.walk(directory):

            for file in files:

                if '.json.gz' in file and file not in zipped_files:

                    zipped_files.append(f'{subdir}/{file}'.replace('\\', '/'))

        for filepath in zipped_files:

            with gzip.open(filepath, 'rb') as extract_file, \
                 open(filepath.replace('.gz', ''), 'wb') as outfile:

                    shutil.copyfileobj(extract_file, outfile, length=65536)
            os.remove(filepath)
