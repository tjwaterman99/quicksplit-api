from typing import Dict
from dataclasses import dataclass

import requests
from werkzeug.local import LocalProxy
from flask_redis import FlaskRedis
from flask import current_app, g, request
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


worker = LocalProxy(get_worker)


class Mailer(object):

    url = "https://api.sendgrid.com/v3"

    def __init__(self, api_key=None, sent_by=None, production=None):
        self.api_key = api_key or current_app.config['SENDGRID_API_KEY']
        self.sent_by = sent_by or current_app.config['SENDGRID_DEFAULT_FROM_ADDRESS']
        self.production = production or current_app.config['ENV'] == 'production'

    def _send(self, route, to, subject, content):
        url = self.url + route
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": to
                        }
                    ],
                    "subject": subject
                }
            ],
            "from": {
                "email": self.sent_by
            },
            "content": [{
                "type": "text/plain",
                "value": content
            }],
            "mail_settings": {
                "sandbox_mode": {
                    "enable": not self.production
                }
            }
        }
        return requests.post(url, headers=headers, json=data)

    def _send_async(self, *args, **kwargs):
        return worker.enqueue(self._send, args=args, kwargs=kwargs)

    def send_text_email(self, to, subject, content):
        return self._send_async(route="/mail/send", to=to, subject=subject, content=content)


def get_mailer():
    if 'mailer' not in g:
        g.mailer = Mailer()
    return g.mailer


redis = LocalProxy(get_redis)
mailer = LocalProxy(get_mailer)
