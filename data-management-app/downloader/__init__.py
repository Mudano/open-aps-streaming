
from apscheduler.schedulers.background import BackgroundScheduler
from utils.slack_publisher import SlackPublisher
from utils.logger import Logger
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask import Flask
import traceback
import sys
import os

logger = Logger()

logger.debug('INIT - Starting initialision.')
try:
    app = Flask(__name__)
    logger.debug('INIT - Flask app initialised.')
    app.config['SECRET_KEY'] = os.environ['DOWNLOADER_SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DOWNLOADER_POSTGRES_CON']
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SQLALCHEMY_POOL_SIZE'] = 20
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = os.environ['DOWNLOADER_APP_EMAIL']
    app.config["MAIL_PASSWORD"] = os.environ['DOWNLOADER_EMAIL_PASSWORD']

    db = SQLAlchemy(app)
    logger.debug('INIT - SQLAlchemy initialised.')

    bcrypt = Bcrypt(app)
    logger.debug('INIT - Bcrypt initialised.')

    mail = Mail()
    mail.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    logger.debug('INIT - Flask Login initialised.')

    SLACK_NOTIFICATION_CHANNEL = 'laurie_app_testing'
    APP_PUBLIC_URL = 'https://127.0.0.1:9999'
    APP_DIRECTORY_PATH = 'C:/Users/Laurie Bamber/Work/openaps/openaps/src/apps/downloader'
    DOWNLOAD_DAYS_CUTOFF = 180

    from downloader.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    from downloader import routes


    from downloader.functions import remove_temporary_files
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=remove_temporary_files, trigger='interval', minutes=10)
    scheduler.start()


    logger.debug('INIT - Finished initialision.')

except Exception:
    logger.error('Error occurred during initialisation: ' + traceback.format_exc())
    sys.exit(1)
