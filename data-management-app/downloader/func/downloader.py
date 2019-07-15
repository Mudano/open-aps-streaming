
from downloader.models import Entry, Treatment, Profile, Device
from downloader.exception import DownloadError
from downloader import APP_DIRECTORY_PATH, db
from flask_login import current_user
import pandas as pd
import traceback
import datetime
import zipfile
import os


OUTFILE_DIR = f'C:/Users/Laurie Bamber/Work/open-aps-streaming/data-management-app/downloader/temp_files'
ENTITY_MAPPER = {
    'entries': {'date_col': 'date', 'class': Entry},
    'treatments': {'date_col': 'created_at', 'class': Treatment},
    'device': {'date_col': 'created_at', 'class': Device},
    'profiles': {'date_col': 'created_at', 'class': Profile}
}


def create_download_file(request):

    filetype = request.form['filetype'].split(' ')[0]
    entity = request.form['entity'].split(' ')[0]
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

    for k, v in ENTITY_MAPPER.items():

        if k == entity or entity == 'all':

            outfile = f'{k}_{start_date}_{end_date}.{filetype}'

            records = [x.raw_json for x in v['class'].query.filter(getattr(v['class'], v['date_col']) >= start_date)\
                                                           .filter(getattr(v['class'], v['date_col']) <= end_date)\
                                                           .filter(v['class'].raw_json != None).all()]

            df = pd.DataFrame(records)

            if filetype == 'json':

                zip_folder.writestr(outfile, df.to_json(orient='table', index=False, compression='gzip'))

            else:
                zip_folder.writestr(outfile, df.to_csv(index=False, compression='gzip'))





def remove_temporary_files():

    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=40)
    directory = f'{APP_DIRECTORY_PATH}/temp_files/'

    for filename in os.listdir(directory):

        modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(directory + filename))

        if modified_time < cutoff and '.json' in filename:
            os.remove(directory + filename)
