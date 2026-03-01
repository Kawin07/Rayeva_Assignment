from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

from . import products
from . import proposals
from . import orders
from . import support

@api_bp.route('', methods=['GET'])
@api_bp.route('/', methods=['GET'])
def api_root():
    return jsonify({
        'success': True,
        'message': 'Rayeva AI Systems for Sustainable Commerce',
        'version': '1.0.0',
        'endpoints': {
            'products': {
                'list': 'GET /api/products',
                'get': 'GET /api/products/<id>',
                'categorize': 'POST /api/products/categorize',
                'delete': 'DELETE /api/products/<id>'
            },
            'proposals': {
                'list': 'GET /api/proposals',
                'get': 'GET /api/proposals/<id>',
                'generate': 'POST /api/proposals/generate',
                'update_status': 'PATCH /api/proposals/<id>/status'
            },
            'orders': {
                'list': 'GET /api/orders',
                'create': 'POST /api/orders',
                'impact_report': 'POST /api/orders/<id>/impact-report'
            },
            'support': {
                'whatsapp': 'POST /api/support/whatsapp',
                'webhook': 'POST /api/support/whatsapp/webhook'
            }
        },
        'documentation': 'See README.md'
    }), 200
