
from models import Treatment, Entry, Profile, DeviceStatus, DeviceStatusMetric

FILES_DIRECTORY = '/data'
ENTITY_MAPPER = {
    'treatments': {'object': Treatment, 'table': 'treatments', 'primary_keys': ['id', 'created_at']},
    'entries': {'object': Entry, 'table': 'entries', 'primary_keys': ['id', 'date']},
    'profile': {'object': Profile, 'table': 'profile', 'primary_keys': ['id', 'created_at']},
    'devicestatus': {'object': DeviceStatus, 'table': 'device_status', 'primary_keys': ['id', 'created_at']},
    'status_metrics': {'object': DeviceStatusMetric,'table': 'device_status_metrics', 'primary_keys': ['device_status_id', 'enacted_timestamp']}
}
