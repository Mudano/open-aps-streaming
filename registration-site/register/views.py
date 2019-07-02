from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import logging
import requests

# Set up logging.
logger = logging.getLogger(__name__)

from .settings import OPENHUMANS_APP_BASE_URL

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def oh_get_member_data(token):
    """
    Exchange OAuth2 token for member data.
    """
    req = requests.get(
        '{}/api/direct-sharing/project/exchange-member/'.format(OPENHUMANS_APP_BASE_URL),
        params={'access_token': token})
    if req.status_code == 200:
        return req.json()
    else:
        raise Exception('Status code {}'.format(req.status_code))



def home(request):
    """
    Starting page for app.
    """
    logger.debug('Loading index. User authenticated: {}'.format(
        request.user.is_authenticated))

    context = {'client_id': settings.OPENHUMANS_CLIENT_ID,
               'oh_proj_page': 'temp activity page'}

    if request.user.is_authenticated:
        context.update({
            'oh_data': oh_get_member_data(
                request.user.openhumansmember.get_access_token())
        })

    return render(request, 'register/index.html', context=context)
