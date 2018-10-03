from .logger_helper import LoggerHelper


COUNT = 'msg_count'
COUNT_INTERVAL = 'msg_interval_count'
LOAD_INDEX = 'load_index'
LOAD_PER_DB = '{}{}'.format(LOAD_INDEX, '_per_db')
LOAD_PER_SYSTEM = '{}{}'.format(LOAD_INDEX, '_system')
OFFSET = 'offset'
SYSTEM_KEY = 'system'


def DB_KEY(db_name: str) -> str:
    return 'db:{}'.format(db_name)


def TCU_KEY(tcu_id: str) -> str:
    return 'tcu:{}'.format(tcu_id)


def DEVICE_KEY(db_name: str, device_id: str) -> str:
    return '{}:device:{}'.format(db_name, device_id)
