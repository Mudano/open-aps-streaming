
import requests
import json
import os

SLACK_URL_POSTMESSAGE = 'https://slack.com/api/chat.postMessage'


class SlackPublisher:
    def __init__(self, api_key=None, env_key=None, webhook=None):


        if api_key:
            self.SLACK_API_KEY = api_key

        if env_key:
            if env_key in os.environ:
                self.SLACK_API_KEY = os.environ.get(env_key)
            else:
                print('Unable to identify key in environment variables.')

        if webhook:
            self.WEBHOOK = webhook

    def post_to_slack(self, channel=None, content={}):

        payload = {
            'token': self.SLACK_API_KEY,
            'channel': channel,
            'text': content.get('text', ''),
            'attachments': json.dumps(content.get('attachments', []))
        }

        resp = requests.post(url=SLACK_URL_POSTMESSAGE, data=payload, timeout=1).json()

        return resp
