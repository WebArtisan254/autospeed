from __future__ import annotations
import os
from rq import Queue
from redis import Redis


def get_redis() -> Redis:
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(url)

def get_queue() -> Queue:
    return Queue("autospeed", connection=get_redis(), default_timeout=300)