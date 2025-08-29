"""
NexusAI Payment Integration
Handles subscription management and payment processing for African market
Integrates with MTN Mobile Money and Dashboard
"""

import os
import json
import logging
import requests
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from billing.usage_tracker import UsageTracker, BillingPlan
from payment.mtn_payment import MTNMobileMoneyPayment, CreditManager

# Import MTN payment handler
try:
    from payment.mtn_payment import MTNMobileMoneyPayment, PaymentRequest
except ImportError:
    print("Warning: MTN payment module not found")
    MTNMobileMoneyPayment = None
    PaymentRequest = None

logger = logging.getLogger(__name__)

@dataclass
class PaymentMethod:
    """Payment method configuration for African market"""
    method_id: str
    name: str
    supported_countries: List[str]
    currency: str
    processing_fee: float  # Percentage
    
class PaymentProcessor:
    """Payment processing for African market"""
    
    def __init__(self):
        self.usage_tracker = UsageTracker()
        self.credit_manager = CreditManager()  # Add credit manager for storing/retrieving credits
        
        # African-focused payment methods
        self.payment_methods = {
            "mpesa": PaymentMethod(
                method_id="mpesa",
                name="M-Pesa",
                supported_countries=["KE", "TZ", "UG", "GH"],
                currency="USD",  # We'll handle conversion
                processing_fee=0.025  # 2.5%
            ),
            "mtn_momo": PaymentMethod(
                method_id="mtn_momo",
                name="MTN Mobile Money",
                supported_countries=["GH", "UG", "RW", "ZM"],
                currency="USD",
                processing_fee=0.03  # 3%
            ),
            "flutterwave": PaymentMethod(
                method_id="flutterwave",
                name="Flutterwave (Cards)",
                supported_countries=["NG", "GH", "KE", "UG", "TZ", "RW", "ZA"],
                currency="USD",
                processing_fee=0.029  # 2.9%
            ),
            "paystack": PaymentMethod(
                method_id="paystack", 
                name="Paystack (Cards)",
                supported_countries=["NG", "GH", "ZA"],
                currency="USD",
                processing_fee=0.027  # 2.7%
            )
        }
    
    def get_available_payment_methods(self, country_code: str) -> List[PaymentMethod]:
        """Get payment methods available for a country"""
        available = []
        for method in self.payment_methods.values():
            if country_code in method.supported_countries:
                available.append(method)
        return available
    
    def calculate_pricing_for_country(self, plan_id: str, country_code: str) -> Dict:
        """Calculate pricing with African market adjustments"""
        base_plans = {
            "starter": {"monthly": 9, "yearly": 90},    # 2 months free
            "professional": {"monthly": 29, "yearly": 290},  
            "enterprise": {"monthly": 99, "yearly": 990}
        }
        
        # African market pricing adjustments
        country_multipliers = {
            # West Africa
            "NG": 0.7,  # Nigeria - 30% discount
            "GH": 0.8,  # Ghana - 20% discount  
            "SN": 0.8,  # Senegal
            "CI": 0.8,  # Ivory Coast
            
            # East Africa  
            "KE": 0.75, # Kenya - 25% discount
            "UG": 0.7,  # Uganda - 30% discount
            "TZ": 0.7,  # Tanzania
            "RW": 0.8,  # Rwanda
            
            # Southern Africa
            "ZA": 0.9,  # South Africa - 10% discount
            "ZW": 0.6,  # Zimbabwe - 40% discount
            
            # Default for other countries
            "default": 1.0
        }
        
        multiplier = country_multipliers.get(country_code, country_multipliers["default"])
        base_price = base_plans.get(plan_id, base_plans["starter"])
        
        return {
            "plan_id": plan_id,
            "country_code": country_code,
            "monthly_price": round(base_price["monthly"] * multiplier, 2),
            "yearly_price": round(base_price["yearly"] * multiplier, 2),
            "currency": "USD",
            "discount_percentage": round((1 - multiplier) * 100, 0),
            "available_payment_methods": [m.name for m in self.get_available_payment_methods(country_code)]
        }
    
    def create_subscription(self, client_id: str, plan_id: str, payment_method_id: str, 
                          country_code: str, billing_cycle: str = "monthly") -> Dict:
        """Create a new subscription"""
        
        pricing = self.calculate_pricing_for_country(plan_id, country_code)
        price = pricing["monthly_price"] if billing_cycle == "monthly" else pricing["yearly_price"]
        
        # In a real implementation, you would:
        # 1. Create payment intent with chosen provider (Flutterwave, Paystack, etc.)
        # 2. Handle payment confirmation
        # 3. Create subscription record
        
        subscription = {
            "subscription_id": f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{client_id}",
            "client_id": client_id,
            "plan_id": plan_id,
            "status": "pending_payment",
            "price": price,
            "currency": "USD",
            "billing_cycle": billing_cycle,
            "payment_method": payment_method_id,
            "country_code": country_code,
            "created_at": datetime.now().isoformat(),
            "next_billing_date": (datetime.now() + timedelta(days=30 if billing_cycle == "monthly" else 365)).isoformat()
        }
        
        return subscription
    
    def handle_webhook(self, provider: str, webhook_data: Dict) -> Dict:
        """Handle payment webhook from providers"""
        
        if provider == "flutterwave":
            return self._handle_flutterwave_webhook(webhook_data)
        elif provider == "paystack":
            return self._handle_paystack_webhook(webhook_data)
        elif provider == "mpesa":
            return self._handle_mpesa_webhook(webhook_data)
        
        return {"status": "unsupported_provider"}
    
    def _handle_flutterwave_webhook(self, webhook_data: Dict) -> Dict:
        """Handle Flutterwave payment webhook"""
        # Example Flutterwave webhook handling
        event = webhook_data.get("event")
        data = webhook_data.get("data", {})
        
        if event == "charge.completed":
            transaction_id = data.get("id")
            status = data.get("status")
            amount = data.get("amount")
            customer_email = data.get("customer", {}).get("email")
            
            if status == "successful":
                # Activate subscription
                return {
                    "status": "subscription_activated",
                    "transaction_id": transaction_id,
                    "amount": amount,
                    "customer_email": customer_email
                }
        
        return {"status": "webhook_processed"}
    
    def _handle_paystack_webhook(self, webhook_data: Dict) -> Dict:
        """Handle Paystack payment webhook"""
        # Similar to Flutterwave but with Paystack's webhook format
        event = webhook_data.get("event")
        data = webhook_data.get("data", {})
        
        if event == "charge.success":
            # Activate subscription
            return {"status": "subscription_activated"}
            
        return {"status": "webhook_processed"}
    
    def _handle_mpesa_webhook(self, webhook_data: Dict) -> Dict:
        """Handle M-Pesa payment webhook"""
        # M-Pesa specific webhook handling
        result_code = webhook_data.get("ResultCode")
        
        if result_code == "0":  # Success
            return {"status": "subscription_activated"}
            
        return {"status": "payment_failed"}

    # Credit Purchase Methods
    def get_credit_packages(self) -> Dict:
        """Get available credit packages (for reference) and credit conversion rate"""
        return {
            # Credit conversion rate: 1000 credits per $1
            "credit_rate": 1000,  # credits per USD
            "minimum_purchase": 5.00,  # minimum $5.00 for production
            "currency": "USD",
            
            # Reference packages (optional, for UI convenience)
            "suggested_packages": {
                "starter": {
                    "amount": 5.0,
                    "credits": 5000,
                    "description": "5,000 NexusAI Credits - Perfect for trying our service"
                },
                "standard": {
                    "amount": 10.0,
                    "credits": 10000,
                    "description": "10,000 NexusAI Credits - Great for regular use"
                },
                "premium": {
                    "amount": 50.0,
                    "credits": 50000,
                    "description": "50,000 NexusAI Credits - Best value for power users"
                }
            }
        }
    
    def process_credit_purchase(self, amount: float, phone_number: str, user_id: str, country_code: str = "LR") -> Dict:
        """Process credit purchase via MTN Mobile Money with custom amount"""
        try:
            # Convert amount to float if it's a string
            amount = float(amount)
            
            credit_info = self.get_credit_packages()
            
            # Validate minimum amount
            if amount < credit_info["minimum_purchase"]:
                return {"success": False, "error": f"Minimum purchase is ${credit_info['minimum_purchase']}"}
            
            # Calculate credits based on amount
            credits_to_add = int(amount * credit_info["credit_rate"])
            
            # Initialize MTN payment if available
            if MTNMobileMoneyPayment:
                try:
                    mtn_payment = MTNMobileMoneyPayment(
                        subscription_key=os.getenv('MTN_SUBSCRIPTION_KEY', 'b60e7311554c49948e4b4be2f0b268b3'),
                        api_user=os.getenv('MTN_API_USER', 'd12bc032-0a43-4bfd-88c7-a4b0a4ea149d'),
                        api_key=os.getenv('MTN_API_KEY', '6f1926714253462eb67a226162809a28'),
                        environment="production",  # Use production for live payments
                        target_environment="mtnliberia"
                    )
                    
                    # Generate unique reference ID
                    # Generate proper UUID for MTN payment reference
                    reference_id = str(uuid.uuid4())
                    
                    # Process payment with custom amount
                    result = mtn_payment.request_payment_custom(
                        phone_number=phone_number,
                        amount=amount,
                        user_id=user_id,
                        reference_id=reference_id,
                        description=f"{credits_to_add} NexusAI Credits (${amount})"
                    )
                except Exception as e:
                    print(f"MTN Payment initialization/processing error: {e}")
                    import traceback
                    traceback.print_exc()
                    return {"success": False, "error": f"Payment processing error: {str(e)}"}
                
                if result.success and result.status == "pending":
                    # Payment was initiated successfully, now we need to poll for completion
                    logger.info(f"Payment initiated. Reference ID: {reference_id}. Polling for completion...")
                    
                    # Poll for payment completion
                    import time
                    max_wait_time = 60   # 1 minute for testing (should be longer in production)
                    poll_interval = 5    # 5 seconds
                    elapsed_time = 0
                    
                    while elapsed_time < max_wait_time:
                        time.sleep(poll_interval)
                        elapsed_time += poll_interval
                        
                        # Check payment status
                        status_result = mtn_payment.check_payment_status(reference_id)
                        logger.info(f"Payment status check: {status_result.status}")
                        
                        if status_result.status == "successful":
                            # Payment completed successfully - add credits
                            logger.info(f"Payment completed successfully! Adding {credits_to_add} credits to user {user_id}")
                            
                            # Add credits to user account
                            credit_success = self.credit_manager.add_credits(
                                user_id=user_id,
                                credits=credits_to_add,
                                transaction_id=result.transaction_id,
                                amount_usd=amount,
                                description=f"Credit purchase: {credits_to_add} credits for ${amount}"
                            )
                            
                            if not credit_success:
                                logger.error(f"Failed to add credits to user {user_id}")
                                return {"success": False, "error": "Failed to allocate credits"}
                            
                            # Get updated user credit balance
                            final_balance = self.credit_manager.get_user_credits(user_id)
                            
                            # Notify dashboard of successful payment
                            dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:3000")
                            webhook_data = {
                                "transaction_id": result.transaction_id,
                                "reference_id": reference_id,
                                "status": "completed",
                                "amount": amount,
                                "currency": credit_info["currency"],
                                "credits": credits_to_add,
                                "user_id": user_id
                            }
                            
                            try:
                                requests.post(f"{dashboard_url}/api/billing/credits", json=webhook_data, timeout=10)
                            except Exception as e:
                                logger.warning(f"Failed to notify dashboard: {e}")
                            
                            return {
                                "success": True,
                                "transaction_id": result.transaction_id,
                                "reference_id": reference_id,
                                "status": "completed",
                                "amount": amount,
                                "credits": credits_to_add,
                                "total_credits": final_balance,
                                "message": f"Payment completed successfully! {credits_to_add} credits added. Total balance: {final_balance} credits."
                            }
                            
                        elif status_result.status == "failed":
                            # Payment failed
                            logger.error(f"Payment failed for reference {reference_id}")
                            return {
                                "success": False,
                                "error": "Payment was declined or failed"
                            }
                        
                        # If status is still "pending", continue polling
                        logger.info(f"Payment still pending. Elapsed time: {elapsed_time}s")
                    
                    # Timeout - payment took too long
                    logger.warning(f"Payment timeout for reference {reference_id}")
                    return {
                        "success": False,
                        "error": "Payment timeout. Please check your mobile device and try again."
                    }
                    
                elif result.success:
                    # Payment completed immediately (shouldn't happen with MTN, but just in case)
                    logger.info(f"Payment completed immediately for reference {reference_id}")
                    
                    # Notify dashboard of successful payment
                    dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:3000")
                    webhook_data = {
                        "transaction_id": result.transaction_id,
                        "reference_id": reference_id,
                        "status": "completed",
                        "amount": amount,
                        "currency": credit_info["currency"],
                        "credits": credits_to_add,
                        "user_id": user_id
                    }
                    
                    try:
                        requests.post(f"{dashboard_url}/api/billing/credits", json=webhook_data, timeout=10)
                    except Exception as e:
                        logger.warning(f"Failed to notify dashboard: {e}")
                    
                    return {
                        "success": True,
                        "transaction_id": result.transaction_id,
                        "reference_id": reference_id,
                        "status": "completed",
                        "amount": amount,
                        "credits": credits_to_add,
                        "message": f"Payment completed! {credits_to_add} credits added."
                    }
                else:
                    return {
                        "success": False,
                        "error": result.message
                    }
            else:
                return {
                    "success": False,
                    "error": "MTN Mobile Money not available"
                }
                
        except Exception as e:
            logger.error(f"Credit purchase error: {e}")
            return {
                "success": False,
                "error": "Payment processing failed"
            }
    
    def verify_api_key_credits(self, api_key: str, tokens_needed: int) -> Dict:
        """Verify if API key has sufficient credits"""
        try:
            dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:3000")
            response = requests.get(f"{dashboard_url}/api/usage?api_key={api_key}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current_credits = data.get("current_credits", 0)
                credits_needed = max(1, tokens_needed // 1000)  # 1 credit per 1000 tokens
                
                return {
                    "valid": current_credits >= credits_needed,
                    "current_credits": current_credits,
                    "credits_needed": credits_needed,
                    "tokens_per_credit": 1000
                }
            else:
                return {
                    "valid": False,
                    "error": "Could not verify credits"
                }
                
        except Exception as e:
            logger.error(f"Credit verification error: {e}")
            return {
                "valid": False,
                "error": "Credit verification failed"
            }
    
    def record_api_usage(self, api_key: str, endpoint: str, tokens_used: int, model: str = None) -> Dict:
        """Record API usage and deduct credits"""
        try:
            dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:3000")
            usage_data = {
                "api_key": api_key,
                "endpoint": endpoint,
                "tokens_used": tokens_used,
                "requests_count": 1,
                "model": model or "default",
                "cost": max(0.001, tokens_used * 0.000001)  # Minimum cost
            }
            
            response = requests.post(f"{dashboard_url}/api/usage", json=usage_data, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 402:
                return {
                    "success": False,
                    "error": "insufficient_credits",
                    "message": "Insufficient credits to process request"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "invalid_api_key",
                    "message": "Invalid or inactive API key"
                }
            else:
                return {
                    "success": False,
                    "error": "usage_tracking_failed",
                    "message": "Failed to record usage"
                }
                
        except Exception as e:
            logger.error(f"Usage recording error: {e}")
            return {
                "success": False,
                "error": "usage_tracking_failed",
                "message": "Failed to record usage"
            }
