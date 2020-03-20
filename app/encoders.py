import datetime
from flask import json


class CustomJSONEncoder(json.JSONEncoder):
    "Add support for serializing timedeltas"

    def default(self, o):
        if type(o) == datetime.timedelta:
            return str(o)
        elif type(o) == datetime.datetime:
            return o.isoformat()
        elif type(o) == datetime.date:
            return str(o)
        else:
            return super().default(o)
