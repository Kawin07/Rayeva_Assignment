from sqlalchemy.exc import IntegrityError
from app import db
from app.errors import APIError
from app.models import Product
from app.modules import AutoCategoryGenerator
from app.tasks import queue
from app.utils import validate_schema, ProductCategorizeRequest, CategoryMetadataOutput, log_ai_interaction


class ProductService:
    def categorize_product(self, payload: dict):
        is_valid, validated, details = validate_schema(ProductCategorizeRequest, payload)
        if not is_valid:
            raise APIError('VALIDATION_ERROR', 'Invalid product payload', 400)

        generator = AutoCategoryGenerator()
        task_result = queue.submit(
            'auto_category_generate',
            generator.generate_metadata,
            validated['name'],
            validated['description'],
            validated.get('price')
        )
        if not task_result.success:
            raise APIError('AI_UNAVAILABLE', 'Unable to process categorization', 503)

        ai_result = task_result.data
        if not ai_result.get('success'):
            raise APIError('AI_GENERATION_FAILED', 'Unable to generate category metadata', 502)

        output_valid, output_data, output_errors = validate_schema(CategoryMetadataOutput, ai_result.get('data', {}))
        if not output_valid:
            raise APIError('AI_SCHEMA_INVALID', 'AI response schema invalid', 502)

        product = Product(
            sku=validated['sku'],
            name=validated['name'],
            description=validated['description'],
            price=validated['price'],
            primary_category=output_data.get('primary_category'),
            sub_category=output_data.get('sub_category'),
            seo_tags=output_data.get('seo_tags'),
            sustainability_filters=output_data.get('sustainability_filters'),
        )

        try:
            db.session.add(product)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise APIError('DUPLICATE_RESOURCE', 'SKU already exists', 409)

        log_ai_interaction(
            module='auto_category',
            prompt=f"Categorize: {validated['name']} - {validated['description']}",
            response=output_data,
            product_id=product.id,
            latency_ms=ai_result.get('latency_ms'),
            success=True,
        )

        return {
            'success': True,
            'data': {
                'product': product.to_dict(),
                'ai_metadata': output_data,
                'processing_time_ms': ai_result.get('latency_ms')
            }
        }, 201
