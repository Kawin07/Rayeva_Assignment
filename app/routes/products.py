from flask import jsonify
from app.routes import api_bp
from app import db
from app.models import Product
from app.services import ProductService
from app.security import require_auth, rate_limit
from app.utils import parse_json_body
from app.errors import APIError

@api_bp.route('/products', methods=['GET'])
@require_auth(roles=['admin', 'support', 'user'])
def list_products():
    products = Product.query.all()
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in products],
        'count': len(products)
    }), 200

@api_bp.route('/products/<int:product_id>', methods=['GET'])
@require_auth(roles=['admin', 'support', 'user'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        raise APIError('NOT_FOUND', 'Product not found', 404)
    return jsonify({'success': True, 'data': product.to_dict()}), 200

@api_bp.route('/products/categorize', methods=['POST'])
@require_auth(roles=['admin', 'user'])
@rate_limit()
def categorize_product():
    data = parse_json_body(max_bytes=1048576)
    service = ProductService()
    payload, status_code = service.categorize_product(data)
    return jsonify(payload), status_code

@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
@require_auth(roles=['admin'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        raise APIError('NOT_FOUND', 'Product not found', 404)
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Product deleted'}), 200
