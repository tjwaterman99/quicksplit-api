import requests
import threading


class Logger(threading.Thread):
    def __init__(self, client, **kwargs):
        self.client = client
        self.kwargs = kwargs
        self.kwargs.update(user_id=self.client.config.user.get('id'))
        super().__init__()

    def run(self):
        return self.client.send('post', '/events', json=self.kwargs)


class Client(object):

    def __init__(self, config):
        self.config = config

    def send(self, method, route, json=None):
        _route = self.config.api_url + route
        headers = {}
        if self.config.token:
            headers.update({'Authorization': self.config.token})
        return requests.request(method, url=_route, json=json, headers=headers)

    def track(self, **kwargs):
        return Logger(client=self, **kwargs).start()

    def login(self, email, password):
        resp = self.post('/login', json={
            'email': email,
            'password': password
        })
        if resp.ok:
            self.config.token = resp.json()['data']['admin_token']['value']
            self.config.user = resp.json()['data']
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
        return resp

    def get(self, route, json=None):
        return self.send(method='GET', route=route, json=json)

    def post(self, route, json=None):
        return self.send(method='POST', route=route, json=json)


class StagingClient(object):
    def __init__(self, client):
        self.client = client
        self.admin_token = client.config.token

    def __enter__(self):
        for token in self.client.config.user['tokens']:
            if token['environment'] == 'staging' and token['private'] == True:
                self.client.config.token = token['value']
                return self.client
        else:
            raise AttributeError("No valid staging token found. Please try logging in.")

    def __exit__(self, type, value, tracebook):
        self.client.config.token = self.admin_token

    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)
