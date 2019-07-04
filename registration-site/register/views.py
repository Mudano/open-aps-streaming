from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
import logging
import requests
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import io

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
        logger.debug(f'OH member data fetched: {req.json()}')
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
        users_file_info = [f for f
                           in request.user.openhumansmember.list_files()
                           if f['basename'].endswith('open_aps_nightscout_url.txt')]

        context.update({
            'ns_url_files': users_file_info,
            'ns_url_file_count': len(users_file_info)
        })

    return render(request, 'register/index.html', context=context)


@login_required
@require_http_methods(['POST'])
def transfer(request):
    oh_member = request.user.openhumansmember
    ns_url = request.POST['nightscoutURL']
    logger.debug(f"Pushing NS URL '{ns_url}' to OH Member {oh_member.oh_id}")

    ns_url_file_description = f"Your Nightscout URL, uploaded by {settings.OPENHUMANS_PROJECT_ADDRESS}"
    ns_url_file_tags = ["open-aps", "Nightscout", "url"]
    ns_url_file_metadata = {"tags": ns_url_file_tags, "description": ns_url_file_description}
    ns_url_filename = f'{oh_member.oh_id}_open_aps_nightscout_url.txt'

    users_current_files = [f['basename'] for f in oh_member.list_files()]

    if ns_url_filename in users_current_files:
        logger.debug('Found an existing Nightscout URL file(s) for user. Deleting these before upload.')
        oh_member.delete_single_file(file_basename=ns_url_filename)  # this deletes all files with the name

    with io.StringIO(ns_url) as s:
        oh_member.upload(s, ns_url_filename, ns_url_file_metadata)

    return redirect('home')


@login_required
@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return redirect('home')
