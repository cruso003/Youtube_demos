"""
MTN Mobile Money Payment Integration for NexusAI
Handles credit purchases via MTN Mobile Money API
"""

import requests
import json
import os
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

@dataclass
class PaymentRequest:
    """Payment request data structure"""
    amount: float
    currency: str = "USD"
    phone_number: str = ""
    reference_id: str = ""
    description: str = ""

@dataclass
class PaymentResponse:
    """Payment response data structure"""
    success: bool
    transaction_id: str
    status: str
    message: str
    reference_id: str = ""

class MTNMobileMoneyPayment:
    """MTN Mobile Money payment processor for NexusAI credits"""
    
    def __init__(self, 
                 api_key: str = None,
                 environment: str = "sandbox",
                 target_environment: str = "mtnliberia"):
        """
        Initialize MTN Mobile Money payment processor
        
        Args:
            api_key: MTN API key
            environment: "sandbox" or "production"
            target_environment: MTN target environment (e.g., "mtnliberia")
        """
        self.api_key = api_key or os.getenv('MTN_API_KEY')
        self.environment = environment
        self.target_environment = target_environment
        
        # MTN API endpoints
        if environment == "production":
            self.base_url = "https://proxy.momoapi.mtn.com"
        else:
            self.base_url = "https://sandbox.momodeveloper.mtn.com"
            
        self.headers = {
            "Content-Type": "application/json",
            "X-Target-Environment": target_environment,
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        # Credit packages
        self.credit_packages = {
            "starter": {
                "credits": 1000,
                "price": 1.00,
                "currency": "USD",
                "description": "1,000 NexusAI Credits"
            },
            "standard": {
                "credits": 10000,
                "price": 9.00,
                "currency": "USD", 
                "description": "10,000 NexusAI Credits (10% Bonus)"
            },
            "premium": {
                "credits": 100000,
                "price": 80.00,
                "currency": "USD",
                "description": "100,000 NexusAI Credits (20% Bonus)"
            }
        }
    
    def create_access_token(self) -> Optional[str]:
        """Create access token for MTN API"""
        try:
            url = f"{self.base_url}/collection/token/"
            response = requests.post(url, headers=self.headers)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            else:
                logger.error(f"Failed to create access token: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            return None
    
    def request_payment(self, 
                       phone_number: str, 
                       package_type: str,
                       user_id: str) -> PaymentResponse:
        """
        Request payment for credit package
        
        Args:
            phone_number: Customer phone number (format: +231XXXXXXXX)
            package_type: "starter", "standard", or "premium"
            user_id: NexusAI user ID
            
        Returns:
            PaymentResponse object
        """
        try:
            # Validate package type
            if package_type not in self.credit_packages:
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    status="failed",
                    message=f"Invalid package type: {package_type}"
                )
            
            package = self.credit_packages[package_type]
            reference_id = f"nexusai_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Get access token
            access_token = self.create_access_token()
            if not access_token:
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    status="failed",
                    message="Failed to authenticate with MTN API"
                )
            
            # Prepare payment request
            payment_data = {
                "amount": str(package["price"]),
                "currency": package["currency"],
                "externalId": reference_id,
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyId": phone_number.replace("+", "")
                },
                "payerMessage": f"NexusAI Credits Purchase - {package['description']}",
                "payeeNote": f"Payment for {package['credits']} NexusAI credits"
            }
            
            # Make payment request
            headers = self.headers.copy()
            headers["Authorization"] = f"Bearer {access_token}"
            headers["X-Reference-Id"] = reference_id
            
            url = f"{self.base_url}/collection/v1_0/requesttopay"
            response = requests.post(url, json=payment_data, headers=headers)
            
            if response.status_code == 202:
                # Payment request accepted
                return PaymentResponse(
                    success=True,
                    transaction_id=reference_id,
                    status="pending",
                    message="Payment request sent successfully",
                    reference_id=reference_id
                )
            else:
                logger.error(f"Payment request failed: {response.text}")
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    status="failed",
                    message=f"Payment request failed: {response.text}",
                    reference_id=reference_id
                )
                
        except Exception as e:
            logger.error(f"Error requesting payment: {e}")
            return PaymentResponse(
                success=False,
                transaction_id="",
                status="error",
                message=f"Payment error: {str(e)}"
            )
    
    def check_payment_status(self, reference_id: str) -> PaymentResponse:
        """
        Check the status of a payment transaction
        
        Args:
            reference_id: Transaction reference ID
            
        Returns:
            PaymentResponse object with current status
        """
        try:
            # Get access token
            access_token = self.create_access_token()
            if not access_token:
                return PaymentResponse(
                    success=False,
                    transaction_id=reference_id,
                    status="failed",
                    message="Failed to authenticate with MTN API"
                )
            
            # Check payment status
            headers = self.headers.copy()
            headers["Authorization"] = f"Bearer {access_token}"
            
            url = f"{self.base_url}/collection/v1_0/requesttopay/{reference_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                payment_data = response.json()
                status = payment_data.get("status", "UNKNOWN").lower()
                
                return PaymentResponse(
                    success=status == "successful",
                    transaction_id=reference_id,
                    status=status,
                    message=f"Payment status: {status}",
                    reference_id=reference_id
                )
            else:
                logger.error(f"Failed to check payment status: {response.text}")
                return PaymentResponse(
                    success=False,
                    transaction_id=reference_id,
                    status="unknown",
                    message="Failed to check payment status"
                )
                
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return PaymentResponse(
                success=False,
                transaction_id=reference_id,
                status="error",
                message=f"Status check error: {str(e)}"
            )
    
    def get_credit_packages(self) -> Dict:
        """Get available credit packages"""
        return self.credit_packages

# Credit management
class CreditManager:
    """Manage user credits and transactions"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        
    def add_credits(self, user_id: str, credits: int, transaction_id: str) -> bool:
        """
        Add credits to user account
        
        Args:
            user_id: User identifier
            credits: Number of credits to add
            transaction_id: Payment transaction ID
            
        Returns:
            Success status
        """
        try:
            # In a real implementation, this would update the database
            # For now, we'll just log the transaction
            logger.info(f"Adding {credits} credits to user {user_id} (transaction: {transaction_id})")
            
            # TODO: Implement database update
            # UPDATE users SET credits = credits + ? WHERE user_id = ?
            # INSERT INTO transactions (user_id, credits, transaction_id, timestamp) VALUES (?, ?, ?, ?)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding credits: {e}")
            return False
    
    def get_user_credits(self, user_id: str) -> int:
        """Get user's current credit balance"""
        try:
            # TODO: Implement database query
            # SELECT credits FROM users WHERE user_id = ?
            
            # For now, return a default value
            return 0
            
        except Exception as e:
            logger.error(f"Error getting user credits: {e}")
            return 0
    
    def deduct_credits(self, user_id: str, credits: int) -> bool:
        """Deduct credits from user account"""
        try:
            current_credits = self.get_user_credits(user_id)
            
            if current_credits >= credits:
                # TODO: Implement database update
                # UPDATE users SET credits = credits - ? WHERE user_id = ?
                logger.info(f"Deducted {credits} credits from user {user_id}")
                return True
            else:
                logger.warning(f"Insufficient credits for user {user_id}: {current_credits} < {credits}")
                return False
                
        except Exception as e:
            logger.error(f"Error deducting credits: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize payment processor
    mtn_payment = MTNMobileMoneyPayment(
        api_key="your_mtn_api_key",
        environment="sandbox",
        target_environment="mtnliberia"
    )
    
    # Request payment for starter package
    payment_result = mtn_payment.request_payment(
        phone_number="+231123456789",
        package_type="starter",
        user_id="user123"
    )
    
    print(f"Payment request: {payment_result}")
    
    # Check payment status
    if payment_result.success:
        status_result = mtn_payment.check_payment_status(payment_result.transaction_id)
        print(f"Payment status: {status_result}")
