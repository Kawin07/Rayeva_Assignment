from app.errors import APIError
from app.models import Order
from app.modules import ImpactReportingGenerator
from app.tasks import queue
from app.utils import validate_schema, OrderCreateRequest, ImpactOutput, log_ai_interaction
from .idempotency_service import IdempotencyService


class OrderService:
    def __init__(self):
        self.idempotency = IdempotencyService()

    def list_orders(self):
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return {
            'success': True,
            'data': [order.to_dict() for order in orders],
            'count': len(orders)
        }, 200

    def create_order(self, payload: dict, idempotency_key: str = ''):
        is_valid, validated, details = validate_schema(OrderCreateRequest, payload)
        if not is_valid:
            raise APIError('VALIDATION_ERROR', 'Invalid order payload', 400)

        def executor():
            from app import db
            order = Order(
                order_id=validated['order_id'],
                customer_name=validated['customer_name'],
                total_amount=validated['total_amount'],
                products=validated['products'],
                status=validated.get('status', 'pending')
            )

            db.session.add(order)
            db.session.flush()

            return {'success': True, 'data': order.to_dict()}, 201

        return self.idempotency.execute_once('orders.create', idempotency_key, validated, executor)

    def generate_impact_report(self, order_id: int):
        from app import db
        order = Order.query.get(order_id)
        if not order:
            raise APIError('NOT_FOUND', 'Order not found', 404)

        generator = ImpactReportingGenerator()
        task_result = queue.submit(
            'impact_report_generate',
            generator.generate_impact_report,
            {
                'order_id': order.order_id,
                'products': order.products or [],
                'total_amount': order.total_amount,
            }
        )
        if not task_result.success:
            raise APIError('AI_UNAVAILABLE', 'Unable to generate impact report', 503)

        ai_result = task_result.data
        if not ai_result.get('success'):
            raise APIError('AI_GENERATION_FAILED', 'Impact report generation failed', 502)

        output_valid, output_data, output_errors = validate_schema(ImpactOutput, ai_result.get('data', {}))
        if not output_valid:
            raise APIError('AI_SCHEMA_INVALID', 'Impact response schema invalid', 502)

        order.plastic_saved_kg = output_data.get('plastic_saved_kg', 0)
        order.carbon_avoided_kg = output_data.get('carbon_avoided_kg', 0)
        order.local_sourcing_percentage = output_data.get('local_sourcing_percentage', 0)
        order.impact_statement = output_data.get('impact_statement')
        db.session.commit()

        log_ai_interaction(
            module='impact_reporter',
            prompt=f"Generate impact report for order {order.order_id}",
            response=output_data,
            order_id=order.id,
            latency_ms=ai_result.get('latency_ms'),
            success=True,
            auto_commit=True,
        )

        return {
            'success': True,
            'data': {
                'order': order.to_dict(),
                'impact_report': output_data,
                'processing_time_ms': ai_result.get('latency_ms')
            }
        }, 200
