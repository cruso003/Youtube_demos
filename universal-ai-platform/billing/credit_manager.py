"""
Credit Management System
Handles credit balance operations and verification
"""

import logging
from typing import Dict, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from billing.models import User, CreditTransaction
import os

logger = logging.getLogger(__name__)

# Setup DB connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nexusai")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class LocalCreditManager:
    """Local credit management with database operations"""
    
    def __init__(self):
        self.minimum_credits_for_api_key = int(os.getenv("MIN_CREDITS_API_KEY", "5000"))  # 5000 credits = $5
    
    def get_user_credits(self, user_id: str) -> int:
        """Get user's current credit balance from local database"""
        session = Session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user.credit_balance or 0
            return 0
        except Exception as e:
            logger.error(f"Error getting credits for user {user_id}: {e}")
            return 0
        finally:
            session.close()
    
    def add_credits(self, user_id: str, credits: int, transaction_id: str, amount_usd: float, description: str) -> bool:
        """Add credits to user account and record transaction"""
        session = Session()
        try:
            # Get user
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return False
            
            # Update user credit balance
            user.credit_balance = (user.credit_balance or 0) + credits
            
            # Record transaction
            transaction = CreditTransaction(
                user_id=user_id,
                credits=credits,
                amount_usd=amount_usd,
                transaction_id=transaction_id,
                description=description
            )
            session.add(transaction)
            session.commit()
            
            logger.info(f"Added {credits} credits to user {user_id}. New balance: {user.credit_balance}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding credits to user {user_id}: {e}")
            return False
        finally:
            session.close()
    
    def deduct_credits(self, user_id: str, credits: int, description: str) -> Dict:
        """Deduct credits from user account"""
        session = Session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            current_balance = user.credit_balance or 0
            if current_balance < credits:
                return {
                    "success": False, 
                    "error": "insufficient_credits",
                    "current_credits": current_balance,
                    "required_credits": credits
                }
            
            # Deduct credits
            user.credit_balance = current_balance - credits
            
            # Record negative transaction
            transaction = CreditTransaction(
                user_id=user_id,
                credits=-credits,
                transaction_id=f"usage_{int(time.time())}",
                description=description
            )
            session.add(transaction)
            session.commit()
            
            return {
                "success": True,
                "new_balance": user.credit_balance,
                "deducted": credits
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error deducting credits from user {user_id}: {e}")
            return {"success": False, "error": "Database error"}
        finally:
            session.close()
    
    def can_generate_api_key(self, user_id: str) -> Dict:
        """Check if user can generate API key - first key requires 5000 credits, additional keys need positive balance"""
        from billing.models import APIKey
        
        session = Session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return {"can_generate": False, "error": "User not found"}
            
            current_credits = user.credit_balance or 0
            existing_keys_count = session.query(APIKey).filter_by(user_id=user_id, revoked=False).count()
            
            # First API key requires full 5000 credits (payment verification)
            if existing_keys_count == 0:
                return {
                    "can_generate": current_credits >= self.minimum_credits_for_api_key,
                    "current_credits": current_credits,
                    "required_credits": self.minimum_credits_for_api_key,
                    "deficit": max(0, self.minimum_credits_for_api_key - current_credits),
                    "is_first_key": True,
                    "reason": "first_key_requires_payment_verification"
                }
            
            # Additional keys only need positive balance (user already proved they can pay)
            return {
                "can_generate": current_credits > 0,
                "current_credits": current_credits,
                "required_credits": 1,
                "deficit": max(0, 1 - current_credits),
                "is_first_key": False,
                "reason": "additional_key_requires_positive_balance"
            }
            
        except Exception as e:
            logger.error(f"Error checking API key generation eligibility: {e}")
            return {"can_generate": False, "error": "Database error"}
        finally:
            session.close()
    
    def verify_api_key_credits(self, api_key: str, estimated_credits: int = None, 
                              service_type: str = "gpt", model: str = "gpt-4o-mini") -> Dict:
        """Verify if API key user has sufficient credits for multi-service operation"""
        from billing.models import APIKey
        
        session = Session()
        try:
            # Get API key and user
            key_obj = session.query(APIKey).filter_by(api_key=api_key, revoked=False).first()
            if not key_obj:
                return {"valid": False, "error": "Invalid API key"}
            
            user = session.query(User).filter_by(id=key_obj.user_id).first()
            if not user or not user.is_active:
                return {"valid": False, "error": "User inactive"}
            
            current_credits = user.credit_balance or 0
            
            # If credits not provided, estimate based on service type and model
            if estimated_credits is None:
                estimated_credits = self._estimate_credits_needed(service_type, model)
            
            return {
                "valid": current_credits >= estimated_credits,
                "user_id": str(user.id),
                "current_credits": current_credits,
                "credits_needed": estimated_credits,
                "service_type": service_type,
                "model": model
            }
            
        except Exception as e:
            logger.error(f"Error verifying API key credits: {e}")
            return {"valid": False, "error": "Verification failed"}
        finally:
            session.close()
    
    def _estimate_credits_needed(self, service_type: str, model: str, units: int = 1000) -> int:
        """Estimate credits needed based on service type and model"""
        # Import pricing from multi-service tracker
        from billing.multi_service_tracker import ServicePricing, ServiceType
        
        try:
            service_enum = ServiceType(service_type)
            cost_info = ServicePricing.calculate_service_cost(
                service_enum, model, units, "tokens" if service_type == "gpt" else "units"
            )
            return cost_info.get("credits_used", 1)
        except (ValueError, KeyError):
            # Fallback for unknown services/models
            return max(1, units // 1000) if service_type == "gpt" else 10

import time