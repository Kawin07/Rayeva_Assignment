from .ai_client import AIClient
import json
from app.utils import setup_logger

logger = setup_logger('impact_reporter')

class ImpactReportingGenerator:
    def __init__(self):
        self.ai_client = AIClient()

    def generate_impact_report(self, order_data):
        system_prompt = """You are an environmental impact analyst specializing in sustainable commerce.

Your task is to calculate realistic environmental impact metrics for orders based on product sustainability profiles.

Provide metrics in this JSON structure:
{
    "plastic_saved_kg": float,
    "plastic_avoided_percentage": float,
    "carbon_avoided_kg": float,
    "carbon_avoided_metric_tons_equivalent": float,
    "local_sourcing_percentage": float,
    "local_suppliers_count": integer,
    "impact_statement": "Human-readable summary",
    "equivalent_actions": ["action1: description", ...]
}

Be realistic with estimates:
- Each eco-conscious product typically saves 0.5-5kg plastic
- Carbon avoidance is ~5-10kg per eco-product
- Local sourcing varies by region (20-80%)
"""
        
        user_message = f"""Calculate impact for this order:

{json.dumps(order_data)}

Provide realistic environmental impact estimates and a compelling impact narrative."""

        logger.info(f"Generating impact report for order: {order_data.get('order_id')}")

        response = self.ai_client.call_claude(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=1000
        )
        
        if not response['success']:
            logger.error(f"API call failed: {response['error']}")
            fallback = self._calculate_baseline_impact(order_data)
            return {
                'success': True,
                'data': fallback,
                'latency_ms': response.get('latency_ms', 0)
            }

        impact_data = self.ai_client.parse_json_response(response['response'])

        if not impact_data:
            impact_data = self._calculate_baseline_impact(order_data)

        logger.info(f"Impact report generated: {impact_data.get('plastic_saved_kg')}kg plastic saved")

        return {
            'success': True,
            'data': impact_data,
            'latency_ms': response['latency_ms']
        }

    def _calculate_baseline_impact(self, order_data):
        products = order_data.get('products', [])

        plastic_saved = 0
        carbon_avoided = 0
        local_sourcing_percentage = 0

        for product in products:
            quantity = product.get('quantity', 1)
            filters = product.get('sustainability_filters', [])

            if 'plastic-free' in filters:
                plastic_saved += quantity * 0.5
                carbon_avoided += quantity * 2.5

            if 'locally-sourced' in filters:
                local_sourcing_percentage += 25

        local_sourcing_percentage = min(local_sourcing_percentage, 100)

        return {
            "plastic_saved_kg": round(plastic_saved, 1),
            "plastic_avoided_percentage": min(int(plastic_saved * 10), 100),
            "carbon_avoided_kg": round(carbon_avoided, 1),
            "carbon_avoided_metric_tons_equivalent": round(carbon_avoided / 1000, 4),
            "local_sourcing_percentage": local_sourcing_percentage,
            "local_suppliers_count": 2,
            "impact_statement": f"This sustainable choice saved {plastic_saved}kg of plastic from landfills",
            "equivalent_actions": [
                f"Planting {int(carbon_avoided / 10)} trees",
                f"Saving {plastic_saved}kg of plastic waste"
            ]
        }
