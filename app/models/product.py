from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    __table_args__ = (
        db.Index('ix_products_primary_category', 'primary_category'),
        db.Index('ix_products_created_at', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)

    primary_category = db.Column(db.String(100))
    sub_category = db.Column(db.String(100))
    seo_tags = db.Column(db.JSON)
    sustainability_filters = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'primary_category': self.primary_category,
            'sub_category': self.sub_category,
            'seo_tags': self.seo_tags or [],
            'sustainability_filters': self.sustainability_filters or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
