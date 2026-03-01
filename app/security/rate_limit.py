import time
from functools import wraps
from flask import request, g, current_app
from app.errors import APIError

_BUCKETS = {}


def _build_identity_key():
    auth = getattr(g, 'auth', None)
    subject = auth.get('subject') if auth else request.remote_addr
    return f"{subject}:{request.path}"


def rate_limit(per_minute=None):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            limit = per_minute or int(current_app.config.get('RATE_LIMIT_PER_MINUTE', 30))
            now = int(time.time())
            window = now // 60
            identity = _build_identity_key()
            bucket_key = f"{identity}:{window}"
            current = _BUCKETS.get(bucket_key, 0)
            if current >= limit:
                raise APIError('RATE_LIMITED', 'Rate limit exceeded', 429)
            _BUCKETS[bucket_key] = current + 1
            return func(*args, **kwargs)

        return wrapped

    return decorator
