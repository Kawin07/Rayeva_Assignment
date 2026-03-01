from flask import jsonify
from app.routes import api_bp
from app.services import SupportService
from app.security import require_auth, rate_limit, verify_webhook_request
from app.utils import parse_json_body


@api_bp.route('/support/whatsapp', methods=['POST'])
@require_auth(roles=['admin', 'support', 'user'])
@rate_limit()
def whatsapp_support():
    data = parse_json_body(max_bytes=1048576)
    service = SupportService()
    payload, status_code = service.handle_whatsapp_message(data)
    return jsonify(payload), status_code


@api_bp.route('/support/whatsapp/webhook', methods=['POST'])
@rate_limit(per_minute=120)
def whatsapp_webhook():
    verify_webhook_request()
    data = parse_json_body(max_bytes=1048576)
    service = SupportService()
    payload, status_code = service.handle_whatsapp_webhook(data)
    return jsonify(payload), status_code
