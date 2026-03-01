import hashlib
import json
from typing import Callable, Tuple
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import IdempotencyRecord
from app.errors import APIError


class IdempotencyService:
    @staticmethod
    def _hash_payload(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def execute_once(self, endpoint: str, idempotency_key: str, payload: dict, executor: Callable[[], Tuple[dict, int]]):
        if not idempotency_key:
            try:
                with db.session.begin():
                    return executor()
            except IntegrityError:
                db.session.rollback()
                raise APIError('DATABASE_WRITE_FAILED', 'Failed to persist request', 500)

        payload_hash = self._hash_payload(payload)
        try:
            with db.session.begin():
                record = IdempotencyRecord(
                    endpoint=endpoint,
                    idempotency_key=idempotency_key,
                    request_hash=payload_hash,
                    response_payload={},
                    status_code=0,
                )
                db.session.add(record)
                db.session.flush()

                response_payload, status_code = executor()
                record.response_payload = response_payload
                record.status_code = status_code
                return response_payload, status_code
        except IntegrityError:
            db.session.rollback()
            existing = IdempotencyRecord.query.filter_by(endpoint=endpoint, idempotency_key=idempotency_key).first()
            if not existing:
                raise APIError('DATABASE_WRITE_FAILED', 'Failed to persist idempotent request', 500)
            if existing.request_hash != payload_hash:
                raise APIError('IDEMPOTENCY_KEY_REUSED', 'Idempotency key was used with different payload', 409)
            if existing.status_code == 0:
                raise APIError('IDEMPOTENCY_IN_PROGRESS', 'Request with this idempotency key is still processing', 409)
            return existing.response_payload, existing.status_code
