

from downloader.exception import LoginError, NotFoundError, AlreadyExistsError, PermissionsError, VerifyError, MailError
from downloader import APP_PUBLIC_URL, app, db, logger, ADMIN_EMAIL, bcrypt
from downloader.models import User, RegApplication
from flask_login import login_user
from flask_mail import Message
from downloader import mail
import traceback
import datetime
import random
import string



def send_message(subject, email, content):

    try:
        message = Message(subject=subject,
                          sender=app.config.get('MAIL_USERNAME'),
                          recipients=[email])
        message.html = content
        mail.send(message)

    except Exception:
        raise MailError(f'Error occurred while sending message: {traceback.format_exc()}')



def process_user_login(request):

    """
    :param request: contains email and pw submitted in login form

    1. Find user
    2. Check conditions: user exists, user is verified, user not deactivated, user pw matches db pw
    3. Login if true, raise error if any conditions fail
    """

    email = request.form['login-email']
    pw = request.form['login-password']

    user = User.query.filter_by(email=email).first()

    if user:
        if user.verified:
            if not user.deactivated:
                if bcrypt.check_password_hash(user.hashed_pw, pw):

                    login_user(user)

                    user.login_count = user.login_count + 1
                    user.last_signin = datetime.datetime.now()
                    db.session.commit()

                    logger.debug(f'LOGIN - login completed successfully for email {email}.')

                else:
                    raise LoginError('Sorry, that password was incorrect.')
            else:
                raise LoginError('Sorry, your user account has been deactivated, please register again to regain access.')
        else:
            raise LoginError('Sorry, your user account has not yet been verified, please check your email for your verification link.')
    else:

        reg = RegApplication.query.filter(RegApplication.email == email)\
                                  .filter(RegApplication.application_processed != True).first()
        if reg:
            raise LoginError('Your registration application has not yet been processed. Please wait for an admin to verify your application.')
        else:
            raise LoginError('Sorry, that email was not recognized.')



def reset_user_password(email):

    temp_code = generate_code()
    user = User.query.filter_by(email=email).first()

    if not user:
        raise NotFoundError('No account was found for the email you provided.')
    elif user.admin:
        raise PermissionsError('Admin passwords can only be changed manually within the database.')

    user.verification_code = temp_code
    db.session.commit()

    send_message(
        subject='OpenAPS Password Reset',
        email=email,
        content=\
        f"""Hey there,<!--
           --><br><!--
           -->a password reset link was requested for your account on the OpenAPS Portal. Click the link below to go to the verification page, and enter the following verification code to reset your password:<!--
           --><br><br><!--
           --><b>Code: {temp_code}</b><!--
           --><br><!--
           --><a href="{APP_PUBLIC_URL + '/verify'}">Link: {APP_PUBLIC_URL + '/verify'}</a>"""
    )



def create_registration_record(request):

    """
    :param request: contains the application form submitted by user

    1. If user already exists and is not verified/is deactivated, delete user
    2. If a registration record already exists, delete it
    3. Create new registration record filled with form responses
    4. Send message to site admin with the form responses
    """

    user = User.query.filter_by(email=request.form['register-email']).first()
    reg = RegApplication.query.filter_by(email=request.form['register-email']).first()

    if user and (user.deactivated or not user.verified):

        User.query.filter_by(email=request.form['register-email']).delete()

    elif user:
        raise AlreadyExistsError('An active account already exists with the specified email.')

    if reg:
        RegApplication.query.filter_by(email=request.form['register-email']).delete()

    try:
        new_application = RegApplication(
            researcher_name=request.form['register-name'],
            email=request.form['register-email'],
            phone_number=request.form['register-phone'],
            irb_approval=request.form['register-irb'],
            sponsor_organisation=request.form['register-sponsor'],
            request_description=request.form['register-textarea'],
            application_processed=False,
            inserted_ts=datetime.datetime.now()
        )
    except Exception:
        raise ValueError('A field value was specified incorrectly in your application, please try again.')

    db.session.add(new_application)
    db.session.commit()

    send_message(
        subject='New User Application',
        email=ADMIN_EMAIL,
        content=f"""Hey there,<!--
           --><br><!--
           -->a new user has requested access to the OpenAPS data portal:<!--
           --><br><br><!--
           --><b>Name</b><!--
           --><br>{new_application.researcher_name}<!--
           --><br><br><!--
           --><b>Email</b><!--
           --><br>{new_application.email}<!--
           --><br><br><!--
           --><b>Phone</b><!--
           --><br>{new_application.phone_number}<!--
           --><br><br><!--
           --><b>IRB Approval</b><!--
           --><br>{new_application.irb_approval}<!--
           --><br><br><!--
           --><b>Sponsor</b><!--
           --><br>{new_application.sponsor_organisation}<!--
           --><br><br><!--
           --><b>Application Description</b><!--
           --><br>{new_application.request_description}<!--
           --><br><br><br><!--
           -->Proceed to the following URL to accept/decline this application:<br><!--
           --><a href="{APP_PUBLIC_URL + '/admin'}">{APP_PUBLIC_URL + '/admin#applications'}</a>"""
    )



def verify_user(request):

    """
    Note: this form is used to reset a users password, as well as just verify new users

    :param request: contains user email, verification code, password and password confirm

    1. Find user
    2. Check conditions: user exists, user is not verified or user already has a password, users code matches code in db, users passwords match
    3. Mark user as verified and set their password

    """

    email = request.form['verify-email']
    code = request.form['verification-code']
    pword = bcrypt.generate_password_hash(request.form['new-password']).decode('utf-8')
    pword_conf = request.form['confirm-password']

    user = User.query.filter_by(email=email).first()

    if user:
        if not user.verified or user.hashed_pw:
            if user.verification_code == code:
                if bcrypt.check_password_hash(pword, pword_conf):

                    user.verified = True
                    user.verification_code = None
                    user.hashed_pw = pword

                    db.session.commit()

                else:
                    raise VerifyError('Your passwords did not match.')
            else:
                raise VerifyError('Your verification code was incorrect.')
        else:
            raise VerifyError('Your account has already been verified.')
    else:
        raise NotFoundError('No account was found for the specified email.')


def generate_code():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9))
