from datetime import datetime
from .oh_user import OhUser
from .nightscout_site import NightscoutSite
import os
from .file_utilities import upload_string_file_to_oh, build_ns_file_metadata, delete_oh_file, upload_local_file_to_oh

CLIENT_ID = os.getenv('OPEN_HUMANS_CLIENT_ID')
CLIENT_SECRET = os.getenv('OPEN_HUMANS_CLIENT_SECRET')


def nightscout_ingest_job():
    print(f'schedule test running at {datetime.now()}')

    # pull tokens from database
    users = OhUser.get_all_users()

    # for each user
    for user in users:

        # Refresh tokens against OH
        user.refresh_oh_token(CLIENT_ID, CLIENT_SECRET)

        # pull the nightscout URL file from OH
        nightscout_url = user.fetch_ns_url()
        #last_recorded_at = user.fetch_last_recorded_at()

        # any failure to fetch either url or last recorded files will result in no transfer, handled below
        if nightscout_url:
            nightscout_site = NightscoutSite(nightscout_url)
            nightscout_site.validate_url()

            data_pulled_until = int(datetime.timestamp(datetime.now())) * 1000
            local_copy_of_entries_data_file = user.fetch_and_write_entries_file()
            data_file_name = local_copy_of_entries_data_file.split('/')[-1]
            data_last_loaded_at = data_file_name.split('_')[0]

            new_entries = nightscout_site.get_new_entries_since(data_last_loaded_at, data_pulled_until)

            if new_entries:
                print(f"new entries found for user {user.member_code}")
                entries_metadata = build_ns_file_metadata('entries')

                # file_deletion_outcome = delete_oh_file(user.access_token, f'{user.member_code}_entries.json')
                # print(file_deletion_outcome)
                with open(local_copy_of_entries_data_file, "a") as past_data_file:
                    past_data_file.write(new_entries)
                #outcome = upload_string_file_to_oh(new_entries, f'{user.member_code}_entries.json',
                #                                   entries_metadata, user.access_token, user.member_code)

                outcome = upload_local_file_to_oh(local_copy_of_entries_data_file, f'{data_pulled_until}_{user.member_code}_entries.json',
                                                  entries_metadata, user.access_token, user.member_code)
                print(outcome)

                file_to_delete = f'{data_file_name}'
                print(f'deleting previous data file at: {file_to_delete}')
                file_deletion_outcome = delete_oh_file(user.access_token, file_to_delete)
                print(file_deletion_outcome)

            # pull the users nightscout data from this URL



        ## push this data to OH





