from app import db
from datetime import datetime


class IdempotencyRecord(db.Model):
    __tablename__ = 'idempotency_records'
    __table_args__ = (
        db.UniqueConstraint('endpoint', 'idempotency_key', name='uq_endpoint_idempotency_key'),
        db.Index('ix_idempotency_created_at', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(255), nullable=False)
    idempotency_key = db.Column(db.String(255), nullable=False)
    request_hash = db.Column(db.String(128), nullable=False)
    response_payload = db.Column(db.JSON, nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
