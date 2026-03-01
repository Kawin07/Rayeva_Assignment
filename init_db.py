from app import create_app, db
from app.models import Product

app = create_app('development')

with app.app_context():
    db.drop_all()
    db.create_all()

    sample_products = [
        {
            "sku": "PROD-BAMBOO-001",
            "name": "Eco Bamboo Toothbrush",
            "description": "Natural bamboo toothbrush with compostable bristles",
            "price": 5.99,
            "primary_category": "Personal Care",
            "sub_category": "Oral Care",
            "seo_tags": ["bamboo", "toothbrush", "eco-friendly", "sustainable", "compostable"],
            "sustainability_filters": ["compostable", "vegan", "zero-waste"]
        },
        {
            "sku": "PROD-BOTTLE-001",
            "name": "Stainless Steel Water Bottle",
            "description": "Reusable stainless steel bottle with non-toxic lining",
            "price": 24.99,
            "primary_category": "Home & Garden",
            "sub_category": "Drinkware",
            "seo_tags": ["water bottle", "reusable", "stainless steel", "eco-friendly", "sustainable"],
            "sustainability_filters": ["plastic-free", "recycled", "zero-waste", "renewable"]
        },
        {
            "sku": "PROD-BAG-001",
            "name": "Organic Cotton Shopping Bag",
            "description": "Durable organic cotton bag for shopping and storage",
            "price": 12.99,
            "primary_category": "Apparel & Accessories",
            "sub_category": "Bags",
            "seo_tags": ["shopping bag", "organic cotton", "eco-friendly", "reusable", "sustainable"],
            "sustainability_filters": ["plastic-free", "organic", "fair-trade", "vegan"]
        }
    ]

    for product_data in sample_products:
        product = Product(**product_data)
        db.session.add(product)

    db.session.commit()

    print(f"✅ Database initialized with {len(sample_products)} sample products")
    print("\nSample Products:")
    for product in Product.query.all():
        print(f"  - {product.name} (${product.price})")
