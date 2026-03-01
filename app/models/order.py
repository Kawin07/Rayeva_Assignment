from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = (
        db.Index('ix_orders_customer_name', 'customer_name'),
        db.Index('ix_orders_status', 'status'),
        db.Index('ix_orders_created_at', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(500), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    products = db.Column(db.JSON)

    plastic_saved_kg = db.Column(db.Float, default=0)
    carbon_avoided_kg = db.Column(db.Float, default=0)
    local_sourcing_percentage = db.Column(db.Float, default=0)
    impact_statement = db.Column(db.Text)

    status = db.Column(db.String(50), default='pending')
    return_policy_acknowledged = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'total_amount': self.total_amount,
            'products': self.products or [],
            'plastic_saved_kg': self.plastic_saved_kg,
            'carbon_avoided_kg': self.carbon_avoided_kg,
            'local_sourcing_percentage': self.local_sourcing_percentage,
            'impact_statement': self.impact_statement,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
