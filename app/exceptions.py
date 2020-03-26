import traceback
from flask import current_app, make_response, json
from app.models import db

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


def handle_route_not_found_exception(exc):
    if not current_app.testing:
        db.session.rollback()
    resp = {
        'data': None,
        'message': "That route does not exist.",
        'status_code': 404
    }
    return make_response(json.dumps(resp), 404)


def handle_api_exception(exc):
    if not current_app.testing:
        db.session.rollback()
    return make_response(json.dumps(exc), exc.status_code)


def handle_uncaught_exception(exc):
    if not current_app.testing:
        db.session.rollback()
    current_app.logger.error("Unhandled error: " + str(exc))
    current_app.logger.error(traceback.format_exc())
    resp = {
        'data': None,
        'message': "Unexpected exception occured. Please try again later.",
        'status_code': 500
    }
    return make_response(json.dumps(resp), 500)
