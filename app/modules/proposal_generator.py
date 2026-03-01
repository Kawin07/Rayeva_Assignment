from .ai_client import AIClient
import json
from app.utils import setup_logger
from app.models import Product

logger = setup_logger('proposal_generator')

class ProposalGenerator:
    def __init__(self):
        self.ai_client = AIClient()

    def generate_proposal(self, client_name, budget, preferences=None):
        products = Product.query.limit(20).all()
        product_catalog = json.dumps([p.to_dict() for p in products], default=str)

        system_prompt = f"""You are an expert B2B sales consultant specializing in sustainable products.

Your task is to create compelling B2B proposals with:
1. Curated product mix that aligns with sustainability values
2. Budget allocation optimizing for quality and cost
3. Detailed cost breakdown
4. Impact positioning (environmental, social, business benefits)

AVAILABLE PRODUCT CATALOG:
{product_catalog}

Return a JSON response with this structure:
{{
    "proposal_summary": "executive summary of the recommendation",
    "product_mix": [
        {{
            "product_id": integer,
            "product_name": string,
            "quantity": integer,
            "unit_price": float,
            "subtotal": float,
            "rationale": "why this product was selected"
        }}
    ],
    "cost_breakdown": {{
        "products_total": float,
        "sustainability_premium": float,
        "estimated_shipping": float,
        "total": float
    }},
    "impact_positioning": {{
        "environmental_benefit": "summary of environmental impact",
        "business_value": "ROI and business benefits",
        "brand_alignment": "how this supports sustainable brand values"
    }},
    "client_recommendation": "personalized recommendation message"
}}

Ensure the total cost does not exceed the provided budget."""
        
        user_message = f"""Generate a B2B proposal for:

Client: {client_name}
Budget: ${budget}
Preferences: {json.dumps(preferences) if preferences else 'None specified'}

Create a compelling, detailed proposal that:
1. Maximizes sustainability impact within budget
2. Includes 3-7 well-chosen products
3. Provides clear ROI and business justification
4. Highlights environmental and social benefits

Return valid JSON only."""

        logger.info(f"Generating proposal for: {client_name}, Budget: ${budget}")

        response = self.ai_client.call_claude(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=2000
        )
        
        if not response['success']:
            logger.error(f"API call failed: {response['error']}")
            fallback = self._fallback_proposal(products, client_name, budget)
            return {
                'success': True,
                'data': fallback,
                'validation_errors': ['AI unavailable, fallback proposal used'],
                'budget_utilization': (fallback['cost_breakdown']['total'] / budget * 100) if budget > 0 else 0,
                'latency_ms': response.get('latency_ms', 0),
                'tokens_used': 0,
            }

        proposal_data = self.ai_client.parse_json_response(response['response'])

        if not proposal_data:
            logger.error("Failed to parse JSON response")
            proposal_data = self._fallback_proposal(products, client_name, budget)

        result = self._validate_proposal(proposal_data, budget)
        result['latency_ms'] = response['latency_ms']
        result['tokens_used'] = response['usage']['output_tokens']

        logger.info(f"Successfully generated proposal with {len(proposal_data.get('product_mix', []))} products")

        return result

    def _validate_proposal(self, proposal_data, budget):
        errors = []

        product_mix = proposal_data.get('product_mix', [])
        if not isinstance(product_mix, list):
            errors.append("product_mix must be a list")
            product_mix = []

        if len(product_mix) == 0:
            errors.append("product_mix must contain at least one product")

        cost_breakdown = proposal_data.get('cost_breakdown', {})
        total_cost = cost_breakdown.get('total', 0)

        if total_cost > budget:
            errors.append(f"Total cost (${total_cost}) exceeds budget (${budget})")

        impact = proposal_data.get('impact_positioning', {})
        if not impact:
            errors.append("impact_positioning is missing")
        
        return {
            'success': len(errors) == 0,
            'data': proposal_data,
            'validation_errors': errors if errors else None,
            'budget_utilization': (total_cost / budget * 100) if budget > 0 else 0
        }

    def _fallback_proposal(self, products, client_name, budget):
        remaining = budget
        mix = []
        for product in products[:5]:
            if product.price <= 0:
                continue
            max_qty = int(max(1, remaining // product.price))
            quantity = min(max_qty, 3)
            subtotal = round(quantity * product.price, 2)
            if subtotal <= 0 or subtotal > remaining:
                continue
            mix.append({
                'product_id': product.id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': float(product.price),
                'subtotal': subtotal,
                'rationale': 'Fallback selection optimized for budget coverage',
            })
            remaining -= subtotal
            if remaining <= 0:
                break

        products_total = round(sum(item['subtotal'] for item in mix), 2)
        shipping = round(min(150.0, max(0.0, products_total * 0.03)), 2)
        premium = round(min(200.0, max(0.0, products_total * 0.05)), 2)
        total = round(min(budget, products_total + shipping + premium), 2)

        return {
            'proposal_summary': f'Sustainable fallback proposal for {client_name}',
            'product_mix': mix,
            'cost_breakdown': {
                'products_total': products_total,
                'sustainability_premium': premium,
                'estimated_shipping': shipping,
                'total': total,
            },
            'impact_positioning': {
                'environmental_benefit': 'Focuses on reusable and low-waste product options',
                'business_value': 'Maintains budget discipline while supporting sustainability goals',
                'brand_alignment': 'Supports responsible procurement and ESG signaling',
            },
            'client_recommendation': 'Use this baseline proposal while AI insights recover.',
        }
