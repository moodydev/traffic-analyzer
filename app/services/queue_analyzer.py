import ast
import os
import time
import psycopg2  # type: ignore
from typing import Any, Dict, List, Tuple

from ..helpers import *
from ..infrastructure import Cache
from ..settings import settings


class QueueAnalyzer:
    def __init__(self) -> None:
        self.cache = Cache()

    @staticmethod
    def fetch_db_state(db: Dict[str, str]) -> List[Tuple[str, int]]:
        db_conn = psycopg2.connect(**db)

        tcu_query = """
            select tcu.tcu_id, dev.device_id from m_controldata_tcu tcu
            inner join m_controldata_devicetcu dev on tcu.id = dev.tcu_id
            where tcu.enabled = true
        """

        cursor = db_conn.cursor()
        cursor.execute(tcu_query)
        tcus = [(tcu_id, device_id) for tcu_id, device_id in cursor]

        db_conn.close()

        return tcus

    def cache_db_state(self, db_name: str, tcu_ids: List[str], device_ids: List[int], tcus) -> None:
        self.cache.start_transaction()
        self.cache.set_hash('db:{}'.format(db_name), {'tcu_list': tcu_ids, 'device_list': device_ids})
        for device_id in device_ids:
            self.cache.set_hash('{}:device:{}'.format(db_name, device_id), {'id': device_id})
        for tcu_id, device_id in tcus:
            self.cache.set_hash('tcu:{}'.format(tcu_id), {
                'db_name': db_name, 'device_id': device_id
            })
        self.cache.end_transaction()

    def sync_db_state(self):
        tcu_count = 0
        tcu_list = []
        device_count = 0
        for db in settings.DATABASES:
            tcus = self.fetch_db_state(settings.DATABASES[db])
            tcu_ids = [tcu[0] for tcu in tcus]
            device_ids = {tcu[1] for tcu in tcus}
            tcu_count += len(tcu_ids)
            device_count += len(device_ids)
            tcu_list += tcu_ids
            self.cache_db_state(db, tcu_ids, device_ids, tcus)

        self.cache.set_hash('system', {
            'db': [key for key in settings.DATABASES],  # in future set just those with active devices and available connection
            'device_count': device_count,
            'tcu_count': tcu_count,
            'tcu_list': tcu_list
        })

    def run_analytics(self):
        print('RUNNING ANALYTICS')
        def _round(_num, _decimals=4):
            return round(_num, _decimals)

        def difference_count(count, interval):
            count = count or 0
            interval = interval or 0
            return int(count) - int(interval)

        def calculate_load_index(system_count, resource_count):
            try:
                index = 1 - ((int(system_count) - int(resource_count)) / int(system_count))
            except ZeroDivisionError:
                index = 0
            return _round(index)

        databases, sys_count, sys_interval, *_ = self.cache.get_hash('system', 'db', COUNT, COUNT_INTERVAL)
        sys_count = sys_count or 0
        sys_msgs = difference_count(sys_count, sys_interval)
        self.cache.update_field('system', COUNT_INTERVAL, sys_count)
        databases = ast.literal_eval(databases)

        for db in databases:
            devices, db_count, db_interval, *_ = self.cache.get_hash(DB_KEY(db), 'device_list', COUNT, COUNT_INTERVAL)
            db_count = db_count or 0
            devices = ast.literal_eval(devices)
            db_msgs = difference_count(db_count, db_interval)
            db_load = calculate_load_index(sys_msgs, db_msgs)
            self.cache.set_hash(DB_KEY(db), {COUNT_INTERVAL: db_count, LOAD_INDEX: db_load})
            for device in devices:
                device_count, device_interval, *_ = self.cache.get_hash(DEVICE_KEY(db, device), COUNT, COUNT_INTERVAL)
                device_count = device_count or 0
                dev_msgs = difference_count(device_count, device_interval)
                load_per_system = calculate_load_index(sys_msgs, dev_msgs)
                load_per_db = calculate_load_index(db_msgs, dev_msgs)
                self.cache.set_hash(DEVICE_KEY(db, device), {
                    COUNT_INTERVAL: device_count,
                    LOAD_PER_DB: load_per_db,
                    LOAD_PER_SYSTEM: load_per_system}
                )

    def start(self) -> None:
        while True:
            self.sync_db_state()
            self.run_analytics()
            time.sleep(settings.ANALYZER_INTERVAL)
