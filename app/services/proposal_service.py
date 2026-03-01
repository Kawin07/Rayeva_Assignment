import uuid
from app.errors import APIError
from app.models import Proposal
from app.modules import ProposalGenerator
from app.tasks import queue
from app.utils import validate_schema, ProposalGenerateRequest, ProposalOutput, log_ai_interaction
from .idempotency_service import IdempotencyService


class ProposalService:
    def __init__(self):
        self.idempotency = IdempotencyService()

    def generate_proposal(self, payload: dict, idempotency_key: str = ''):
        is_valid, validated, details = validate_schema(ProposalGenerateRequest, payload)
        if not is_valid:
            raise APIError('VALIDATION_ERROR', 'Invalid proposal payload', 400)

        def executor():
            generator = ProposalGenerator()
            task_result = queue.submit(
                'proposal_generate',
                generator.generate_proposal,
                validated['client_name'],
                validated['budget'],
                validated.get('preferences')
            )
            if not task_result.success:
                raise APIError('AI_UNAVAILABLE', 'Unable to generate proposal', 503)

            ai_result = task_result.data
            if not ai_result.get('success'):
                raise APIError('AI_GENERATION_FAILED', 'Proposal generation failed', 502)

            output_valid, output_data, output_errors = validate_schema(ProposalOutput, ai_result.get('data', {}))
            if not output_valid:
                raise APIError('AI_SCHEMA_INVALID', 'AI response schema invalid', 502)

            if output_data['cost_breakdown']['total'] > validated['budget']:
                raise APIError('BUDGET_EXCEEDED', 'Generated proposal exceeds budget', 422)

            proposal = Proposal(
                proposal_id=f"PROP-{uuid.uuid4().hex[:8].upper()}",
                client_name=validated['client_name'],
                budget=validated['budget'],
                product_mix=output_data['product_mix'],
                cost_breakdown=output_data['cost_breakdown'],
                impact_summary=output_data['impact_positioning']['environmental_benefit'],
                total_estimated_cost=output_data['cost_breakdown']['total'],
                status='draft'
            )

            from app import db
            db.session.add(proposal)
            db.session.flush()

            log_ai_interaction(
                module='proposal_generator',
                prompt=f"Generate proposal for {validated['client_name']} with budget ${validated['budget']}",
                response=output_data,
                proposal_id=proposal.id,
                latency_ms=ai_result.get('latency_ms'),
                success=True,
                auto_commit=False,
            )

            response = {
                'success': True,
                'data': {
                    'proposal': proposal.to_dict(),
                    'ai_analysis': output_data,
                    'budget_utilization': f"{ai_result.get('budget_utilization', 0):.1f}%",
                    'processing_time_ms': ai_result.get('latency_ms')
                }
            }
            return response, 201

        return self.idempotency.execute_once('proposals.generate', idempotency_key, validated, executor)
