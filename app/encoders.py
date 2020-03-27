import datetime
from flask import json
from sqlalchemy.engine import RowProxy


class CustomJSONEncoder(json.JSONEncoder):
    "Add support for serializing timedeltas"

    def default(self, o):
        if type(o) == datetime.timedelta:
            return str(o)
        elif type(o) == datetime.datetime:
            return o.isoformat()
        elif type(o) == datetime.date:
            return str(o)
        elif type(o) == RowProxy:
            return dict(o)
        else:
            return super().default(o)
