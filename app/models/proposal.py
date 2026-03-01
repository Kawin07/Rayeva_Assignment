from app import db
from datetime import datetime

class Proposal(db.Model):
    __tablename__ = 'proposals'
    __table_args__ = (
        db.Index('ix_proposals_client_name', 'client_name'),
        db.Index('ix_proposals_status', 'status'),
        db.Index('ix_proposals_created_at', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.String(255), unique=True, nullable=False)
    client_name = db.Column(db.String(500), nullable=False)
    budget = db.Column(db.Float, nullable=False)

    product_mix = db.Column(db.JSON)
    cost_breakdown = db.Column(db.JSON)
    impact_summary = db.Column(db.Text)
    total_estimated_cost = db.Column(db.Float)

    status = db.Column(db.String(50), default='draft')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'proposal_id': self.proposal_id,
            'client_name': self.client_name,
            'budget': self.budget,
            'product_mix': self.product_mix or [],
            'cost_breakdown': self.cost_breakdown or {},
            'impact_summary': self.impact_summary,
            'total_estimated_cost': self.total_estimated_cost,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
