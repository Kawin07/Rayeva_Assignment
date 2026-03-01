import hmac
import hashlib
import time
from flask import request, current_app
from app.errors import APIError
from app.utils import setup_logger

logger = setup_logger('webhook_security')
_REPLAY_CACHE = {}


def _get_signature_headers():
    signature = request.headers.get('X-Webhook-Signature', '')
    timestamp = request.headers.get('X-Webhook-Timestamp', '')
    event_id = request.headers.get('X-Webhook-Event-Id', '')
    return signature, timestamp, event_id


def _verify_signature(secret: str, timestamp: str, body: bytes, signature: str):
    payload = f"{timestamp}.".encode('utf-8') + body
    expected = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_webhook_request():
    signature, timestamp, event_id = _get_signature_headers()
    secret = current_app.config.get('WEBHOOK_SECRET', '')

    if not secret:
        raise APIError('WEBHOOK_CONFIG_ERROR', 'Webhook secret not configured', 500)

    if not signature or not timestamp or not event_id:
        raise APIError('WEBHOOK_INVALID_HEADERS', 'Missing webhook security headers', 401)

    try:
        ts = int(timestamp)
    except ValueError:
        raise APIError('WEBHOOK_INVALID_TIMESTAMP', 'Invalid webhook timestamp', 401)

    replay_window = int(current_app.config.get('WEBHOOK_REPLAY_WINDOW_SECONDS', 300))
    now = int(time.time())
    if abs(now - ts) > replay_window:
        raise APIError('WEBHOOK_REPLAY_REJECTED', 'Timestamp outside allowed window', 401)

    if event_id in _REPLAY_CACHE:
        raise APIError('WEBHOOK_REPLAY_REJECTED', 'Duplicate webhook event', 409)

    body = request.get_data(cache=True)
    if not _verify_signature(secret, timestamp, body, signature):
        raise APIError('WEBHOOK_SIGNATURE_INVALID', 'Invalid webhook signature', 401)

    _REPLAY_CACHE[event_id] = now

    logger.info(
        'webhook_verified event_id=%s timestamp=%s path=%s',
        event_id,
        timestamp,
        request.path,
    )
