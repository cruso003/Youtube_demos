"""
Payment API Endpoints
Handles subscription management and payment processing
"""

from flask import Blueprint, request, jsonify
import logging
from billing.payment_processor import PaymentProcessor

logger = logging.getLogger(__name__)
payment_bp = Blueprint('payment', __name__)
payment_processor = PaymentProcessor()

@payment_bp.route("/api/v1/pricing/<country_code>", methods=["GET"])
def get_pricing(country_code: str):
    """Get pricing for a specific country"""
    try:
        plan_id = request.args.get('plan', 'starter')
        pricing = payment_processor.calculate_pricing_for_country(plan_id, country_code.upper())
        
        return jsonify({
            "status": "success",
            "pricing": pricing
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting pricing: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@payment_bp.route("/api/v1/payment-methods/<country_code>", methods=["GET"])
def get_payment_methods(country_code: str):
    """Get available payment methods for a country"""
    try:
        methods = payment_processor.get_available_payment_methods(country_code.upper())
        
        return jsonify({
            "status": "success",
            "country_code": country_code.upper(),
            "payment_methods": [
                {
                    "id": method.method_id,
                    "name": method.name,
                    "currency": method.currency,
                    "processing_fee": method.processing_fee
                }
                for method in methods
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting payment methods: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@payment_bp.route("/api/v1/subscription/create", methods=["POST"])
def create_subscription():
    """Create a new subscription"""
    try:
        data = request.get_json()
        
        required_fields = ["client_id", "plan_id", "payment_method", "country_code"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        subscription = payment_processor.create_subscription(
            client_id=data["client_id"],
            plan_id=data["plan_id"],
            payment_method_id=data["payment_method"],
            country_code=data["country_code"],
            billing_cycle=data.get("billing_cycle", "monthly")
        )
        
        return jsonify({
            "status": "success",
            "subscription": subscription,
            "message": "Subscription created. Complete payment to activate."
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@payment_bp.route("/api/v1/webhook/<provider>", methods=["POST"])
def payment_webhook(provider: str):
    """Handle payment webhooks from providers"""
    try:
        webhook_data = request.get_json()
        result = payment_processor.handle_webhook(provider, webhook_data)
        
        return jsonify({
            "status": "success",
            "result": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@payment_bp.route("/api/v1/plans", methods=["GET"])
def get_plans():
    """Get all available billing plans"""
    try:
        plans = [
            {
                "plan_id": "free",
                "name": "Free Tier",
                "price": 0,
                "features": [
                    "5 messages/day",
                    "1 session per IP", 
                    "Text only",
                    "Community support"
                ],
                "limits": {
                    "daily_messages": 5,
                    "rate_limit": "1/minute",
                    "capabilities": ["text"]
                }
            },
            {
                "plan_id": "starter", 
                "name": "Starter Plan",
                "price": 9,
                "features": [
                    "1,000 messages/month",
                    "All capabilities",
                    "Email support",
                    "API analytics"
                ],
                "limits": {
                    "monthly_messages": 1000,
                    "rate_limit": "60/minute",
                    "capabilities": ["text", "voice", "vision"]
                }
            },
            {
                "plan_id": "professional",
                "name": "Professional Plan", 
                "price": 29,
                "features": [
                    "10,000 messages/month",
                    "Priority support",
                    "Custom business adapters",
                    "Advanced analytics"
                ],
                "limits": {
                    "monthly_messages": 10000,
                    "rate_limit": "120/minute",
                    "capabilities": ["text", "voice", "vision"]
                }
            },
            {
                "plan_id": "enterprise",
                "name": "Enterprise Plan",
                "price": 99, 
                "features": [
                    "Unlimited messages",
                    "24/7 phone support",
                    "White-label option",
                    "Custom integrations"
                ],
                "limits": {
                    "monthly_messages": "unlimited",
                    "rate_limit": "unlimited",
                    "capabilities": ["text", "voice", "vision"]
                }
            }
        ]
        
        return jsonify({
            "status": "success",
            "plans": plans
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting plans: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
