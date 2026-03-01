from flask import jsonify, g
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError


class APIError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def make_error_response(code: str, message: str, status_code: int):
    request_id = getattr(g, 'request_id', 'unknown')
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'request_id': request_id,
        }
    }), status_code


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return make_error_response(error.code, error.message, error.status_code)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return make_error_response('VALIDATION_ERROR', 'Invalid request payload', 400)

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return make_error_response('HTTP_ERROR', error.description or 'HTTP error', error.code or 400)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return make_error_response('INTERNAL_SERVER_ERROR', 'Internal server error', 500)
