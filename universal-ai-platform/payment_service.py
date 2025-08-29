"""
Simple Flask API to integrate MTN Payment with the Dashboard
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the payment directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'payment'))

from mtn_payment import MTNMobileMoneyPayment, PaymentRequest
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MTN payment handler
mtn_payment = MTNMobileMoneyPayment(
    environment="sandbox",  # Change to "production" for live
    target_environment="mtnliberia"
)

@app.route('/api/payment/mtn', methods=['POST'])
def process_mtn_payment():
    """Process MTN Mobile Money payment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'phone_number', 'reference_id', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create payment request
        payment_request = PaymentRequest(
            amount=float(data['amount']),
            currency=data.get('currency', 'USD'),
            phone_number=data['phone_number'],
            reference_id=data['reference_id'],
            description=data['description']
        )
        
        logger.info(f"Processing payment: {payment_request.reference_id} for ${payment_request.amount}")
        
        # Process payment
        result = mtn_payment.request_payment(payment_request)
        
        if result.success:
            logger.info(f"Payment initiated successfully: {result.transaction_id}")
            return jsonify({
                'success': True,
                'transaction_id': result.transaction_id,
                'status': result.status,
                'message': result.message,
                'reference_id': result.reference_id
            })
        else:
            logger.error(f"Payment failed: {result.message}")
            return jsonify({
                'success': False,
                'error': result.message,
                'status': result.status
            }), 400
            
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/payment/status/<transaction_id>', methods=['GET'])
def check_payment_status(transaction_id):
    """Check payment status"""
    try:
        status = mtn_payment.check_payment_status(transaction_id)
        return jsonify({
            'transaction_id': transaction_id,
            'status': status.status,
            'message': status.message
        })
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({
            'error': 'Failed to check payment status'
        }), 500

@app.route('/api/webhook/mtn', methods=['POST'])
def mtn_webhook():
    """Handle MTN payment webhooks"""
    try:
        data = request.get_json()
        logger.info(f"Received MTN webhook: {data}")
        
        # In a real implementation, you'd verify the webhook signature
        # and then call the dashboard webhook endpoint
        
        # Forward to dashboard webhook
        import requests
        dashboard_webhook_url = "http://localhost:3000/api/webhooks/mtn"
        
        response = requests.post(dashboard_webhook_url, json=data)
        
        if response.status_code == 200:
            return jsonify({'status': 'success'})
        else:
            logger.error(f"Dashboard webhook failed: {response.text}")
            return jsonify({'status': 'error'}), 500
            
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({'status': 'error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MTN Payment Service',
        'environment': mtn_payment.environment
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
