from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ValidationError, StrictStr, StrictInt, StrictFloat, conlist, confloat, constr


class ProductCategorizeRequest(BaseModel):
    sku: constr(strip_whitespace=True, min_length=1, max_length=255)
    name: constr(strip_whitespace=True, min_length=1, max_length=500)
    description: constr(strip_whitespace=True, min_length=1, max_length=5000)
    price: confloat(gt=0)


class ProposalGenerateRequest(BaseModel):
    client_name: constr(strip_whitespace=True, min_length=1, max_length=500)
    budget: confloat(gt=0)
    preferences: Optional[Dict[str, Any]] = None


class OrderCreateRequest(BaseModel):
    order_id: constr(strip_whitespace=True, min_length=1, max_length=255)
    customer_name: constr(strip_whitespace=True, min_length=1, max_length=500)
    total_amount: confloat(gt=0)
    products: List[Dict[str, Any]]
    status: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = 'pending'


class WhatsAppMessageRequest(BaseModel):
    customer_id: constr(strip_whitespace=True, min_length=1, max_length=255)
    message: constr(strip_whitespace=True, min_length=1, max_length=1000)


class WhatsAppWebhookPayload(BaseModel):
    customer_id: constr(strip_whitespace=True, min_length=1, max_length=255)
    message: constr(strip_whitespace=True, min_length=1, max_length=1000)
    timestamp: StrictInt
    event_id: constr(strip_whitespace=True, min_length=1, max_length=255)


class CategoryMetadataOutput(BaseModel):
    primary_category: StrictStr
    sub_category: StrictStr
    seo_tags: conlist(StrictStr, min_items=5, max_items=10)
    sustainability_filters: List[StrictStr]
    reasoning: StrictStr


class ProposalCostBreakdown(BaseModel):
    products_total: confloat(ge=0)
    sustainability_premium: confloat(ge=0)
    estimated_shipping: confloat(ge=0)
    total: confloat(ge=0)


class ProposalImpactPositioning(BaseModel):
    environmental_benefit: StrictStr
    business_value: StrictStr
    brand_alignment: StrictStr


class ProposalProductMixItem(BaseModel):
    product_id: StrictInt
    product_name: StrictStr
    quantity: StrictInt
    unit_price: confloat(ge=0)
    subtotal: confloat(ge=0)
    rationale: StrictStr


class ProposalOutput(BaseModel):
    proposal_summary: StrictStr
    product_mix: List[ProposalProductMixItem]
    cost_breakdown: ProposalCostBreakdown
    impact_positioning: ProposalImpactPositioning
    client_recommendation: StrictStr


class ImpactOutput(BaseModel):
    plastic_saved_kg: confloat(ge=0)
    plastic_avoided_percentage: confloat(ge=0)
    carbon_avoided_kg: confloat(ge=0)
    carbon_avoided_metric_tons_equivalent: confloat(ge=0)
    local_sourcing_percentage: confloat(ge=0)
    local_suppliers_count: StrictInt
    impact_statement: StrictStr
    equivalent_actions: List[StrictStr]


def validate_schema(schema, data: dict):
    try:
        parsed = schema(**data)
        return True, parsed.dict(), None
    except ValidationError as error:
        return False, None, error.errors()
