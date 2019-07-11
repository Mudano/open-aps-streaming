

class NightScoutDataTypes:
    def __init__(self, name, sensitive_keys, time_filter_name, file_update_method):
        self.name = name
        self.sensitive_keys = sensitive_keys
        self.time_filter_name = time_filter_name
        self.file_update_method = file_update_method

    def __repr__(self):
        return f'{self.__class__.__name__}('f'data_type={self.name!r})'


entries_data_type = NightScoutDataTypes('entries', [], 'date', 'append')
treatments_data_type = NightScoutDataTypes('treatments', ['enteredBy'], 'created_at', 'append')
device_status_data_type = NightScoutDataTypes('devicestatus', ['device'], 'created_at', 'append')
profile_data_type = NightScoutDataTypes('profile', [], 'created_at', 'overwrite')

supported_data_types = [entries_data_type, treatments_data_type, device_status_data_type, profile_data_type]
