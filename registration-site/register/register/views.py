from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.conf import settings
import logging
import requests
from .models import OpenHumansMember
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

# Set up logging.
logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def oh_code_to_member(code):
    """
    Exchange code for token, use this to create and return OpenHumansMember.
    If a matching OpenHumansMember already exists in db, update and return it.
    """
    logger.debug('Running oh_code_to_member with code {}...'.format(code))
    if settings.OPENHUMANS_CLIENT_SECRET and settings.OPENHUMANS_CLIENT_ID and code:
        data = {
            'grant_type': 'authorization_code',
            'redirect_uri': '{}/complete'.format(settings.OPENHUMANS_APP_BASE_URL),
            'code': code,
        }
        logger.debug(data)
        req = requests.post(
            '{}/oauth2/token/'.format(settings.OPENHUMANS_OH_BASE_URL),
            data=data,
            auth=(settings.OPENHUMANS_CLIENT_ID, settings.OPENHUMANS_CLIENT_SECRET)
        )

        data = req.json()
        if 'access_token' in data:
            logger.debug('Token exchange successful.')
            oh_id = oh_get_member_data(
                data['access_token'])['project_member_id']
            try:
                oh_member = OpenHumansMember.objects.get(oh_id=oh_id)
                logger.debug('Member {} re-authorized.'.format(oh_id))
                oh_member.access_token = data['access_token']
                oh_member.refresh_token = data['refresh_token']
                oh_member.token_expires = OpenHumansMember.get_expiration(
                    data['expires_in'])
            except:  # OpenHumansMember.DoesNotExist:
                oh_member = OpenHumansMember.create(
                    oh_id=oh_id,
                    access_token=data['access_token'],
                    refresh_token=data['refresh_token'],
                    expires_in=data['expires_in'])
                logger.debug('Member {} created.'.format(oh_id))
            oh_member.save()

            return oh_member
        elif 'error' in req.json():
            logger.debug('Error in token exchange: {}'.format(req.json()))
        else:
            logger.warning('Neither token nor error info in OH response!')
    else:
        logger.error('OH_CLIENT_SECRET or code are unavailable')
    return None


def complete(request):
    """
    Receive user from Open Humans. Make account / log in, return to main page.
    """
    # Exchange code for token.
    # This creates an OpenHumansMember and associated User account.

    code = request.GET.get('code', '')
    oh_member = oh_code_to_member(code=code)

    if oh_member:

        # Log in the user.
        user = oh_member.user
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Redirect user to home.
        messages.success(request, 'Connected to Open Humans')
        # xfer_to_open_humans.delay(oh_id=oh_member.oh_id)
        # context = {'oh_id': oh_member.oh_id,
        #            'oh_proj_page': settings.OH_ACTIVITY_PAGE}
        # return render(request, 'oh_data_source/complete.html',
        #               context=context)

    else:
        messages.error(request, 'Invalid code exchange! Connection to Open Humans NOT established.')

    return redirect('home')


def oh_get_member_data(token):
    """
    Exchange OAuth2 token for member data.
    """
    req = requests.get(
        '{}/api/direct-sharing/project/exchange-member/'.format(settings.OPENHUMANS_OH_BASE_URL),
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
               'oh_proj_page': settings.OPENHUMANS_PROJECT_ADDRESS}

    if request.user.is_authenticated:
        context.update({
            'oh_data': oh_get_member_data(
                request.user.openhumansmember.get_access_token())
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
