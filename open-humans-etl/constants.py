
from models import Treatment, Entry, Profile, DeviceStatus, DeviceStatusMetric

FILES_DIRECTORY='C:/Users/Laurie Bamber/Work/open-aps-streaming/open-humans-etl/data/test'
ENTITY_MAPPER = {
    'treatments': {'object': Treatment, 'table': 'treatments'},
    'entries': {'object': Entry, 'table': 'entries'},
    'profile': {'object': Profile, 'table': 'profile'},
    'devicestatus': {'object': DeviceStatus, 'table': 'device_status'},
    'status_metrics': {'object': DeviceStatusMetric,'table': 'device_status_metrics'}
}
