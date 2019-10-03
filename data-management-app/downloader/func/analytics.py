
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




    iframe_mapper = {
        'entries': {'number': 6},
        'treatments': {'number': 7},
        'demographics': {'number': 8}
    }

    for dashboard, params in iframe_mapper.items():
        payload = {
            "resource": {"dashboard": params['number']},
            "params": {
            }
        }
        token = jwt.encode(payload, os.environ['METABASE_SECRET_KEY'], "HS256")
        params['url'] = os.environ['METABASE_URL'] + "/embed/dashboard/" + token.decode("utf8") + "#theme=night&bordered=false&titled=false"

    return iframe_mapper


def dashboard_mapper():

    mapper = os.environ['METABASE_DASHBOARD_ID']

    if current_user.allowed_projects == 1:

        return {
            'entries': {'number': 6},
            'treatments': {'number': 7},
            'demographics': {'number': 8}
        }

    elif current_user.allowed_projects == 2:

        return {
            'entries': {'number': 6},
            'treatments': {'number': 7},
            'demographics': {'number': 8}
        }

    elif current_user.allowed_projects == 3:

        return {
            'entries': {'number': 6},
            'treatments': {'number': 7},
            'demographics': {'number': 8}
        }