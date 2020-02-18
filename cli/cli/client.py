import requests


class Client(object):

    def __init__(self, config):
        self.config = config

    def send(self, method, route, json=None):
        _route = self.config.api_url + route
        headers = {}
        if self.config.token:
            headers.update({'Authorization': self.config.token})
        return requests.request(method, url=_route, json=json, headers=headers)

    def login(self, email, password):
        resp = self.post('/login', json={
            'email': email,
            'password': password
        })
        if resp.ok:
            self.config.token = resp.json()['data']['id']
            self.config.dump_config()
        return resp

    def logout(self):
        self.config.token = None
        self.config.dump_config()

    def register(self, email, password):
        resp = self.post('/user', json={
            'email': email,
            'password': password
        })
        if resp.ok:
            self.login(email, password)
        return resp

    def get(self, route, json=None):
        return self.send(method='GET', route=route, json=json)

    def post(self, route, json=None):
        return self.send(method='POST', route=route, json=json)
