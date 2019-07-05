from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import io

# Set up logging.
logger = logging.getLogger(__name__)


def home(request):
    """
    Starting page for app.
    """
    logger.debug(f'Loading index. User authenticated: {request.user.is_authenticated}')
    context = build_project_context(settings.OPENHUMANS_CLIENT_ID, settings.OPENHUMANS_PROJECT_ADDRESS)

    if request.user.is_authenticated:
        users_file_info = get_oh_members_nightscout_files(request.user.openhumansmember)
        context.update(build_file_info_context(users_file_info))
        messages.success(request, 'Connected to Open Humans')

    return render(request, 'register/index.html', context=context)


@login_required
@require_http_methods(['POST'])
def transfer(request):
    """
    The page that is hit when a Nightscout URL transfer is requested.
    """
    oh_member = request.user.openhumansmember
    ns_url = request.POST['nightscoutURL']
    logger.debug(f"Pushing NS URL '{ns_url}' to OH Member {oh_member.oh_id}")

    try:
        ns_url_file_metadata = build_ns_url_metadata(settings.OPENHUMANS_PROJECT_ADDRESS)
        ns_url_filename = f'{oh_member.oh_id}_open_aps_nightscout_url.txt'

        if ns_url_filename in get_oh_member_file_names(oh_member):
            logger.debug('Found an existing Nightscout URL file(s) for user. Deleting these before upload.')
            oh_member.delete_single_file(file_basename=ns_url_filename)  # this deletes all files with the name

        upload_successful = upload_string_file_to_oh(oh_member, ns_url, ns_url_filename, ns_url_file_metadata)
        handle_oh_upload_attempt(request, upload_successful)
    except:
        messages.error(request, 'Failed to update Nightscout URL information on Open Humans')

    return redirect('home')


@login_required
@require_http_methods(['POST'])
def logout_view(request):
    """
    The /logout endpoint. Responds to post requests by logging out the django user.
    """
    logout(request)
    return redirect('home')


def build_ns_url_metadata(oh_project_address):
    """
    Given the OH project URL returns the metadata for a Nightscout URL file.

    :param oh_project_address: The url of the OH project pushing the data
    :return: A dictionary of metadata information.
    """
    file_description = f"Your Nightscout URL, uploaded by {oh_project_address}"
    file_tags = ["open-aps", "Nightscout", "url", "text"]
    return {"tags": file_tags, "description": file_description}


def get_oh_members_nightscout_files(oh_member):
    """
    For a given Open Humans member returns the file information for any files
    in their Open Humans account that match the file name for the stored
    nightscout URL file.

    :param oh_member: An Open Humans member Django model.
    :return: A list of dictionaries containing the information for any nightscout url files.
    """
    return [f for f
            in oh_member.list_files()
            if f['basename'].endswith('open_aps_nightscout_url.txt')]


def get_oh_member_file_names(oh_member):
    """
    For a given Open Humans member, returns the file names for all files
    in their Open Humans account.

    :param oh_member: An Open Humans member Django model.
    :return: A list of filenames (strings).
    """
    return [f['basename'] for f in oh_member.list_files()]


def build_project_context(client_id, project_address):
    """
    Takes the values of the application's basic homepage context an formats them into a dictionary.

    :param client_id: The application's Open Humans client ID.
    :param project_address: The Open Humans URL of the associated data project.
    :return: A dictionary of the base application home page context.
    """
    return {
        'client_id': client_id,
        'oh_proj_page': project_address
    }


def build_file_info_context(file_info):
    """
    Takes the information on all a users Open Humans project files and formats them into a dictionary.

    :param file_info: List of dictionaries containing Open Humans file information.
    :return: A dictionary of the users Open Humans project file information.
    """
    return {
        'ns_url_files': file_info,
        'ns_url_file_count': len(file_info)
    }


def upload_string_file_to_oh(oh_member, string_content, filename, file_metadata):
    """
    Uploads a new file to the members Open Humans account, containing the string contents provided.
    :param oh_member: An Open Humans member Django model.
    :param string_content: The string to be written inside of the new uploaded file.
    :param filename: The name of the file to be uploaded.
    :param file_metadata: The metadata of the file to be uploaded.
    :return: boolean. True if successful, else False
    """
    try:
        with io.StringIO(string_content) as s:
            oh_member.upload(s, filename, file_metadata)
        return True
    except:
        logger.error(f'Failed to upload Nightscout URL to OH for OH member {oh_member.oh_id}')
        return False


def handle_oh_upload_attempt(request, upload_successful):
    """
    Returns a message to the user indicating the outcome of the Nightscout URL upload attempt.
    :param request: The Django request object.
    :param upload_successful: boolean, indicating success (true) or failure (false)
    :return: None
    """
    if upload_successful:
        messages.success(request, 'Successfully updated Nightscout URL information on Open Humans')
    else:
        messages.error(request, 'An error occurred uploading the file to Open Humans.')
