
from flask_login import current_user
import jwt
import os


def retrieve_iframes():

    """
        Called when a user visits the app/analytics.html page.

            1. Define entities and dashboard numbers

            For each entity:
                2. Get token using environ Metabase Secret Key
                3. Construct URL from token and environ Metabase URL

        :returns: A dictionary containing dashboard URL's for Metabase

    """

    from downloader.helpers import metabase_secret_key, metabase_url
    METABASE_URL = metabase_url()
    METABASE_KEY = metabase_secret_key()

    iframe_mapper = get_dashboard_mapper()

    for dashboard, params in iframe_mapper.items():

        if params['number'] == 'NA':
            params['url'] = 'none'
        else:
            payload = {
                "resource": {"dashboard": params['number']},
                "params": {
                }
            }
            token = jwt.encode(payload, METABASE_KEY, "HS256")
            params['url'] = METABASE_URL + "/embed/dashboard/" + token.decode("utf8") + "#theme=night&bordered=false&titled=false"

    return iframe_mapper


def get_dashboard_mapper():

    if current_user.allowed_projects == 0:

        return {
            'entries': {'number': 9},
            'treatments': {'number': 12},
            'demographics': {'number': 'NA'}
        }

    elif current_user.allowed_projects == 1:

        return {
            'entries': {'number': 10},
            'treatments': {'number': 11},
            'demographics': {'number': 'NA'}
        }

    elif current_user.allowed_projects == 2:

        return {
            'entries': {'number': 6},
            'treatments': {'number': 7},
            'demographics': {'number': 8}
        }

    else:
        return {
            'entries': 'NA',
            'treatments': 'NA',
            'demographics': 'NA'
        }
