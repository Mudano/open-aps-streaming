from functools import reduce
from operator import concat
import json
import io
from ohapi.api import upload_stream, delete_file
from datetime import datetime
import requests

def minify_json(json_dict):
    return json.dumps(json_dict, separators=(',', ':')) + '\n'


def process_ns_entries(ns_entries_response):
    ns_entries_json = ns_entries_response.json()
    ns_entries_json.reverse()
    minified_entries = [minify_json(e) for e in ns_entries_json]
    json_string = reduce(concat, minified_entries, '')

    return json_string


def upload_local_file_to_oh(file_path, file_name, file_metadata, access_token, member_id):
    """
    Uploads a local file to the members Open Humans account.
    :param file_path: The location of the local file to be uploaded to Open Humans.
    :param file_name: The name of the file to be uploaded.
    :param file_metadata: The metadata of the file to be uploaded.
    :return: boolean. True if successful, else False
    """
    try:
        with open(file_path, 'rb') as fs:
            upload_stream(fs, file_name, file_metadata, access_token)
        return True
    except:
        print(f'Failed to upload {file_path} to OH for OH member {member_id}')
        return False


def upload_string_file_to_oh(string_content, file_name, file_metadata, access_token, member_id):
    """
    Uploads a new file to the members Open Humans account, containing the string contents provided.
    :param oh_member: An Open Humans member Django model.
    :param string_content: The string to be written inside of the new uploaded file.
    :param file_name: The name of the file to be uploaded.
    :param file_metadata: The metadata of the file to be uploaded.
    :return: boolean. True if successful, else False
    """
    try:
        with io.StringIO(string_content) as s:
            # oh_member.upload(s, filename, file_metadata)
            upload_stream(s, file_name, file_metadata, access_token)
        return True
    except:
        print(f'Failed to upload {file_name} to OH for OH member {member_id}')
        return False


def build_ns_file_metadata(file_type):
    """
    Given the OH project URL returns the metadata for a Nightscout URL file.

    :param file_type: Strig giving the type (of 4) nightscout data files.
    :return: A dictionary of metadata information.
    """
    file_description = f"Your Nightscout {file_type} data, uploaded at {datetime.utcnow()} UTC."
    file_tags = ["open-aps", "Nightscout", file_type, "json"]
    return {"tags": file_tags, "description": file_description}


def delete_oh_file(access_token, file_name):
    try:
        x = delete_file(access_token, file_basename=file_name)
        print(x.content)
        # delete_url = f'https://www.openhumans.org/api/direct-sharing/project/files/delete/?access_token={access_token}'
        # x = requests.post(delete_url, {"file_basename": f"{file_name}"})
        print(x.content)
        return True
    except:
        print(f'An error was encountered trying to delete file {file_name}')
        return False
