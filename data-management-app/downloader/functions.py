
from downloader import APP_PUBLIC_URL, APP_DIRECTORY_PATH, app, db, logger
from downloader.models import User
from flask_login import current_user
from downloader import mail
from flask_mail import Message
import pandas as pd
import datetime
import os


class NotFoundError(Exception):
    pass


def send_message(subject, email, content):

    message = Message(subject=subject,
                      sender=app.config.get('MAIL_USERNAME'),
                      recipients=[email])

    message.html = content
    mail.send(message)

    logger.debug(f'SEND MESSAGE - Mail message sent to user {email}.')


def reset_user_password(email, temp_code):

    user = User.query.filter_by(email=email).first()

    if not user:
        raise NotFoundError

    user.verified = False
    user.verification_code = temp_code
    db.session.commit()

    logger.debug(f'PASSWORD RESET - About to send message to user {email}.')

    send_message(
        subject='OpenAPS Password Reset',
        email=email,
        content=\
        f"""Hey there,<!--
           --><br><!--
           -->a password reset link was requested for your account on the OpenAPS Portal. Click the link below to go to the verification page, and enter the following verification code to reset your password:<!--
           --><br><br><!--
           --><b>{temp_code}</b><!--
           --><br><!--
           --><a href="{APP_PUBLIC_URL + '/verify'}">{APP_PUBLIC_URL + '/verify'}</a>"""
    )


def create_new_user(email, temp_code):

    new_user = User(
        email=email,
        verified=False,
        verification_code=temp_code,
        admin=False,
        login_count=0,
        num_downloads=0,
        total_download_size_mb=0,
        created_ts=datetime.datetime.now()
    )
    db.session.add(new_user)
    db.session.commit()

    logger.debug(f'CREATE USER - About to send message to user {email}.')

    send_message(
        subject='OpenAPS Account Invitation',
        email=email,
        content=\
        f"""Hey there,<!--
           --><br><!--
           -->you've been invited to join the OpenAPS Data Portal! Click the link below to go to the verification page, and enter the following verification code to activate your account:<!--
           --><br><br><!--
           --><b>{temp_code}</b><!--
           --><br><!--
           --><a href="{APP_PUBLIC_URL + '/verify'}">{APP_PUBLIC_URL + '/verify'}</a>"""
    )


def create_download_file(request):

    filetype = request.form['filetype']
    entity = request.form['entity'].split(' ')[0]
    start_date = request.form['date-range'].split(' to ')[0].split(' ')[0]
    end_date = request.form['date-range'].split(' to ')[1].split(' ')[0]

    outfile = f'{APP_DIRECTORY_PATH}/temp_files/{entity}_{start_date}_{end_date}.{filetype}'

    tmap = {
        'entries': {'date_col': 'date'},
        'treatments': {'date_col': 'created_at'},
        'device_status': {'date_col': 'created_at'}
    }

    res = db.engine.execute(f"""
            SELECT      * 
            FROM        openaps.%s base
            {'INNER JOIN openaps.device_status_metrics met ON base.id = met.device_status_id' if entity == 'device_status' else ""}
            WHERE       %s::DATE > '%s'::DATE 
            AND         %s::DATE < '%s'::DATE 
            ORDER BY %s
        """ % (entity, tmap[entity]['date_col'], start_date, tmap[entity]['date_col'], end_date, tmap[entity]['date_col'])).fetchall()

    if res:

        df = pd.DataFrame(res, columns=res[0].keys())

        if filetype == 'csv':

            df.to_csv(outfile, index=False)

        elif filetype == 'json':

            df.to_json(outfile, index=False, orient='table')

    else:
        raise NotFoundError

    return outfile


def remove_temporary_files():

    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=10)
    directory = f'{APP_DIRECTORY_PATH}/temp_files/'

    for filename in os.listdir(directory):

        modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(directory + filename))

        if modified_time < cutoff:
            os.remove(directory + filename)
