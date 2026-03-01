from flask import request, jsonify
from app.routes import api_bp
from app import db
from app.models import Proposal
from app.services import ProposalService
from app.security import require_auth, rate_limit
from app.utils import parse_json_body
from app.errors import APIError

@api_bp.route('/proposals', methods=['GET'])
@require_auth(roles=['admin', 'support', 'user'])
def list_proposals():
    proposals = Proposal.query.all()
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in proposals],
        'count': len(proposals)
    }), 200

@api_bp.route('/proposals/<int:proposal_id>', methods=['GET'])
@require_auth(roles=['admin', 'support', 'user'])
def get_proposal(proposal_id):
    proposal = Proposal.query.get(proposal_id)
    if not proposal:
        raise APIError('NOT_FOUND', 'Proposal not found', 404)
    return jsonify({'success': True, 'data': proposal.to_dict()}), 200

@api_bp.route('/proposals/generate', methods=['POST'])
@require_auth(roles=['admin', 'user'])
@rate_limit()
def generate_proposal():
    data = parse_json_body(max_bytes=1048576)
    idempotency_key = request.headers.get('Idempotency-Key', '').strip()
    service = ProposalService()
    payload, status_code = service.generate_proposal(data, idempotency_key=idempotency_key)
    return jsonify(payload), status_code

@api_bp.route('/proposals/<int:proposal_id>/status', methods=['PATCH'])
@require_auth(roles=['admin', 'support'])
def update_proposal_status(proposal_id):
    proposal = Proposal.query.get(proposal_id)
    if not proposal:
        raise APIError('NOT_FOUND', 'Proposal not found', 404)

    data = parse_json_body(max_bytes=1024)
    new_status = data.get('status')

    if new_status not in ['draft', 'sent', 'accepted', 'rejected']:
        raise APIError('VALIDATION_ERROR', 'Invalid status', 400)
    
    proposal.status = new_status
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': proposal.to_dict()
    }), 200
