from app import db
from datetime import datetime

class AILog(db.Model):
    __tablename__ = 'ai_logs'
    __table_args__ = (
        db.Index('ix_ai_logs_module_created', 'module', 'created_at'),
        db.Index('ix_ai_logs_request_id', 'request_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(100), nullable=False)

    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.JSON, nullable=False)

    model = db.Column(db.String(100))
    tokens_used = db.Column(db.Integer)
    latency_ms = db.Column(db.Integer)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposals.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))

    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    request_id = db.Column(db.String(64))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'module': self.module,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'latency_ms': self.latency_ms,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
