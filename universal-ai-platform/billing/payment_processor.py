"""
NexusAI Payment Integration
Handles subscription management and payment processing for African market
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from billing.usage_tracker import UsageTracker, BillingPlan

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
