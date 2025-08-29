"""
MTN Mobile Money Payment Service for NexusAI
Handles credit purchases and integrates with the dashboard
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the payment directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'payment'))

from mtn_payment import MTNMobileMoneyPayment, PaymentRequest
import logging
import requests

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
        
        # For testing, we'll simulate the payment process
        # In production, this would call the actual MTN API
        if data.get('test_mode', True):
            # Simulate successful payment for testing
            result_data = {
                'success': True,
                'transaction_id': f"mtn_{payment_request.reference_id}",
                'status': 'processing',
                'message': 'Payment initiated successfully',
                'reference_id': payment_request.reference_id
            }
            
            # Simulate webhook callback after 3 seconds (in real scenario, this comes from MTN)
            import threading
            import time
            
            def simulate_webhook():
                time.sleep(3)  # Wait 3 seconds
                webhook_data = {
                    "transaction_id": result_data['transaction_id'],
                    "reference_id": payment_request.reference_id,
                    "status": "completed",
                    "amount": payment_request.amount,
                    "currency": payment_request.currency,
                    "message": "Payment completed successfully"
                }
                
                # Call dashboard webhook
                try:
                    dashboard_url = data.get('webhook_url', 'http://localhost:3000/api/webhooks/mtn')
                    response = requests.post(dashboard_url, json=webhook_data, timeout=10)
                    logger.info(f"Webhook sent to dashboard: {response.status_code}")
                except Exception as e:
                    logger.error(f"Failed to send webhook: {str(e)}")
            
            # Start webhook simulation in background
            webhook_thread = threading.Thread(target=simulate_webhook)
            webhook_thread.daemon = True
            webhook_thread.start()
            
            return jsonify(result_data)
        else:
            # Process real payment
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
        # For testing, return completed status
        if transaction_id.startswith('mtn_'):
            return jsonify({
                'transaction_id': transaction_id,
                'status': 'completed',
                'message': 'Payment completed successfully'
            })
        
        # In production, check with MTN
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MTN Payment Service',
        'environment': mtn_payment.environment,
        'version': '1.0.0'
    })

@app.route('/test/simulate-payment', methods=['POST'])
def simulate_test_payment():
    """Simulate a payment for testing purposes"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id', 'test_tx_123')
        reference_id = data.get('reference_id', 'test_ref_123')
        amount = data.get('amount', 9.00)
        
        # Simulate successful webhook
        webhook_data = {
            "transaction_id": transaction_id,
            "reference_id": reference_id,
            "status": "completed",
            "amount": amount,
            "currency": "USD",
            "message": "Test payment completed"
        }
        
        dashboard_url = data.get('webhook_url', 'http://localhost:3000/api/webhooks/mtn')
        response = requests.post(dashboard_url, json=webhook_data, timeout=10)
        
        return jsonify({
            'success': True,
            'message': 'Test payment simulated',
            'webhook_response': response.status_code
        })
        
    except Exception as e:
        logger.error(f"Test simulation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8002))
    app.run(host='0.0.0.0', port=port, debug=True)
