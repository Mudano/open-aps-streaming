from functools import reduce
from operator import concat
import json
import io
from ohapi.api import upload_stream, delete_file
from datetime import datetime
import os
import random
import string


def get_current_unix_timestamp_ms():
    """
    Returns the current unix timestamp in milliseconds. Millisecond values are simply produced derived
    from second values and so are only suitable for millisecond formatting, not millisecond precision.

    :return: integer
    """
    return int(datetime.timestamp(datetime.now())) * 1000


def get_basename(absolute_file_path):
    """
    Takes an absolute file path and returns only the file name (stripping of all directory information).

    :param absolute_file_path: The absolute path from which to extract the filename.
    :return: string
    """
    return absolute_file_path.split('/')[-1]


def get_previous_upload_timestamp(nightscout_data_file_name):
    """
    Based on the formatting of uploaded Nightscout data files on Open Humans, this function gets the time of the last
    data upload from the uploaded file name.

    :param nightscout_data_file_name: The file name of the nightscout data file held on OpenHumans.
    :return: A Unix timestamp value in milliseconds.
    """
    return int(nightscout_data_file_name.split('_')[0])


def dict_to_minified_json_string(json_dict):
    """
    Takes a python dictionary and returns a json string with all whitespace removed and a linebreak added at the end.

    :param json_dict: The python dictionary to format
    :return: A string representation of the dictionary as json, with no whitespace apart from a linebreak at the end.
    """
    return json.dumps(json_dict, separators=(',', ':')) + '\n'


def update_file_with_string(file_path, update_string, update_method):
    """
    Given a file path, and a string, will update the file with the string according to the provided update method
    (either 'append', or 'overwrite').

    :param file_path: The path of the file to update.
    :param update_string: The string to update the file with.
    :param update_method: Either 'append' to append the string to the file, or any other value will result in
    the file being overwritten.
    :return: None
    """
    if update_method == 'append':
        open_mode = 'a'
    else:
        open_mode = 'w'

    with open(file_path, open_mode) as past_data_file:
        past_data_file.write(update_string)


def delete_local_file(file_path):
    """
    Deletes a local file given its path.
    
    :param file_path: 
    :return:
    """
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")


def build_new_oh_filename(end_data_timestamp, oh_user_code, data_type):
    """

    :param end_data_timestamp: The unix timestamp (milliseconds) giving the time of his update.
    :param oh_user_code: The OpenHumans member code of the user who's data this is.
    :param data_type: string representing which one of the four file types loaded from nightscout this is
    :return:
    """
    return f'{end_data_timestamp}_{oh_user_code}_{data_type}.json'


def process_ns_data(ns_data_dict, sensitive_keys):
    """
    Takes a dictionary of pulled Nightscout data and a list of any sensitive keys, any instances of these keys will
    have their values replaced by random values. The dictionary is then converted to a JSON string representation with
    whitespace removed and a linebreak added at the end of each instance.

    :param ns_data_dict: The NightScout data as a python dictionary.
    :param sensitive_keys: A list of any keys that might contain sensitive information.
    :return: A string representing cleaned json data records, separated by linebreaks.
    """
    ns_data_dict.reverse()

    processed_list_of_data = [dict_to_minified_json_string(sub_sensitive_key(d, sensitive_keys)) for d in ns_data_dict]
    json_string = reduce(concat, processed_list_of_data, '')

    return json_string


def upload_local_file_to_oh(file_path, file_name, file_metadata, access_token, member_id):
    """
    Uploads a local file to the members Open Humans account.

    :param file_path: The location of the local file to be uploaded to Open Humans.
    :param file_name: The name of the file to be uploaded.
    :param file_metadata: The metadata of the file to be uploaded.
    :param access_token: The project access token for the given member.
    :param member_id: The Open Humans ID of the member.
    :return: boolean. True if successful, else False
    """
    try:
        with open(file_path, 'rb') as fs:
            upload_stream(fs, file_name, file_metadata, access_token)
        return True
    except:
        print(f'Failed to upload {file_path} to OH for OH member {member_id}')
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
    """
    Deletes any files belonging to an OH user and projet, whose base file name matches the given file name.

    :param access_token: The project access token for the given member.
    :param file_name: The name of the file to be deleted from OpenHumans (all matching filenames will be deleted).
    :return: boolean. True if successful, else False
    """
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
