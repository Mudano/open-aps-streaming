from datetime import datetime
from .oh_user import OhUser
from .nightscout_site import NightscoutSite
from .nightscout_data_types import supported_data_types
import os
from .utility_functions import build_ns_file_metadata, delete_oh_file, \
    upload_local_file_to_oh, get_current_unix_timestamp_ms, get_basename, get_previous_upload_timestamp, \
    build_new_oh_filename, update_file_with_string, delete_local_file

CLIENT_ID = os.getenv('OPEN_HUMANS_CLIENT_ID')
CLIENT_SECRET = os.getenv('OPEN_HUMANS_CLIENT_SECRET')


def nightscout_ingest_job():
    print(f'Ingest job commencing at {datetime.now()}')

    # pull tokens from database
    users = OhUser.get_all_users()

    # for each user
    for user in users:

        # Refresh tokens against OH and pull the nightscout URL file from OH
        token_refresh_outcome = user.refresh_oh_token(CLIENT_ID, CLIENT_SECRET)
        nightscout_url = user.fetch_ns_url()

        # any failure to fetch a nightscout url will result in no transfer
        if nightscout_url and token_refresh_outcome:
            nightscout_site = NightscoutSite(nightscout_url)
            ns_valid = nightscout_site.validate_url()

            data_pulled_until = get_current_unix_timestamp_ms()

            if ns_valid:
                for data_type in supported_data_types:

                    local_copy_of_data_file_name = user.fetch_and_write_data_file(data_type.name)
                    data_file_name = get_basename(local_copy_of_data_file_name)
                    data_last_loaded_at = get_previous_upload_timestamp(data_file_name)

                    new_data = nightscout_site.get_new_data_since(data_type, data_last_loaded_at, data_pulled_until)

                    # if no new data is fetched for the given type then no further action is taken
                    if new_data:
                        print(f"new {data_type.name} found for user {user.member_code}")
                        update_file_with_string(local_copy_of_data_file_name, new_data, data_type.file_update_method)

                        entries_metadata = build_ns_file_metadata(data_type.name)
                        new_oh_file_name = build_new_oh_filename(data_pulled_until, user.member_code, data_type.name)

                        print(f'pushing new data file to {new_oh_file_name} for user {user.member_code}')
                        upload_local_file_to_oh(local_copy_of_data_file_name, new_oh_file_name,
                                                entries_metadata, user.access_token, user.member_code)

                        print(f'deleting previous OH file at: {data_file_name}')
                        delete_oh_file(user.access_token, data_file_name)

                    print(f'deleting local temp file at: {local_copy_of_data_file_name}')
                    delete_local_file(local_copy_of_data_file_name)

    print(f'Ingest job completed at {datetime.now()}')
