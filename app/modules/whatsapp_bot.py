from .ai_client import AIClient
from app.utils import setup_logger
from app.utils import log_ai_interaction
from app.models import Order

logger = setup_logger('whatsapp_support_bot')

class WhatsAppSupportBot:
    RETURN_POLICY = {
        "days": 30,
        "condition": "Unused and in original packaging",
        "refund_percentage": 100,
        "exceptions": [
            "Customized items",
            "Items with signs of use or damage",
            "Items without original packaging"
        ]
    }

    SUPPORT_ESCALATION_KEYWORDS = [
        'refund', 'damaged', 'complaint', 'broken', 'wrong', 
        'not received', 'quality issue', 'urgent'
    ]

    def __init__(self):
        self.ai_client = AIClient()

    def handle_customer_message(self, customer_id, message):
        intent = self._classify_intent(message)
        logger.info(f"Customer {customer_id}: {intent} - {message[:50]}")

        if intent == "order_status":
            result = self._handle_order_status(customer_id, message)
        elif intent == "return_policy":
            result = self._handle_return_policy(message)
        elif intent == "return_request":
            result = self._handle_return_request(customer_id, message)
        elif intent == "escalate":
            result = self._escalate_to_support(customer_id, message)
        else:
            result = self._handle_general_inquiry(message)

        self.log_conversation(customer_id, message, result.get('response', ''), result.get('intent', intent), result.get('success', False))
        return result

    def _classify_intent(self, message):
        message_lower = message.lower()

        if any(word in message_lower for word in ['status', 'order', 'track', 'when', 'where']):
            return "order_status"
        elif any(word in message_lower for word in ['return', 'refund']):
            return "return_policy"
        elif any(word in message_lower for word in ['want to return', 'process return']):
            return "return_request"
        elif any(word in message_lower for word in self.SUPPORT_ESCALATION_KEYWORDS):
            return "escalate"
        else:
            return "general"

    def _handle_order_status(self, customer_id, message):
        customer_text = str(customer_id).strip()
        matched_orders = Order.query.filter(Order.customer_name == customer_text).order_by(Order.created_at.desc()).limit(5).all()

        if not matched_orders:
            matched_orders = Order.query.filter(Order.order_id == customer_text).order_by(Order.created_at.desc()).limit(5).all()

        if not matched_orders:
            response_text = "I could not find recent orders for this customer ID. Share your exact order ID for a precise status update."
            return {
                'success': True,
                'response': response_text,
                'intent': 'order_status',
                'escalation_needed': False
            }

        order_lines = []
        for order in matched_orders:
            item_count = len(order.products or [])
            order_lines.append(f"Order #{order.order_id} | Status: {order.status} | Items: {item_count} | Total: ${order.total_amount:.2f}")

        response_text = "\n".join(["Order status details:", *order_lines, "Reply with an order ID if you want a single-order breakdown."])

        return {
            'success': True,
            'response': response_text,
            'intent': 'order_status',
            'escalation_needed': False
        }

    def _handle_return_policy(self, message):
        policy = self.RETURN_POLICY

        response_text = f"""↩️ Return Policy

We want you to be satisfied! Here's our policy:

📅 Return Window: {policy['days']} days from purchase
📦 Condition: {policy['condition']}
💰 Refund: {policy['refund_percentage']}% refund

Exceptions:
{chr(10).join(f'• {exc}' for exc in policy['exceptions'])}

Need help with a return? Reply with "I want to return an order"
"""

        return {
            'success': True,
            'response': response_text,
            'intent': 'return_policy',
            'escalation_needed': False
        }

    def _handle_return_request(self, customer_id, message):
        response_text = """✅ Return Request Initiated

Thank you! We've received your return request.

Next steps:
1. You'll receive a return label via email within 2 hours
2. Pack the item securely
3. Drop off at any shipping location
4. Refund processed within 5-7 business days of receipt

Your Reference: RET-2024-001234
📧 Check your email for return label

Questions? Reply here or email support@rayeva.com"""

        return {
            'success': True,
            'response': response_text,
            'intent': 'return_request',
            'escalation_needed': False,
            'action': 'create_return_ticket'
        }

    def _escalate_to_support(self, customer_id, message):
        response_text = """👥 Escalating to Support Team

We're connecting you with our specialist team to help resolve this.

Your message has been forwarded to support@rayeva.com
Expected response time: 2-4 hours

Thank you for your patience! 🙏
"""

        return {
            'success': True,
            'response': response_text,
            'intent': 'escalate',
            'escalation_needed': True,
            'action': 'create_support_ticket'
        }

    def _handle_general_inquiry(self, message):
        system_prompt = """You are a friendly, helpful customer support representative for Rayeva, 
an eco-friendly sustainable commerce platform. 

Keep responses concise (2-3 sentences), friendly, and focused on helping the customer.
Always offer relevant next steps."""

        user_message = f"Customer question: {message}"

        response = self.ai_client.call_claude(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )

        if response['success']:
            return {
                'success': True,
                'response': response['response'],
                'intent': 'general',
                'escalation_needed': False
            }
        else:
            return {
                'success': False,
                'response': "I'm having trouble processing your request. Please try again or contact support@rayeva.com",
                'intent': 'general',
                'escalation_needed': True
            }

    def log_conversation(self, customer_id, message, response, intent, success):
        log_ai_interaction(
            module='whatsapp_support',
            prompt=f"Customer {customer_id}: {message}",
            response={
                'intent': intent,
                'response': response
            },
            success=success
        )
        logger.info(f"Conversation logged - Customer: {customer_id}, Intent: {intent}")
