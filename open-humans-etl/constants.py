
from models import Treatment, Entry, Profile, DeviceStatus, DeviceStatusMetric

FILES_DIRECTORY='C:/Users/Laurie Bamber/Work/open-aps-streaming/open-humans-etl/data/test'
ENTITY_MAPPER = {
    'treatments': {'object': Treatment, 'table': 'treatments', 'primary_keys': ['id']},
    'entries': {'object': Entry, 'table': 'entries', 'primary_keys': ['id']},
    'profile': {'object': Profile, 'table': 'profile', 'primary_keys': ['id']},
    'devicestatus': {'object': DeviceStatus, 'table': 'device_status', 'primary_keys': ['id']},
    'status_metrics': {'object': DeviceStatusMetric,'table': 'device_status_metrics', 'primary_keys': ['device_status_id']}
}
