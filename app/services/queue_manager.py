import io
import fastavro

from kafka import KafkaConsumer, TopicPartition

from ..helpers import COUNT, DB_KEY, DEVICE_KEY, OFFSET, TCU_KEY
from ..infrastructure import Cache
from ..settings import settings

TMDC_DATA_SCHEMA = {
    'namespace': 'tmatix',
    'name': 'TMDCRawData',
    'type': 'record',
    'fields': [{
        'name': 'metadata', 'type': {
            'type': 'record', 'name': 'Metadata',
            'fields': [
                {
                    'name': 'process',
                    'type': {
                        'type': 'record',
                        'name': 'ProcessMetadata',
                        'fields': [
                            {'name': 'host', 'type': 'string'},
                            {'name': 'pid', 'type': 'int'}
                        ]
                    }
                },
                {'name': 'version', 'type': 'int'}
            ]
        }},
        {'name': 'uuid', 'type': 'string'},
        {'name': 'tcu_id', 'type': 'string'},
        {'name': 'collection_date', 'type': 'string'},
        {'name': 'data', 'type': {'type': 'map', 'values': 'string'}}
    ]
}


class QueueManager:
    def __init__(self) -> None:
        self.consumer = KafkaConsumer(**settings.KAFKA)
        self.topic = TopicPartition(settings.KAFKA_DATA_TOPIC, 0)
        self.consumer.assign([self.topic])
        self.cache = Cache()

        offset, *_ = self.cache.get_hash('system', OFFSET)
        try:
            self.consumer.seek(self.topic, int(offset))
        except ValueError:
            self.consumer.seek_to_end(self.topic)

    def start(self) -> None:
        VALUE = 1
        while True:
            for message in self.consumer:
                b_msg = io.BytesIO(message.value)
                offset = message.offset
                avro_message = fastavro.load(b_msg, TMDC_DATA_SCHEMA)
                tcu_id = avro_message['tcu_id']
                tcu_list, *_ = self.cache.get_hash('system', 'tcu_list')
                if str(tcu_id) in tcu_list:
                    print(tcu_id)
                    db_name, device_id = self.cache.get_hash(TCU_KEY(tcu_id), 'db_name', 'device_id')
                    self.cache.start_transaction()
                    self.cache.increment_field('system', COUNT, VALUE)
                    self.cache.update_field('system', OFFSET, offset)
                    self.cache.increment_field(DB_KEY(db_name), COUNT, VALUE)
                    self.cache.update_field(DB_KEY(db_name), OFFSET, offset)
                    self.cache.increment_field(DEVICE_KEY(db_name, device_id), COUNT, VALUE)
                    self.cache.update_field(DEVICE_KEY(db_name, device_id), OFFSET, offset)
                    self.cache.increment_field(TCU_KEY(tcu_id), COUNT, VALUE)
                    self.cache.end_transaction()
