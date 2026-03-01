from flask import request
from app.errors import APIError


JSON_CONTENT_TYPE = 'application/json'


def parse_json_body(max_bytes=None):
    content_type = request.headers.get('Content-Type', '')
    if JSON_CONTENT_TYPE not in content_type:
        raise APIError('INVALID_CONTENT_TYPE', 'Content-Type must be application/json', 415)

    if max_bytes is not None:
        content_length = request.content_length or 0
        if content_length > max_bytes:
            raise APIError('REQUEST_TOO_LARGE', 'Request payload too large', 413)

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        raise APIError('INVALID_JSON', 'Malformed or missing JSON body', 400)

    return data


def sanitize_text(value: str, max_length: int):
    if not isinstance(value, str):
        raise APIError('VALIDATION_ERROR', 'Invalid string value', 400)
    clean = ' '.join(value.strip().split())
    if len(clean) == 0:
        raise APIError('VALIDATION_ERROR', 'Text value cannot be empty', 400)
    if len(clean) > max_length:
        raise APIError('VALIDATION_ERROR', f'Text exceeds max length {max_length}', 400)
    return clean
