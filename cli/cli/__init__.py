import os

_qs_config_fname = os.path.join(os.path.expanduser('~'), '.quicksplit.json')
_qs_data_fname = os.path.join(os.getcwd(), '.data.yml')


os.environ.setdefault('QUICKSPLIT_CONFIG', _qs_config_fname)
os.environ.setdefault('QUICKSPLIT_DATA', _qs_data_fname)
os.environ.setdefault('QUICKSPLIT_API_URL', 'https://api.quicksplit.io')


from cli.commands import base
from cli.client import Client
from cli.config import Config
