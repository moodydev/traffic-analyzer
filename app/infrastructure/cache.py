import redis  # type: ignore
from typing import Any, Dict, Optional, Tuple

from ..settings import settings


class Cache:
    def __init__(self) -> None:
        self.redis = self.redis_client()
        self.submitter = self.redis

    def redis_client(self) -> redis.client:  # type: ignore
        return redis.StrictRedis(**settings.REDIS)

    def start_transaction(self) -> Any:
        self.submitter = self.redis.pipeline()

    def end_transaction(self) -> None:
        self.submitter.execute()
        self.submitter = self.redis

    def set_hash(self, _key: str, _dict: Dict[Any, Any]) -> None:
        self.submitter.hmset(_key, _dict)

    def get_hash(self, _key: str, *args: str) -> Tuple:
        return self.submitter.hmget(_key, *args)

    def increment_field(self, _key: str, _field: str, amount: int) -> None:
        self.submitter.hincrby(_key, _field, amount)

    def update_field(self, _key: str, _field: str, value: Any) -> None:
        self.submitter.hset(_key, _field, value)
