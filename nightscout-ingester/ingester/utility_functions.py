from functools import reduce
from operator import concat
import json
import io
from ohapi.api import upload_stream, delete_file
from datetime import datetime
import os
import random
import string


def get_current_unix_timestamp():
    return int(datetime.timestamp(datetime.now())) * 1000


def get_basename(full_local_filename):
    return full_local_filename.split('/')[-1]


def get_previous_upload_timestamp(local_file_basename):
    return int(local_file_basename.split('_')[0])


def minify_json(json_dict):
    return json.dumps(json_dict, separators=(',', ':')) + '\n'


def update_file_with_string(file_name, string_to_append, update_method):
    if update_method == 'append':
        open_mode = 'a'
    else:
        open_mode = 'w'

    with open(file_name, open_mode) as past_data_file:
        past_data_file.write(string_to_append)


def delete_local_file(file_name):
    try:
        os.remove(file_name)
    except OSError as e:
        print(f"Error deleting file {file_name}: {e}")


def build_new_oh_filename(end_data_timestamp, oh_user_code, data_type):
    """

    :param end_data_timestamp: The unix timestamp (milliseconds) giving the time of his update.
    :param oh_user_code: The OpenHumans member code of the user who's data this is.
    :param data_type: string representing which one of the four file types loaded from nightscout this is
    :return:
    """
    return f'{end_data_timestamp}_{oh_user_code}_{data_type}.json'


def process_ns_data(ns_data_response, sensitive_keys):
    ns_data_json = ns_data_response.json()
    ns_data_json.reverse()

    minified_data = [minify_json(sub_sensitive_key(d, sensitive_keys)) for d in ns_data_json]
    json_string = reduce(concat, minified_data, '')

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
            upload_stream(s, file_name, file_metadata, access_token)
        return True
    except:
        print(f'Failed to upload {file_name} to OH for OH member {member_id}')
        return False


def build_ns_file_metadata(file_type):
    """
    Given the OH project URL returns the metadata for a Nightscout URL file.

    :param file_type: String giving the type (of 4) nightscout data files.
    :return: A dictionary of metadata information.
    """
    file_description = f"Your Nightscout {file_type} data, uploaded at {datetime.utcnow()} UTC."
    file_tags = ["open-aps", "Nightscout", file_type, "json"]
    return {"tags": file_tags, "description": file_description}


def delete_oh_file(access_token, file_name):
    try:
        deletion_response = delete_file(access_token, file_basename=file_name)

        if deletion_response.status_code == 200:
            return True
        else:
            print(f'An error was encountered trying to delete file {file_name}')
            return False
    except:
        print(f'An error was encountered trying to delete file {file_name}')
        return False


def generate_random_string(length):
    """
    Returns a random string of Upper case and numeric characters of the given length.

    :param length: The length of the string to be generated.
    :return: String
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def sub_sensitive_key(target_dict, sensitive_key_names):
    """
    For a list of sensitive key names, will replace any occurrences of these names in a given dict with random strings.

    :param target_dict:
    :param sensitive_key_names:
    :return: The target dictionary, with any sensitive key values scrubbed.
    """
    for sensitive_key in sensitive_key_names:
        if sensitive_key in target_dict:
            target_dict[sensitive_key] = generate_random_string(6)

    return target_dict


    # try:
    #     targ_dict[keyval] = subs_dict[targ_dict[keyval]]
    # except KeyError:
    #     try:
    #         subs_dict[targ_dict[keyval]] = ''.join(random.choice(
    #             string.ascii_uppercase + string.digits) for _ in range(6))
    #         targ_dict[keyval] = subs_dict[targ_dict[keyval]]
    #     except KeyError:
    #         pass