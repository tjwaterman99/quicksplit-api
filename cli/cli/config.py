from dataclasses import dataclass, asdict
from json import dumps, dump, load
import os


@dataclass
class Config(object):
    api_url: str
    token: str
    user: dict

    def __init__(self):
        self.config_fname = os.environ['QUICKSPLIT_CONFIG']
        self.data_fname = os.environ['QUICKSPLIT_DATA']
        self.api_url = os.environ['QUICKSPLIT_API_URL']
        self.token = None
        self.user = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_fname):
            self.dump_config()
        with open(self.config_fname, 'r') as o:
            data = load(o)
            self.token = data.get('token')
            self.api_url = data.get('api_url') or self.api_url
            self.user = data.get('user') or {}

    def dump_config(self):
        with open(self.config_fname, 'w') as o:
            dump(asdict(self), o, indent=2)

    def __str__(self):
        return dumps(asdict(self), indent=2)
