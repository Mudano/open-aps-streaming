
from downloader.models import Entry, Treatment, Profile, Device
from downloader import db, APP_DIRECTORY_PATH
from downloader.exception import DownloadError
from flask_login import current_user
import pandas as pd
import traceback
import datetime
import json
import os


ENTITY_MAPPER = {
    'entries': {'date_col': 'date', 'class': Entry},
    'treatments': {'date_col': 'created_at', 'class': Treatment},
    'device': {'date_col': 'created_at', 'class': Device},
    'profiles': {'date_col': 'created_at', 'class': Profile}
}


def create_download_file(request):

    if request.form['filetype'] == 'json':
        filetype = 'json'
    elif request.form['filetype'] == 'excel' and request.form['entity'] == 'all':
        filetype = 'xlsx'
    else:
        filetype = 'csv'

    entity = request.form['entity'].split(' ')[0]
    start_date = request.form['date-range'].split(' to ')[0].split(' ')[0]
    end_date = request.form['date-range'].split(' to ')[1].split(' ')[0]

    outfile = f'{APP_DIRECTORY_PATH}/temp_files/{entity}_{start_date}_{end_date}.{filetype}'

    try:
        results = _extract_results(get_entity_records(entity, start_date, end_date))
        generate_outfile(results, outfile)

    except Exception:
        raise DownloadError(traceback.format_exc())

    current_user.total_download_size_mb = current_user.total_download_size_mb + (os.path.getsize(outfile) / (1024 * 1024.0))
    current_user.num_downloads = current_user.num_downloads + 1
    db.session.commit()

    return outfile


def get_entity_records(entity, start_date, end_date):

    outlist = []
    for k, v in ENTITY_MAPPER.items():

        if k == entity or entity == 'all':

            records = v['class'].query.filter(v['class'].__getattribute__(v['date_col']) >= start_date)\
                                      .filter(v['class'].__getattribute__(v['date_col']) <= end_date).all()
            outlist.append(records)

    return outlist


def _extract_results(results, entity):

    outlist = []
    if entity == 'all':

        for res in results:

            pass

    return outlist


def generate_outfile(outlist, outfile):

    if 'all' in outfile:

        if 'json' in outfile:

            with open(outfile, 'w') as t:

                t.write(json.dumps())

        else:
            writer = pd.ExcelWriter(outfile, engine='xlsxwriter')

            for (entity, k) in (outlist, ENTITY_MAPPER.keys()):

                df = pd.DataFrame(entity)
                df.to_excel(writer, k)

            writer.save()

    else:
        df = pd.DataFrame(outlist)

        if 'json' in outfile:

            df.to_json(outfile)

        else:
            df.to_csv(outfile)










def remove_temporary_files():

    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=10)
    directory = f'{APP_DIRECTORY_PATH}/temp_files/'

    for filename in os.listdir(directory):

        modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(directory + filename))

        if modified_time < cutoff and '.json' in filename:
            os.remove(directory + filename)
