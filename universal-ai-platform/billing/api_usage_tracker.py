"""
API Usage Analytics System
Tracks detailed usage per API key with cost breakdown
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
import os

logger = logging.getLogger(__name__)

# Setup DB connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nexusai")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class APIUsageRecord(Base):
    """Detailed API usage record per API key"""
    __tablename__ = 'api_usage_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key = Column(String, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    model = Column(String, nullable=True)  # gpt-4o-mini, gpt-4, claude-3, etc.
    
    # Usage metrics
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    credits_used = Column(Integer, nullable=False)
    
    # Cost breakdown
    input_cost = Column(Float, default=0.0)
    output_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Request details
    request_size_bytes = Column(Integer, default=0)
    response_size_bytes = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    
    # Status and metadata
    status_code = Column(Integer, default=200)
    error_message = Column(Text, nullable=True)
    session_id = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelPricing:
    """Model-specific pricing configuration"""
    
    PRICING = {
        "gpt-4o-mini": {
            "input_cost_per_1k": 0.00015,  # $0.15 per 1M tokens
            "output_cost_per_1k": 0.0006,  # $0.60 per 1M tokens
            "credits_per_1k": 1  # 1 credit per 1K tokens
        },
        "gpt-4o": {
            "input_cost_per_1k": 0.0025,   # $2.50 per 1M tokens
            "output_cost_per_1k": 0.01,    # $10.00 per 1M tokens  
            "credits_per_1k": 8  # 8 credits per 1K tokens (more expensive)
        },
        "gpt-4": {
            "input_cost_per_1k": 0.03,     # $30.00 per 1M tokens
            "output_cost_per_1k": 0.06,    # $60.00 per 1M tokens
            "credits_per_1k": 25  # 25 credits per 1K tokens
        },
        "claude-3-sonnet": {
            "input_cost_per_1k": 0.003,    # $3.00 per 1M tokens
            "output_cost_per_1k": 0.015,   # $15.00 per 1M tokens
            "credits_per_1k": 12  # 12 credits per 1K tokens
        },
        "claude-3-haiku": {
            "input_cost_per_1k": 0.00025,  # $0.25 per 1M tokens
            "output_cost_per_1k": 0.00125, # $1.25 per 1M tokens
            "credits_per_1k": 1  # 1 credit per 1K tokens
        },
        # Default for unknown models
        "default": {
            "input_cost_per_1k": 0.001,
            "output_cost_per_1k": 0.002,
            "credits_per_1k": 2
        }
    }
    
    @classmethod
    def get_pricing(cls, model: str) -> Dict:
        """Get pricing for a specific model"""
        return cls.PRICING.get(model, cls.PRICING["default"])
    
    @classmethod
    def calculate_cost_and_credits(cls, model: str, input_tokens: int, output_tokens: int) -> Dict:
        """Calculate cost and credits for token usage"""
        pricing = cls.get_pricing(model)
        
        input_cost = (input_tokens / 1000) * pricing["input_cost_per_1k"]
        output_cost = (output_tokens / 1000) * pricing["output_cost_per_1k"]
        total_cost = input_cost + output_cost
        
        total_tokens = input_tokens + output_tokens
        credits_used = max(1, int((total_tokens / 1000) * pricing["credits_per_1k"]))
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "credits_used": credits_used,
            "total_tokens": total_tokens
        }

class APIUsageTracker:
    """Advanced API usage tracking with per-key analytics"""
    
    def __init__(self):
        self.session = Session()
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create tables if they don't exist"""
        try:
            Base.metadata.create_all(engine)
        except Exception as e:
            logger.error(f"Failed to create usage tracking tables: {e}")
    
    def record_api_usage(self, api_key: str, user_id: str, endpoint: str, 
                        model: str = "gpt-4o-mini", input_tokens: int = 0, 
                        output_tokens: int = 0, session_id: str = None,
                        request_size: int = 0, response_size: int = 0,
                        processing_time_ms: int = 0, status_code: int = 200,
                        error_message: str = None) -> Dict:
        """Record detailed API usage"""
        
        try:
            # Calculate costs and credits
            cost_breakdown = ModelPricing.calculate_cost_and_credits(
                model, input_tokens, output_tokens
            )
            
            # Create usage record
            usage_record = APIUsageRecord(
                api_key=api_key,
                user_id=user_id,
                endpoint=endpoint,
                method="POST",  # Most AI endpoints are POST
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=cost_breakdown["total_tokens"],
                credits_used=cost_breakdown["credits_used"],
                input_cost=cost_breakdown["input_cost"],
                output_cost=cost_breakdown["output_cost"],
                total_cost=cost_breakdown["total_cost"],
                request_size_bytes=request_size,
                response_size_bytes=response_size,
                processing_time_ms=processing_time_ms,
                status_code=status_code,
                error_message=error_message,
                session_id=session_id
            )
            
            self.session.add(usage_record)
            self.session.commit()
            
            logger.info(f"Recorded usage: {api_key[-8:]}... used {cost_breakdown['credits_used']} credits for {model}")
            
            return {
                "success": True,
                "usage_id": str(usage_record.id),
                "credits_used": cost_breakdown["credits_used"],
                "total_cost": cost_breakdown["total_cost"],
                "model": model
            }
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to record API usage: {e}")
            return {"success": False, "error": str(e)}
    
    def get_usage_by_api_key(self, api_key: str, start_date: datetime = None, 
                           end_date: datetime = None, limit: int = 100) -> List[Dict]:
        """Get usage records for specific API key"""
        try:
            query = self.session.query(APIUsageRecord).filter_by(api_key=api_key)
            
            if start_date:
                query = query.filter(APIUsageRecord.created_at >= start_date)
            if end_date:
                query = query.filter(APIUsageRecord.created_at <= end_date)
                
            records = query.order_by(APIUsageRecord.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": str(record.id),
                    "endpoint": record.endpoint,
                    "model": record.model,
                    "input_tokens": record.input_tokens,
                    "output_tokens": record.output_tokens,
                    "total_tokens": record.total_tokens,
                    "credits_used": record.credits_used,
                    "total_cost": record.total_cost,
                    "processing_time_ms": record.processing_time_ms,
                    "status_code": record.status_code,
                    "created_at": record.created_at.isoformat()
                }
                for record in records
            ]
            
        except Exception as e:
            logger.error(f"Failed to get usage by API key: {e}")
            return []
    
    def get_usage_analytics_by_user(self, user_id: str, days: int = 30) -> Dict:
        """Get comprehensive usage analytics for user across all their API keys"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all usage records for user
            records = self.session.query(APIUsageRecord).filter(
                APIUsageRecord.user_id == user_id,
                APIUsageRecord.created_at >= start_date
            ).all()
            
            # Aggregate by API key
            api_key_stats = {}
            total_stats = {
                "total_requests": 0,
                "total_credits": 0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "models_used": set(),
                "endpoints_used": set()
            }
            
            for record in records:
                # Per API key stats
                key_short = record.api_key[-8:]  # Last 8 chars for privacy
                if key_short not in api_key_stats:
                    api_key_stats[key_short] = {
                        "api_key": key_short,
                        "requests": 0,
                        "credits_used": 0,
                        "total_cost": 0.0,
                        "tokens_used": 0,
                        "models": {},
                        "endpoints": {},
                        "avg_processing_time": 0,
                        "error_rate": 0,
                        "errors": 0
                    }
                
                stats = api_key_stats[key_short]
                stats["requests"] += 1
                stats["credits_used"] += record.credits_used
                stats["total_cost"] += record.total_cost
                stats["tokens_used"] += record.total_tokens
                
                # Model usage
                if record.model:
                    stats["models"][record.model] = stats["models"].get(record.model, 0) + 1
                    total_stats["models_used"].add(record.model)
                
                # Endpoint usage
                stats["endpoints"][record.endpoint] = stats["endpoints"].get(record.endpoint, 0) + 1
                total_stats["endpoints_used"].add(record.endpoint)
                
                # Error tracking
                if record.status_code >= 400:
                    stats["errors"] += 1
                
                # Processing time (for average calculation)
                if record.processing_time_ms:
                    current_avg = stats["avg_processing_time"]
                    stats["avg_processing_time"] = ((current_avg * (stats["requests"] - 1)) + record.processing_time_ms) / stats["requests"]
                
                # Total stats
                total_stats["total_requests"] += 1
                total_stats["total_credits"] += record.credits_used
                total_stats["total_cost"] += record.total_cost
                total_stats["total_tokens"] += record.total_tokens
            
            # Calculate error rates
            for stats in api_key_stats.values():
                if stats["requests"] > 0:
                    stats["error_rate"] = (stats["errors"] / stats["requests"]) * 100
            
            # Convert sets to lists for JSON serialization
            total_stats["models_used"] = list(total_stats["models_used"])
            total_stats["endpoints_used"] = list(total_stats["endpoints_used"])
            
            return {
                "period_days": days,
                "total_statistics": total_stats,
                "api_key_breakdown": list(api_key_stats.values()),
                "top_consuming_keys": sorted(
                    api_key_stats.values(), 
                    key=lambda x: x["credits_used"], 
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage analytics: {e}")
            return {"error": str(e)}
    
    def get_model_cost_breakdown(self, user_id: str, days: int = 30) -> Dict:
        """Get cost breakdown by model for user"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Query usage by model
            from sqlalchemy import func
            results = self.session.query(
                APIUsageRecord.model,
                func.count(APIUsageRecord.id).label('requests'),
                func.sum(APIUsageRecord.credits_used).label('total_credits'),
                func.sum(APIUsageRecord.total_cost).label('total_cost'),
                func.sum(APIUsageRecord.total_tokens).label('total_tokens')
            ).filter(
                APIUsageRecord.user_id == user_id,
                APIUsageRecord.created_at >= start_date
            ).group_by(APIUsageRecord.model).all()
            
            model_breakdown = []
            for model, requests, credits, cost, tokens in results:
                model_breakdown.append({
                    "model": model or "unknown",
                    "requests": requests,
                    "credits_used": credits or 0,
                    "total_cost": float(cost or 0),
                    "tokens_used": tokens or 0,
                    "avg_credits_per_request": (credits or 0) / requests if requests > 0 else 0,
                    "avg_tokens_per_request": (tokens or 0) / requests if requests > 0 else 0
                })
            
            # Sort by credits used (descending)
            model_breakdown.sort(key=lambda x: x["credits_used"], reverse=True)
            
            return {
                "period_days": days,
                "model_breakdown": model_breakdown,
                "total_models": len(model_breakdown)
            }
            
        except Exception as e:
            logger.error(f"Failed to get model cost breakdown: {e}")
            return {"error": str(e)}
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close()