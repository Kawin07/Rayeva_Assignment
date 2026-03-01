from .ai_client import AIClient
import json
from app.utils import setup_logger

logger = setup_logger('auto_category_generator')

class AutoCategoryGenerator:
    PREDEFINED_CATEGORIES = [
        "Apparel & Accessories",
        "Home & Garden",
        "Food & Beverage",
        "Personal Care",
        "Office Supplies",
        "Packaging & Shipping",
        "Electronics",
        "Toys & Games",
        "Sports & Outdoors"
    ]
    
    SUSTAINABILITY_FILTERS = [
        "plastic-free",
        "compostable",
        "vegan",
        "recycled",
        "biodegradable",
        "fair-trade",
        "organic",
        "zero-waste",
        "renewable",
        "locally-sourced"
    ]
    
    def __init__(self):
        self.ai_client = AIClient()

    def generate_metadata(self, product_name, description, price=None):
        system_prompt = f"""You are an expert e-commerce categorization AI specializing in sustainable products.
        
Your task is to categorize products and generate SEO metadata.

PREDEFINED CATEGORIES (choose one as primary):
{json.dumps(self.PREDEFINED_CATEGORIES)}

AVAILABLE SUSTAINABILITY FILTERS (select all that apply):
{json.dumps(self.SUSTAINABILITY_FILTERS)}

Return a JSON response with exactly this structure:
{{
    "primary_category": "string (one of the predefined categories)",
    "sub_category": "string (specific subcategory within primary)",
    "seo_tags": ["tag1", "tag2", ...] (5-10 relevant SEO tags),
    "sustainability_filters": ["filter1", "filter2", ...] (all applicable filters),
    "reasoning": "brief explanation of categorization choices"
}}

Be concise, accurate, and focus on sustainability aspects where relevant."""
        
        user_message = f"""Please categorize this product:

Product Name: {product_name}
Description: {description}
Price: ${price if price else 'Not specified'}

Analyze and provide complete metadata in the specified JSON format."""

        logger.info(f"Generating metadata for: {product_name}")

        response = self.ai_client.call_claude(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        if not response['success']:
            logger.error(f"API call failed: {response['error']}")
            fallback = self._fallback_metadata(product_name, description)
            return {
                'success': True,
                'data': fallback,
                'validation_errors': ['AI unavailable, fallback metadata used'],
                'latency_ms': response.get('latency_ms', 0),
                'tokens_used': 0,
            }

        metadata = self.ai_client.parse_json_response(response['response'])

        if not metadata:
            logger.error("Failed to parse JSON response")
            metadata = self._fallback_metadata(product_name, description)

        result = self._validate_metadata(metadata)
        result['latency_ms'] = response['latency_ms']
        result['tokens_used'] = response['usage']['output_tokens']

        logger.info(f"Successfully generated metadata: {result.get('primary_category')}")

        return result

    def _fallback_metadata(self, product_name, description):
        text = f"{product_name} {description}".lower()
        primary = 'Home & Garden'
        if any(keyword in text for keyword in ['toothbrush', 'soap', 'skincare', 'care']):
            primary = 'Personal Care'
        elif any(keyword in text for keyword in ['bag', 'shirt', 'wear', 'apparel']):
            primary = 'Apparel & Accessories'
        elif any(keyword in text for keyword in ['food', 'beverage', 'snack']):
            primary = 'Food & Beverage'

        filters = [flt for flt in self.SUSTAINABILITY_FILTERS if flt in text]
        if not filters:
            filters = ['recycled']

        tags = [
            product_name.lower().replace(' ', '-'),
            primary.lower().replace(' & ', '-').replace(' ', '-'),
            'sustainable',
            'eco-friendly',
            'green-commerce',
        ]

        return {
            'primary_category': primary,
            'sub_category': 'General',
            'seo_tags': tags[:5],
            'sustainability_filters': filters,
            'reasoning': 'Fallback classification based on product text patterns',
        }

    def _validate_metadata(self, metadata):
        errors = []

        if metadata.get('primary_category') not in self.PREDEFINED_CATEGORIES:
            errors.append(f"Invalid primary_category: {metadata.get('primary_category')}")
            metadata['primary_category'] = self.PREDEFINED_CATEGORIES[0]

        seo_tags = metadata.get('seo_tags', [])
        if not isinstance(seo_tags, list):
            errors.append("seo_tags must be a list")
            seo_tags = []
        if len(seo_tags) < 5 or len(seo_tags) > 10:
            errors.append(f"seo_tags must have 5-10 items, got {len(seo_tags)}")
        metadata['seo_tags'] = seo_tags[:10] if len(seo_tags) > 10 else seo_tags

        filters = metadata.get('sustainability_filters', [])
        if not isinstance(filters, list):
            errors.append("sustainability_filters must be a list")
            filters = []
        invalid_filters = [f for f in filters if f not in self.SUSTAINABILITY_FILTERS]
        if invalid_filters:
            errors.append(f"Invalid filters: {invalid_filters}")
        metadata['sustainability_filters'] = [f for f in filters if f in self.SUSTAINABILITY_FILTERS]
        
        return {
            'success': len(errors) == 0,
            'data': metadata,
            'validation_errors': errors if errors else None
        }
