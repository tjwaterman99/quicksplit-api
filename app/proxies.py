from typing import Dict
from dataclasses import dataclass

from werkzeug.local import LocalProxy
from flask_redis import FlaskRedis
from flask import current_app, g
from rq import Queue
from rq.job import Job


@dataclass(init=False)
class JsonSerializableJobClass(Job):
    id: str


def get_redis():
    if 'redis' not in g:
        g.redis = FlaskRedis(current_app)._redis_client
    return g.redis


def get_worker():
    redis = get_redis()
    if 'worker' not in g:
        g.worker = Queue(connection=redis, job_class=JsonSerializableJobClass)
    return g.worker


redis = LocalProxy(get_redis)
worker = LocalProxy(get_worker)
