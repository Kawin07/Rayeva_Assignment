from flask import request, jsonify
from app.routes import api_bp
from app.services import OrderService
from app.security import require_auth, rate_limit
from app.utils import parse_json_body


@api_bp.route('/orders', methods=['GET'])
@require_auth(roles=['admin', 'support'])
def list_orders():
    service = OrderService()
    payload, status_code = service.list_orders()
    return jsonify(payload), status_code


@api_bp.route('/orders', methods=['POST'])
@require_auth(roles=['admin', 'user'])
def create_order():
    data = parse_json_body(max_bytes=1048576)
    idempotency_key = request.headers.get('Idempotency-Key', '').strip()
    service = OrderService()
    payload, status_code = service.create_order(data, idempotency_key=idempotency_key)
    return jsonify(payload), status_code


@api_bp.route('/orders/<int:order_id>/impact-report', methods=['POST'])
@require_auth(roles=['admin', 'support', 'user'])
@rate_limit()
def generate_impact_report(order_id):
    service = OrderService()
    payload, status_code = service.generate_impact_report(order_id)
    return jsonify(payload), status_code
