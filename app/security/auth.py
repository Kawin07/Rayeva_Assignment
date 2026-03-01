from functools import wraps
from flask import request, g, current_app
from app.errors import APIError


def _extract_bearer_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header.replace('Bearer ', '', 1).strip()


def require_auth(roles=None):
    allowed_roles = set(roles or [])

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            token = _extract_bearer_token()
            if not token:
                raise APIError('UNAUTHORIZED', 'Missing bearer token', 401)

            token_map = current_app.config.get('AUTH_TOKEN_MAP', {})
            principal = token_map.get(token)
            if not principal:
                raise APIError('UNAUTHORIZED', 'Invalid token', 401)

            role = principal.get('role')
            if allowed_roles and role not in allowed_roles:
                raise APIError('FORBIDDEN', 'Insufficient permissions', 403)

            g.auth = {
                'token': token,
                'role': role,
                'subject': principal.get('subject', 'unknown')
            }
            return func(*args, **kwargs)

        return wrapped

    return decorator
