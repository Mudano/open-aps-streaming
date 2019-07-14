
import jwt
import os


def retrieve_iframes():

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
