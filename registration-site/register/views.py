from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.models import User
import logging
import json
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import io
import psycopg2
from .settings import postgres_connection_string

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

    consent_string = get_consent_string(request)
    consent_filename = f'{oh_member.oh_id}_open_aps_data_sharing_consent.txt'
    consent_metadata = build_consent_metadata(settings.OPENHUMANS_PROJECT_ADDRESS)

    logger.debug(f"OH Member {oh_member.oh_id} has specified sharing consent for: {consent_string}")

    if ns_url:
        try:
            ns_url_file_metadata = build_ns_url_metadata(settings.OPENHUMANS_PROJECT_ADDRESS)
            ns_url_filename = f'{oh_member.oh_id}_open_aps_nightscout_url.txt'

            if ns_url_filename in get_oh_member_file_names(oh_member):
                logger.debug('Found an existing Nightscout URL file(s) for user. Deleting these before upload.')
                oh_member.delete_single_file(file_basename=ns_url_filename)  # this deletes all files with the name

            ns_upload_successful = upload_string_file_to_oh(oh_member, ns_url, ns_url_filename, ns_url_file_metadata)
            consent_upload_successful = upload_string_file_to_oh(oh_member, consent_string, consent_filename, consent_metadata)
            handle_oh_upload_attempt(request, ns_upload_successful, consent_upload_successful)
        except Exception as e:
            logger.error(e)
            messages.error(request, 'Failed to update Nightscout URL information on Open Humans')
    else:
        messages.warning(request, 'An empty Nightscout address cannot be submitted, please provide a valid URL.')

    return redirect('home')


@login_required
@require_http_methods(['POST'])
def logout_view(request):
    """
    The /logout endpoint. Responds to post requests by logging out the django user.
    """
    logout(request)
    return redirect('home')


@require_http_methods(['POST'])
@csrf_exempt
def deauth_view(request):
    """
    The /deauth endpoint. Hit with a POST request when a user de-authorises
    the OpenHumans project from accessing their data. The body of this request
    is of the form { 'project_member_id': '12345678', 'erasure_requested': True }
    """
    json_str = json.loads(request.body.decode('utf-8'))
    deauth_data = json.loads(json_str)
    member_code = deauth_data['project_member_id']
    erasure_requested = deauth_data['erasure_requested']

    if erasure_requested:
        logger.debug(f'Request received to delete member {member_code}')
        delete_user(member_code)
        delete_users_data(member_code)

    return HttpResponse(status=200)


def get_consent_string(request):
    nsf_consent = request.POST.get('nightscoutFoundationConsent', False)
    openaps_consent = request.POST.get('openApsConsent', False)

    if nsf_consent and openaps_consent:
        return 'both'
    elif nsf_consent:
        return 'nsf'
    elif openaps_consent:
        return 'openaps'
    else:
        return 'none'


def build_ns_url_metadata(oh_project_address):
    """
    Given the OH project URL returns the metadata for a Nightscout URL file.

    :param oh_project_address: The url of the OH project pushing the data
    :return: A dictionary of metadata information.
    """
    file_description = f"Your Nightscout URL, uploaded by {oh_project_address}"
    file_tags = ["open-aps", "Nightscout", "url", "text"]
    return {"tags": file_tags, "description": file_description}


def build_consent_metadata(oh_project_address):
    """
    Given the OH project URL returns the metadata for a data sharing consent file.

    :param oh_project_address: The url of the OH project pushing the data
    :return: A dictionary of metadata information.
    """
    file_description = f"Your Nightscout data sharing consent, uploaded by {oh_project_address}"
    file_tags = ["open-aps", "Nightscout", "consent", "text", "sharing"]
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
        logger.error(f'Failed to upload file {filename} to OH for OH member {oh_member.oh_id}')
        return False


def handle_oh_upload_attempt(request, ns_upload_successful, consent_upload_successful):
    """
    Returns a message to the user indicating the outcome of the Nightscout URL and consent file upload attempt.
    :param request: The Django request object.
    :param ns_upload_successful: boolean, indicating success (true) or failure (false) for upload of the NS URL.
    :param consent_upload_successful: boolean, indicating success (true) or failure (false) for upload of the consent string.
    :return: None
    """
    if ns_upload_successful and consent_upload_successful:
        messages.success(request, 'Successfully updated Nightscout URL information on Open Humans')
    else:
        messages.error(request, 'An error occurred uploading the file to Open Humans.')


def delete_user(member_code):
    """
    Given an Open Humans member code will attempt to delete that user from all locations in the
    registration portion of the application database.

    :param member_code: The Open Humans code of the member to be deleted
    :return: None
    """
    try:
        u = User.objects.get(username=f'{member_code}_openhumans')
        u.delete()
        logger.info(f'Successfully deleted member {member_code} from the registration database')

    except User.DoesNotExist:
        logger.error(f'Unable to delete member {member_code} as requested, member does not exist')

    except Exception as e:
        logger.error(f'error encountered attempting to delete member {member_code}: {e}')


def delete_users_data(member_code):
    """
    Given an Open Humans member code, will attempt to delete all of that users Nightscout data from
    the application database. This and the `delete_user` function should fully remove any record of
    a registered user if called successfully.

    :param member_code:  The Open Humans code of the member to be deleted
    :return: None
    """

    # this list gives the tables that should be deleted when clearing a user data, along with the
    # column in which their member code is stored.
    tables_to_delete_from = [
        ('openaps.device_status', 'user_id'),
        ('openaps.entries', 'user_id'),
        ('openaps.oh_etl_log', 'openaps_id'),
        ('openaps.profile', 'user_id'),
        ('openaps.treatments', 'user_id')
    ]

    delete_device_status_metrics_sql = """
        DELETE FROM
          openaps.device_status_metrics as dsm
        USING
          openaps.device_status as ds
        WHERE
          dsm.device_status_id = ds.id
        AND
          ds.user_id = %s
    """

    try:
        with psycopg2.connect(postgres_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(delete_device_status_metrics_sql, (member_code,))

                for to_delete in tables_to_delete_from:
                    deletion_sql = generate_user_deletion_sql(to_delete[0], to_delete[1])
                    cursor.execute(deletion_sql, (member_code,))

    except Exception as e:
        print(f"Error encountered attempting to delete data for user {member_code}: {e}")


def generate_user_deletion_sql(tbl_name, user_id_colname):
    return f"""
        DELETE FROM
          {tbl_name}
        WHERE
          {tbl_name}.{user_id_colname} = %s
    """