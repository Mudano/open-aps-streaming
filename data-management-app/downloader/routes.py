
from downloader.exception import *

from downloader.func.site import process_user_login, reset_user_password, create_registration_record, verify_user
from downloader.func.downloader import create_download_file
from downloader.func.admin import process_admin_request
from downloader.func.analytics import retrieve_iframes

from flask_login import current_user, login_required, logout_user
from flask import session, redirect, url_for, request
from downloader.models import User, RegApplication
from flask import render_template, send_file
from downloader import app, logger
import traceback



@app.route("/login", methods=['GET', 'POST'])
def login():

    try:
        if request.method == 'POST':

            if 'login-email' in request.form:

                try:
                    process_user_login(request)
                    return redirect(url_for('main'))

                except LoginError as e:
                    session['notification'] = {'status': 'error', 'content': str(e)}
                    return redirect(url_for('login'))

            elif 'password-reset' in request.form:

                try:
                    reset_user_password(request.form['password-reset'])

                    session['notification'] = {'status': 'success', 'content': 'A reset code has been sent to your email.'}
                    return redirect(url_for('verify'))

                except (NotFoundError, PermissionsError) as e:
                    session['notification'] = {'status': 'error', 'content': str(e)}
                    return redirect(url_for('login'))

        return render_template('user/login.html', title='Login', notification=get_notification())

    except Exception:
        logger.error(f'LOGIN - ERROR OCCURRED: {str(traceback.format_exc())}')
        return 'Sorry, an error occurred. Please try again later.', 500



@app.route('/conditions', methods=['GET', 'POST'])
def register_conditions():

    try:
        if not current_user.is_authenticated:

            if request.method == 'POST':

                if request.form.get('terms-checkbox') == 'on':

                    session['register'] = True
                    return redirect(url_for('register'))

                else:
                    session['notification'] = {'status': 'error', 'content': 'You did not tick the agree to terms checkbox.'}
                    return redirect(url_for('register_conditions'))
        else:
            return redirect(url_for('main'))

        return render_template('user/guidelines.html', notification=get_notification())

    except Exception:
        logger.error(f'CONDITIONS - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Error occurred, please try again later.'}
        return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():

    try:
        if not current_user.is_authenticated:

            if 'register' in session and session['register']:

                if request.method == 'POST':

                    session['register'] = False

                    try:
                        create_registration_record(request)

                        session['notification'] = {'status': 'success', 'content': 'Your application has been submitted. Please wait for approval from an OpenAPS admin, which you will be notified of via your provided email.'}

                    except (AlreadyExistsError, ValueError) as e:
                        session['notification'] = {'status': 'error', 'content': str(e)}

                    return redirect(url_for('login'))

                return render_template('user/register.html', notification=get_notification())

            else:
                return redirect(url_for('register_conditions'))
        else:
            return redirect(url_for('main'))

    except Exception:
        logger.error(f'REGISTER - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Error occurred, please try again later.'}
        return redirect(url_for('login'))



@app.route('/verify', methods=['GET', 'POST'])
def verify():

    try:
        if request.method == 'POST':

            try:
                verify_user(request)

                session['notification'] = {'status': 'success', 'content': 'Account verified successfully.'}

            except (NotFoundError, VerifyError) as e:
                session['notification'] = {'status': 'error', 'content': str(e)}

            return redirect(url_for('login'))

        return render_template('user/verify.html', notification=get_notification())

    except Exception:
        logger.error(f'VERIFY - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Error occurred, please try again later.'}
        return redirect(url_for('login'))



@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():

    try:
        if current_user.admin:

            users = User.query.filter(User.deactivated != True).all()
            applications = RegApplication.query.filter(RegApplication.application_processed != True).all()

            if request.method == 'POST':

                try:
                    returned_message = process_admin_request(request)
                    session['notification'] = {'status': 'success', 'content': returned_message}

                except (AlreadyExistsError, NotProcessedError) as e:
                    session['notification'] = {'status': 'error', 'content': str(e)}

                return redirect(url_for('admin'))

        else:
            session['notification'] = {'status': 'error', 'content': 'You do not have the necessary permissions to view this page.'}
            return redirect(url_for('main'))

        return render_template('app/admin.html', users=users, applications=applications, notification=get_notification())

    except Exception:
        logger.error(f'ADMIN - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Error occurred, please try again later.'}
        return redirect(url_for('main'))



@app.route('/', methods=['GET'])
@app.route('/main', methods=['GET'])
@login_required
def main():

    try:
        return render_template('user/main.html', notification=get_notification())

    except Exception:
        logger.error(f'MAIN - Error occurred: {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Error occurred, please try again later.'}
        return redirect(url_for('login'))



@app.route('/downloader', methods=['GET', 'POST'])
@login_required
def downloader():

    try:
        if request.method == 'POST':

            try:
                file_location = create_download_file(request)

            except DownloadError:
                session['notification'] = {'status': 'error', 'content': 'Sorry, an error occurred. If you were trying to download a large date-range or all entities, try narrowing your search.'}
                logger.error(f'DOWNLOADER - {str(traceback.format_exc())}')
                return redirect(url_for('downloader'))

            return send_file(file_location, as_attachment=True)

        return render_template('app/downloader.html', notification=get_notification())

    except Exception:
        logger.error(f'DOWNLOADER - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Error occurred, please try again later.'}
        return redirect(url_for('main'))



@app.route('/analytics', methods=['GET'])
@login_required
def analytics():

    try:
        iframe_mapper = retrieve_iframes()
        return render_template('app/analytics.html', iframe_mapper=iframe_mapper, notification=get_notification())

    except Exception:
        logger.error(f'ANALYTICS - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Error occurred, please try again later.'}
        return redirect(url_for('main'))



@app.route("/logout", methods=['GET'])
@login_required
def logout():

    try:
        if current_user.is_authenticated:

            logout_user()
            return redirect(url_for('login'))

    except Exception:
        logger.error(f'LOGOUT - {str(traceback.format_exc())}')
        session['notification'] = {'status': 'error', 'content': 'Error occurred, please try again later.'}
        return redirect(url_for('login'))


def get_notification():

    notification = session['notification'] if 'notification' in session else None
    session['notification'] = None
    return notification
