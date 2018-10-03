class ConfigBase:
    DATABASES = {
        'new_proc': {
            'user': 'tmatix',
            'password': 'tmatix',
            'host': 'localhost',
            'dbname': 'new_proc',
        }
    }

    KAFKA = {
        'bootstrap_servers': ['localhost:9092'],
        'enable_auto_commit': False,
        'consumer_timeout_ms': 1000
    }

    KAFKA_DATA_TOPIC = 'tmdc_data'

    ZOOKEEPER = {
        'hosts': '127.0.0.1:2181'
    }

    ZOO_OFFSET_PATH = '/tmatix/processing/offsets'

    REDIS = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'decode_responses': True
    }

    ANALYZER_INTERVAL = 30
