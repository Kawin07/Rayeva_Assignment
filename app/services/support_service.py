from flask import current_app
from app.errors import APIError
from app.modules import WhatsAppSupportBot
from app.utils import validate_schema, WhatsAppMessageRequest, WhatsAppWebhookPayload, sanitize_text


class SupportService:
    def handle_whatsapp_message(self, payload: dict):
        is_valid, validated, details = validate_schema(WhatsAppMessageRequest, payload)
        if not is_valid:
            raise APIError('VALIDATION_ERROR', 'Invalid support payload', 400)

        max_length = int(current_app.config.get('WHATSAPP_MESSAGE_MAX_LENGTH', 1000))
        clean_message = sanitize_text(validated['message'], max_length)

        bot = WhatsAppSupportBot()
        result = bot.handle_customer_message(validated['customer_id'], clean_message)
        if not result.get('success'):
            raise APIError('SUPPORT_UNAVAILABLE', 'Unable to process support request', 503)

        return {
            'success': True,
            'data': result
        }, 200

    def handle_whatsapp_webhook(self, payload: dict):
        is_valid, validated, details = validate_schema(WhatsAppWebhookPayload, payload)
        if not is_valid:
            raise APIError('VALIDATION_ERROR', 'Invalid webhook payload', 400)

        max_length = int(current_app.config.get('WHATSAPP_MESSAGE_MAX_LENGTH', 1000))
        clean_message = sanitize_text(validated['message'], max_length)

        bot = WhatsAppSupportBot()
        result = bot.handle_customer_message(validated['customer_id'], clean_message)
        if not result.get('success'):
            raise APIError('SUPPORT_UNAVAILABLE', 'Unable to process webhook event', 503)

        return {
            'success': True,
            'data': {
                'event_id': validated['event_id'],
                'result': result,
            }
        }, 200
