from datetime import datetime
import psycopg2
from .scheduler import postgres_connection_string
from .oh_user import OhUser
from .nightscout_site import NightscoutSite
import requests
from ohapi.api import oauth2_token_exchange
import os

CLIENT_ID = os.getenv('OPEN_HUMANS_CLIENT_ID')
CLIENT_SECRET = os.getenv('OPEN_HUMANS_CLIENT_SECRET')


def nightscout_ingest_job():
    print(f'schedule test running at {datetime.now()}')

    # pull tokens from database
    users = OhUser.get_all_users()

    # for each user
    for user in users:
        print(user)

        # Refresh tokens against OH
        user.refresh_oh_token(CLIENT_ID, CLIENT_SECRET)

        # pull the nightscout URL file from OH
        nightscout_url = user.fetch_ns_url()
        last_recorded_at = user.fetch_last_recorded_at()

        # any failure to fetch either url or last recorded files will result in no transfer, handled below
        if nightscout_url and last_recorded_at:
            nightscout_site = NightscoutSite(nightscout_url)
            print(nightscout_site)
            print(last_recorded_at)

            # pull the users nightscout data from this URL



        ## push this data to OH





