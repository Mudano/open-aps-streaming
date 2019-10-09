
from downloader.models import Entry, Treatment, Profile, Device
from downloader.exception import DownloadError
from downloader import APP_DIRECTORY_PATH, db
from flask_login import current_user
from pandas.io.json import json_normalize
from dateutil.parser import parse
import traceback
import datetime
import zipfile
import os


OUTFILE_DIR = f'{APP_DIRECTORY_PATH}/temp_files'
ENTITY_MAPPER = {
    'entries': {'date_col': 'date', 'class': Entry},
    'treatments': {'date_col': 'created_at', 'class': Treatment},
    'device': {'date_col': 'created_at', 'class': Device},
    'profiles': {'date_col': 'created_at', 'class': Profile}
}


def create_download_file(request):

    """
    :param request: contains form from download page

        1. Run injection check to prevent SQL injection
        2. Create outfile name
        3. Open .zip file, and run sub-function to populate .zip with the csv/json file/s
        4. Update user download metrics

    :return: the path location of the created .zip file, containing the generated csv/json files
    """

    _injection_check(request)

    filetype = request.form['filetype']
    entity = request.form['entity']
    start_date = request.form['date-range'].split(' to ')[0].split(' ')[0]
    end_date = request.form['date-range'].split(' to ')[1].split(' ')[0]

    try:

        zip_file = f"{OUTFILE_DIR}/openaps_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.zip"

        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zip_folder:

            populate_files(entity, start_date, end_date, filetype, zip_folder)

    except Exception:
        raise DownloadError(traceback.format_exc())

    current_user.total_download_size_mb = current_user.total_download_size_mb + (os.path.getsize(f'{zip_file}') / (1024 * 1024.0))
    current_user.num_downloads = current_user.num_downloads + 1
    db.session.commit()

    return zip_file


def populate_files(entity, start_date, end_date, filetype, zip_folder):

    """
    :param entity: refers to tables in db, can be all, entries, treatments, profiles or device
    :param start_date: start date for records
    :param end_date: end date for records
    :param filetype: outfile type, can be csv or json
    :param zip_folder: the opened .zip folder to be written to

        1. Iterate over each table name in the mapper dict
        2. If the table name is equal to the entity chosen, or if the entity is all, continue
        3. Generate an outfile name
        4. Retrieve records from db, query in raw SQL is as follows:

            SELECT raw_json FROM openaps.<entity> WHERE <start_date> > <table_date_column>
                                                  AND <end_date> < <table_date_column>
                                                  AND raw_json IS NOT NULL

        5. Filter records based on user access, level 2 means user has access to all projects
        6. Normalize the retrieved records, turning raw_json from nested dictionary to one-dimensional object
        7. Write to the .zip file using gzip compression

    """

    for k, v in ENTITY_MAPPER.items():

        if k == entity or entity == 'all':

            outfile = f'{k}_{start_date}_{end_date}.{filetype}'

            records = [x.raw_json for x in v['class'].query\
                                                     .filter(getattr(v['class'], v['date_col']) >= start_date)\
                                                     .filter(getattr(v['class'], v['date_col']) <= end_date)\
                                                     .filter(v['class'].raw_json != None).all()]

            if current_user.allowed_projects != 2:
                records = [x for x in records if x['source_entity'] in [current_user.allowed_projects, 2]]

            df = json_normalize(records)

            if filetype == 'json':

                zip_folder.writestr(outfile, df.to_json(orient='table', index=False, compression='gzip'))

            else:
                zip_folder.writestr(outfile, df.to_csv(index=False, compression='gzip'))


def _injection_check(request):

    if request.form['filetype'] not in ['json', 'csv']:

        raise DownloadError(f"Malicious filetype parameter identified, user was {current_user.email} and value was {request.form['filetype']}")

    elif request.form['entity'] not in ['all', 'profile', 'treatments', 'entries', 'device_status']:

            raise DownloadError(f"Malicious entity parameter identified, user was {current_user.email} and value was {request.form['entity']}")

    try:
        parse(request.form['date-range'].split(' to ')[0].split(' ')[0])
        parse(request.form['date-range'].split(' to ')[1].split(' ')[0])
    except ValueError:
        raise DownloadError(f"Malicious date parameter identified, user was {current_user.email} and value was {request.form['date-range']}")


def remove_temporary_files():

    """
        Cron function used to delete processed downloads.

        1. Find all files in the downloads directory
        2. Check if the modified_time is greater than a cutoff time (40 minutes)
        3. If true, delete file

    """

    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=40)
    directory = f'{APP_DIRECTORY_PATH}/temp_files/'

    for filename in os.listdir(directory):

        modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(directory + filename))

        if modified_time < cutoff and '.json' in filename:
            os.remove(directory + filename)
