from dataclasses import dataclass


@dataclass
class ApiException(Exception):
    message: str
    status_code: int
    data: dict

    def __init__(self, status_code, message, data=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.data = data
