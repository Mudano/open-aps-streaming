
from utils.slack_publisher import SlackPublisher
import datetime
import logging
import sys
import os


class Logger(object):

    def __init__(self, error_channel='openaps-errors', path=None, name='logger', level=logging.DEBUG, file_name_format='%Y-%m-%d-%H-%M-%S', delimiter='~'):

        self.slacker = SlackPublisher(api_key=os.environ['DOWNLOADER_SLACK_KEY'])
        self.error_channel = error_channel

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = logging.Formatter('%(asctime)s ' + delimiter + ' %(module)s ' + delimiter + ' %(lineno)d ' + delimiter + ' %(levelname)s ' + delimiter + ' %(message)s ')
        stream_formatter = logging.Formatter('%(message)s')
        if path:

            logs_dir_path = path
            if not os.path.exists(logs_dir_path):
                os.makedirs(logs_dir_path)

            if file_name_format:
                dt = datetime.datetime.today().strftime(file_name_format)
            else:
                dt = datetime.datetime.today().strftime('%Y%m%d%H%M%S')

            logfile = os.path.join(logs_dir_path, dt + '.log')

            fh = logging.FileHandler(logfile)
            fh.setFormatter(formatter)

            self.logger.addHandler(fh)

        else:
            sh = logging.StreamHandler()
            sh.setFormatter(stream_formatter)
            self.logger.addHandler(sh)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.slacker.post_to_slack(channel=self.error_channel,
                                   content={'text': msg})
        self.logger.error(msg)

    def exit(self, msg):
        self.logger.debug(msg)
        sys.exit(0)

    def db_exit(self, db, msg):
        self.logger.debug(msg)
        db.close()
        sys.exit(0)
