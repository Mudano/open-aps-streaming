from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
import logging
import requests
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

# Set up logging.
logger = logging.getLogger(__name__)


def oh_get_member_data(token):
    """
    Exchange OAuth2 token for member data.
    """
    req = requests.get(
        f'{settings.OPENHUMANS_OH_BASE_URL}/api/direct-sharing/project/exchange-member/',
        params={'access_token': token})
    if req.status_code == 200:
        return req.json()
    else:
        raise Exception(f'Status code {req.status_code}')


def home(request):
    """
    Starting page for app.
    """
    logger.debug(f'Loading index. User authenticated: {request.user.is_authenticated}')

    context = {
        'client_id': settings.OPENHUMANS_CLIENT_ID,
        'oh_proj_page': settings.OPENHUMANS_PROJECT_ADDRESS
    }

    if request.user.is_authenticated:
        context.update({
            'oh_data': oh_get_member_data(request.user.openhumansmember.get_access_token())
        })

    return render(request, 'register/index.html', context=context)


@login_required
@require_http_methods(['POST'])
def transfer(request):
    return redirect('home')


@login_required
@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return redirect('home')
