"""
Payment API Endpoints
Handles subscription management, payment processing, and credit purchases
"""

from flask import Blueprint, request, jsonify
import logging
from billing.payment_processor import PaymentProcessor

logger = logging.getLogger(__name__)
payment_bp = Blueprint('payment', __name__)
payment_processor = PaymentProcessor()

@payment_bp.route("/api/v1/pricing/<country_code>", methods=["GET"])
def get_pricing(country_code: str):
    """Get credit pricing for a specific country"""
    try:
        # Return credit pricing information
        base_rate = 1000  # credits per USD
        minimum_purchase = 5.00  # minimum $5.00
        
        pricing = {
            "country_code": country_code.upper(),
            "currency": "USD",
            "credit_rate": base_rate,
            "minimum_purchase": minimum_purchase,
            "suggested_amounts": {
                "starter": {"amount": 5.0, "credits": 5000},
                "standard": {"amount": 10.0, "credits": 10000},
                "premium": {"amount": 50.0, "credits": 50000}
            }
        }
        
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

@payment_bp.route("/api/v1/credits/packages", methods=["GET"])
def get_credit_packages():
    """Get available credit packages"""
    try:
        packages = payment_processor.get_credit_packages()
        return jsonify({
            "status": "success",
            "packages": packages
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting credit packages: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@payment_bp.route("/api/v1/credits/purchase", methods=["POST"])
def purchase_credits():
    """Purchase credits via mobile money with custom amount"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'phone_number', 'user_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Validate amount
        amount = float(data['amount'])
        if amount < 5.00:
            return jsonify({
                "status": "error",
                "message": "Minimum purchase amount is $5.00"
            }), 400
        
        result = payment_processor.process_credit_purchase(
            amount=amount,
            phone_number=data['phone_number'],
            user_id=data['user_id'],
            country_code=data.get('country_code', 'LR')
        )
        
        if result['success']:
            return jsonify({
                "status": "success",
                **result
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": result.get('error', 'Payment failed')
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing credit purchase: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
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

# Legacy endpoints removed - now using credit system
# Use /api/v1/credits/purchase for purchasing credits
# Use /api/v1/credits/packages for available credit packages
