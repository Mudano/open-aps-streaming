

from downloader.exception import NotProcessedError, AlreadyExistsError
from downloader.func.site import send_message, generate_code
from downloader.models import RegApplication
from downloader import db, APP_PUBLIC_URL
from downloader.models import User
import datetime



def process_admin_request(request):

    """
    :param request: One of the forms from the app/admin.html template.
                    This function is used to determine which form is submitted,
                    and to then direct to a sub-function.
    """

    if 'add-user' in request.form:

        process_adding_user(request.form['add-user'])

        return 'User added successfully, a verification link has been sent to their email.'

    elif 'deactivate-user' in request.form:

        user = User.query.filter_by(id=request.form.get('deactivate-user')).first()
        user.deactivated = True
        user.deactivated_date = datetime.datetime.now()

        db.session.commit()

        return 'User deactivated successfully.'

    elif 'application-email' in request.form:

        update_application(request)

        if request.form['application-action'] == 'approve':

            process_adding_user(request.form['application-email'])

        return 'Action processed successfully, the user has been notified.'


def update_application(request):

    """
    Called when an admin approves/rejects a request for access application.
        1. Mark the application as processed
        2. Set the granted status based on the form response
        3. Notify user if they are rejected

    """

    record = RegApplication.query.filter_by(email=request.form['application-email']).first()

    record.application_processed = True
    record.application_granted = False if request.form['application-action'] == 'reject' else True
    record.processed_date = datetime.datetime.now()
    db.session.commit()

    if not record.application_granted:

        send_message(subject='OpenAPS Access Refused',
                     email=request.form['application-email'],
                     content=f"""Your application for access to the OpenAPS data portal was rejected for the following reason:
                                 <br><br>
                                 '{request.form['reject-reason']}'""")


def process_adding_user(email):

    """
    :param email: The email address of the user to be added

    Called when a new user is to be created, or when a deactivated/unverified user re-applies.

        1. generate a temporary verification code
        2. determine if user exists

             - if the user exists, is verifed, and is not deactivated, raise an already exists error
             - if the user exists but is not verified or is deactivated, restart verification process
             - if an application already exists for the user and is not processed, raise not processed error
             - if the user does not exist and no/processed application is detected, create a new user in the app_users table, start verification process

        3. If an error has not been raised, notify the user with a verification email

    """

    temp_code = generate_code()

    user = User.query.filter_by(email=email).first()
    reg = RegApplication.query.filter_by(email=email).first()

    if user and (not user.deactivated and user.verified):

        raise AlreadyExistsError('The user you are attempting to add already has an active account.')

    elif user:

        user.verified = False
        user.verification_code = temp_code
        user.hashed_pw = None
        user.deactivated = False
        user.deactivated_date = None

        db.session.commit()

    elif reg and not reg.application_processed:

        raise NotProcessedError('An outstanding application exists for this user in the application section.')

    else:
        new_user = User(
            email=email.lower(),
            verified=False,
            verification_code=temp_code,
            admin=False,
            login_count=0,
            num_downloads=0,
            total_download_size_mb=0,
            deactivated=False,
            created_ts=datetime.datetime.now()
        )
        db.session.add(new_user)
        db.session.commit()

    send_message(
        subject='OpenAPS Account Invitation',
        email=email,
        content= \
            f"""Hey there,<!--
               --><br><!--
               -->you've been invited to join the OpenAPS Data Portal! Click the link below to go to the verification page, and enter the following verification code to activate your account:<!--
               --><br><br><!--
               --><b>{temp_code}</b><!--
               --><br><!--
               --><a href="{APP_PUBLIC_URL + '/verify'}">{APP_PUBLIC_URL + '/verify'}</a>"""
    )
