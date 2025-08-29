"""
MTN Mobile Money Payment Integration for NexusAI
Handles credit purchases via MTN Mobile Money API
"""

import requests
import json
import os
import logging
import base64
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)
# Set to DEBUG level to see detailed logs
logger.setLevel(logging.DEBUG)

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
    amount: float = 0.0
    phone_number: str = ""

class MTNMobileMoneyPayment:
    """MTN Mobile Money payment processor for NexusAI credits"""
    
    def __init__(self, 
                 subscription_key: str = None,
                 api_user: str = None,
                 api_key: str = None,
                 environment: str = "production",
                 target_environment: str = "mtnliberia"):
        """
        Initialize MTN Mobile Money payment processor
        
        Args:
            subscription_key: MTN subscription key (Ocp-Apim-Subscription-Key)
            api_user: MTN API User ID
            api_key: MTN API Key (for the API User)
            environment: "sandbox" or "production"
            target_environment: MTN target environment (e.g., "mtnliberia")
        """
        self.subscription_key = subscription_key or os.getenv('MTN_SUBSCRIPTION_KEY')
        self.api_user = api_user or os.getenv('MTN_API_USER')
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
            "Ocp-Apim-Subscription-Key": self.subscription_key
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
            
            # Create Basic Auth header using API User ID and API Key
            auth_string = base64.b64encode(f"{self.api_user}:{self.api_key}".encode()).decode()
            
            headers = {
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": self.subscription_key,
                "Authorization": f"Basic {auth_string}"
            }
            
            logger.debug(f"Token request URL: {url}")
            logger.debug(f"Token request headers: {headers}")
            
            response = requests.post(url, headers=headers)
            
            logger.debug(f"Token response status: {response.status_code}")
            logger.debug(f"Token response: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                logger.info(f"Access token created successfully: {access_token[:20]}...")
                return access_token
            else:
                logger.error(f"Failed to create access token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            return None
    
    def request_payment(self, 
                       phone_number: str, 
                       package_type: str,
                       user_id: str,
                       test_amount: float = None) -> PaymentResponse:
        """
        Request payment for credit package
        
        Args:
            phone_number: Customer phone number (format: +231XXXXXXXX)
            package_type: "starter", "standard", or "premium"
            user_id: NexusAI user ID
            test_amount: Optional test amount to override package price
            
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
            
            # Use test amount if provided, otherwise use package price
            amount = test_amount if test_amount is not None else package["price"]
            
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
            # Create payment data - simplified to match Node.js exactly
            payment_data = {
                "amount": str(amount),
                "currency": "USD",
                "externalId": reference_id,
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyId": phone_number.replace("+", "")
                },
                "payerMessage": "Payment for NexusAI credits",
                "payeeNote": "NexusAI credit purchase"
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
                    reference_id=reference_id,
                    amount=amount,
                    phone_number=phone_number
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
    
    def request_payment_custom(self, 
                              phone_number: str, 
                              amount: float,
                              user_id: str,
                              reference_id: str,
                              description: str) -> PaymentResponse:
        """
        Request payment with custom amount (for flexible credit purchases)
        
        Args:
            phone_number: Customer phone number (format: +231XXXXXXXX)
            amount: Custom amount in USD
            user_id: NexusAI user ID
            reference_id: Unique reference ID
            description: Payment description
            
        Returns:
            PaymentResponse object
        """
        try:
            # Convert amount to float if it's a string
            amount = float(amount)
            
            # Validate minimum amount
            if amount < 5.00:
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    status="failed",
                    message="Minimum amount is $5.00"
                )
            
            # Get access token
            access_token = self.create_access_token()
            if not access_token:
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    status="failed",
                    message="Failed to authenticate with MTN API"
                )
            
            # Prepare payment request - matching Node.js format exactly
            external_id = str(uuid.uuid4())  # Separate UUID for externalId like Node.js
            payment_data = {
                "amount": amount,  # Keep as number, not string
                "currency": "USD",
                "externalId": external_id,  # Use separate UUID like Node.js
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyId": phone_number.replace("+", "")  # Remove + like Node.js
                },
                "payerMessage": "Payment for NexusAI credits",  # Exact match
                "payeeNote": "NexusAI credit purchase"  # Exact match
            }
            
            # Headers matching Node.js version exactly
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Reference-Id": reference_id,
                "X-Target-Environment": "mtnliberia",  # Exact match with Node.js
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": self.subscription_key
            }
            
            logger.info(f"Requesting custom payment: ${amount} from {phone_number}")
            logger.debug(f"Payment data: {payment_data}")
            logger.debug(f"Headers: {headers}")
            logger.debug(f"URL: {self.base_url}/collection/v1_0/requesttopay")
            
            response = requests.post(
                f"{self.base_url}/collection/v1_0/requesttopay",
                json=payment_data,
                headers=headers
            )
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Response content: {response.text}")
            
            if response.status_code == 202:
                transaction_id = response.headers.get('X-Reference-Id', reference_id)
                logger.info(f"Custom payment initiated successfully. Transaction ID: {transaction_id}")
                
                return PaymentResponse(
                    success=True,
                    transaction_id=transaction_id,
                    status="pending",
                    message="Payment request sent. Please complete on your mobile device.",
                    reference_id=reference_id,
                    amount=amount,
                    phone_number=phone_number
                )
            else:
                logger.error(f"Custom payment request failed: {response.status_code} - {response.text}")
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    status="failed",
                    message=f"Payment request failed: {response.text}"
                )
                
        except Exception as e:
            logger.error(f"Error requesting custom payment: {e}")
            return PaymentResponse(
                success=False,
                transaction_id="",
                status="failed",
                message=f"Payment request failed: {str(e)}"
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
                
                # Extract additional info from response
                amount = float(payment_data.get("amount", 0))
                phone = payment_data.get("payer", {}).get("partyId", "")
                
                return PaymentResponse(
                    success=status == "successful",
                    transaction_id=reference_id,
                    status=status,
                    message=f"Payment status: {status}",
                    reference_id=reference_id,
                    amount=amount,
                    phone_number=phone
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
    """Manage user credits and transactions with database persistence and idempotency"""
    
    def __init__(self, db_path: str = "credits.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for credits and transactions"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Users table with credit balance
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    credits INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Credit transactions table with idempotency
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'completed',
                    payment_reference TEXT,
                    amount_usd REAL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(transaction_id)
                )
            """)
            
            # Index for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_transactions ON credit_transactions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transaction_id ON credit_transactions(transaction_id)")
            
            conn.commit()
            logger.info("Credit database initialized successfully")
        
    def add_credits(self, user_id: str, credits: int, transaction_id: str, amount_usd: float = None, description: str = None) -> bool:
        """
        Add credits to user account with idempotency protection
        
        Args:
            user_id: User identifier
            credits: Number of credits to add
            transaction_id: Unique payment transaction ID (ensures idempotency)
            amount_usd: USD amount paid (optional)
            description: Transaction description (optional)
            
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("BEGIN TRANSACTION")
                
                # Check if transaction already exists (idempotency)
                existing = conn.execute(
                    "SELECT id, status FROM credit_transactions WHERE transaction_id = ?",
                    (transaction_id,)
                ).fetchone()
                
                if existing:
                    logger.info(f"Transaction {transaction_id} already processed (idempotent)")
                    return True
                
                # Get or create user
                current_time = datetime.now().isoformat()
                user = conn.execute(
                    "SELECT user_id, credits FROM users WHERE user_id = ?",
                    (user_id,)
                ).fetchone()
                
                if user:
                    # Update existing user
                    new_balance = user[1] + credits
                    conn.execute(
                        "UPDATE users SET credits = ?, updated_at = ? WHERE user_id = ?",
                        (new_balance, current_time, user_id)
                    )
                else:
                    # Create new user
                    new_balance = credits
                    conn.execute(
                        "INSERT INTO users (user_id, credits, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (user_id, credits, current_time, current_time)
                    )
                
                # Record transaction
                conn.execute("""
                    INSERT INTO credit_transactions 
                    (transaction_id, user_id, credits, transaction_type, payment_reference, amount_usd, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction_id, user_id, credits, "credit_purchase", 
                    transaction_id, amount_usd, description or f"Credit purchase: {credits} credits", current_time
                ))
                
                conn.commit()
                logger.info(f"✅ Successfully added {credits} credits to user {user_id}. New balance: {new_balance} (Transaction: {transaction_id})")
                return True
                
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                logger.info(f"Transaction {transaction_id} already processed (idempotent - integrity error)")
                return True
            else:
                logger.error(f"Database integrity error: {e}")
                return False
        except Exception as e:
            logger.error(f"Error adding credits: {e}")
            return False
    
    def get_user_credits(self, user_id: str) -> int:
        """Get user's current credit balance from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute(
                    "SELECT credits FROM users WHERE user_id = ?",
                    (user_id,)
                ).fetchone()
                
                credits = result[0] if result else 0
                logger.debug(f"User {user_id} has {credits} credits")
                return credits
                
        except Exception as e:
            logger.error(f"Error getting user credits: {e}")
            return 0
    
    def deduct_credits(self, user_id: str, credits: int, description: str = None) -> bool:
        """Deduct credits from user account with transaction logging"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("BEGIN TRANSACTION")
                
                # Get current balance
                current_credits = self.get_user_credits(user_id)
                
                if current_credits >= credits:
                    # Update user balance
                    new_balance = current_credits - credits
                    current_time = datetime.now().isoformat()
                    
                    conn.execute(
                        "UPDATE users SET credits = ?, updated_at = ? WHERE user_id = ?",
                        (new_balance, current_time, user_id)
                    )
                    
                    # Record transaction
                    transaction_id = f"deduct_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
                    conn.execute("""
                        INSERT INTO credit_transactions 
                        (transaction_id, user_id, credits, transaction_type, description, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        transaction_id, user_id, -credits, "credit_usage", 
                        description or f"Credit usage: {credits} credits", current_time
                    ))
                    
                    conn.commit()
                    logger.info(f"✅ Deducted {credits} credits from user {user_id}. New balance: {new_balance}")
                    return True
                else:
                    logger.warning(f"Insufficient credits for user {user_id}: {current_credits} < {credits}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deducting credits: {e}")
            return False
    
    def get_user_transactions(self, user_id: str, limit: int = 50) -> list:
        """Get user's transaction history from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                
                results = conn.execute("""
                    SELECT transaction_id, credits, transaction_type, amount_usd, description, created_at, status
                    FROM credit_transactions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit)).fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Error getting user transactions: {e}")
            return []
    
    def get_all_users_credits(self) -> dict:
        """Get all user credits (for admin/testing purposes)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                results = conn.execute(
                    "SELECT user_id, credits FROM users ORDER BY credits DESC"
                ).fetchall()
                
                return {user_id: credits for user_id, credits in results}
                
        except Exception as e:
            logger.error(f"Error getting all user credits: {e}")
            return {}
    
    def get_transaction_by_id(self, transaction_id: str) -> dict:
        """Get specific transaction details (for idempotency checks)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                result = conn.execute("""
                    SELECT * FROM credit_transactions WHERE transaction_id = ?
                """, (transaction_id,)).fetchone()
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"Error getting transaction: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Initialize payment processor
    mtn_payment = MTNMobileMoneyPayment(
        subscription_key="your_subscription_key",
        api_user="your_api_user_id",
        api_key="your_api_key",
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
    