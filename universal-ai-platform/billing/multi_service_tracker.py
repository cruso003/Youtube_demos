"""
Multi-Service Credit Allocation System
Handles credit usage across multiple AI services (Phone + GPT, Voice + Vision, etc.)
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, JSON
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

class ServiceType(Enum):
    """Available AI services"""
    GPT = "gpt"
    VOICE_TTS = "voice_tts"  # Text-to-Speech
    VOICE_STT = "voice_stt"  # Speech-to-Text
    VISION = "vision"        # Image analysis
    PHONE = "phone"          # Twilio calling
    REALTIME = "realtime"    # LiveKit real-time
    OCR = "ocr"             # Document processing
    EMBEDDING = "embedding"  # Vector embeddings

@dataclass
class ServiceUsage:
    """Individual service usage within a multi-service request"""
    service_type: ServiceType
    units_consumed: int        # tokens, seconds, images, etc.
    unit_type: str            # "tokens", "seconds", "images", "minutes"
    credits_used: int
    cost_usd: float
    model_or_provider: str    # "gpt-4o-mini", "twilio", "openai-tts", etc.
    metadata: Dict[str, Any] = None

class MultiServiceUsageRecord(Base):
    """Multi-service usage record for complex workflows"""
    __tablename__ = 'multi_service_usage_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key = Column(String, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(String, nullable=True, index=True)
    
    # Workflow information
    workflow_name = Column(String, nullable=False)  # "phone_ai_call", "voice_chat", "image_analysis"
    business_adapter = Column(String, nullable=True)  # "emergencyservices", "languagelearning"
    
    # Service breakdown (JSON field)
    services_used = Column(JSON, nullable=False)  # List of ServiceUsage objects
    
    # Totals
    total_credits_used = Column(Integer, nullable=False)
    total_cost_usd = Column(Float, default=0.0)
    total_duration_seconds = Column(Integer, default=0)
    
    # Request metadata
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, default=200)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ServicePricing:
    """Multi-service pricing configuration"""
    
    PRICING = {
        ServiceType.GPT: {
            "gpt-4o-mini": {"credits_per_1k_tokens": 1, "cost_per_1k_tokens": 0.00015},
            "gpt-4o": {"credits_per_1k_tokens": 8, "cost_per_1k_tokens": 0.0025},
            "gpt-4": {"credits_per_1k_tokens": 25, "cost_per_1k_tokens": 0.03}
        },
        ServiceType.VOICE_TTS: {
            "cartesia": {"credits_per_char": 0.0008, "cost_per_char": 0.000011},  # Cartesia Sonic
            "openai-tts": {"credits_per_char": 0.001, "cost_per_char": 0.000015}   # Fallback option
        },
        ServiceType.VOICE_STT: {
            "deepgram": {"credits_per_minute": 8, "cost_per_minute": 0.0043},      # Primary STT
            "openai-whisper": {"credits_per_minute": 10, "cost_per_minute": 0.006}  # Backup option
        },
        ServiceType.VISION: {
            "gpt-4o-vision": {"credits_per_image": 40, "cost_per_image": 0.008},   # GPT-4o with vision
            "gpt-4-vision": {"credits_per_image": 50, "cost_per_image": 0.01}      # GPT-4 with vision
        },
        ServiceType.PHONE: {
            "twilio": {"credits_per_minute": 20, "cost_per_minute": 0.0085},       # US rates
            "twilio-intl": {"credits_per_minute": 35, "cost_per_minute": 0.015}    # International
        },
        ServiceType.REALTIME: {
            "livekit": {"credits_per_minute": 12, "cost_per_minute": 0.004},       # LiveKit real-time
            "livekit-egress": {"credits_per_minute": 15, "cost_per_minute": 0.005} # Recording/streaming
        }
    }
    
    @classmethod
    def calculate_service_cost(cls, service_type: ServiceType, provider: str, 
                             units: int, unit_type: str) -> Dict:
        """Calculate cost and credits for a specific service"""
        pricing = cls.PRICING.get(service_type, {}).get(provider)
        
        if not pricing:
            # Default fallback pricing
            return {
                "credits_used": max(1, units // 100),  # 1 credit per 100 units
                "cost_usd": units * 0.0001,  # $0.0001 per unit
                "unit_rate": f"1 credit per 100 {unit_type}"
            }
        
        # Calculate based on unit type
        if unit_type == "tokens" and "credits_per_1k_tokens" in pricing:
            credits_used = max(1, int((units / 1000) * pricing["credits_per_1k_tokens"]))
            cost_usd = (units / 1000) * pricing["cost_per_1k_tokens"]
        elif unit_type == "characters" and "credits_per_char" in pricing:
            credits_used = max(1, int(units * pricing["credits_per_char"]))
            cost_usd = units * pricing["cost_per_char"]
        elif unit_type == "minutes" and "credits_per_minute" in pricing:
            credits_used = max(1, int(units * pricing["credits_per_minute"]))
            cost_usd = units * pricing["cost_per_minute"]
        elif unit_type == "images" and "credits_per_image" in pricing:
            credits_used = max(1, units * pricing["credits_per_image"])
            cost_usd = units * pricing["cost_per_image"]
        else:
            # Fallback calculation
            credits_used = max(1, units)
            cost_usd = units * 0.001
        
        return {
            "credits_used": credits_used,
            "cost_usd": cost_usd,
            "unit_rate": f"{credits_used} credits for {units} {unit_type}"
        }

class MultiServiceTracker:
    """Track usage across multiple AI services in a single workflow"""
    
    def __init__(self):
        self.session = Session()
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create tables if they don't exist"""
        try:
            Base.metadata.create_all(engine)
        except Exception as e:
            logger.error(f"Failed to create multi-service tables: {e}")
    
    def start_workflow_tracking(self, api_key: str, user_id: str, workflow_name: str,
                              endpoint: str, session_id: str = None, 
                              business_adapter: str = None) -> str:
        """Start tracking a multi-service workflow"""
        workflow_id = str(uuid.uuid4())
        
        # Store workflow start in memory/cache for active tracking
        workflow_context = {
            "workflow_id": workflow_id,
            "api_key": api_key,
            "user_id": user_id,
            "workflow_name": workflow_name,
            "endpoint": endpoint,
            "session_id": session_id,
            "business_adapter": business_adapter,
            "services_used": [],
            "start_time": datetime.utcnow()
        }
        
        # Cache active workflow (in production, use Redis)
        setattr(self, f"_workflow_{workflow_id}", workflow_context)
        
        return workflow_id
    
    def add_service_usage(self, workflow_id: str, service_type: ServiceType, 
                         provider: str, units_consumed: int, unit_type: str,
                         metadata: Dict[str, Any] = None) -> Dict:
        """Add service usage to an active workflow"""
        
        workflow_context = getattr(self, f"_workflow_{workflow_id}", None)
        if not workflow_context:
            return {"success": False, "error": "Workflow not found"}
        
        # Calculate cost and credits for this service
        cost_breakdown = ServicePricing.calculate_service_cost(
            service_type, provider, units_consumed, unit_type
        )
        
        service_usage = {
            "service_type": service_type.value,
            "provider": provider,
            "units_consumed": units_consumed,
            "unit_type": unit_type,
            "credits_used": cost_breakdown["credits_used"],
            "cost_usd": cost_breakdown["cost_usd"],
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        workflow_context["services_used"].append(service_usage)
        
        logger.info(f"Added {service_type.value} usage: {cost_breakdown['credits_used']} credits for {units_consumed} {unit_type}")
        
        return {
            "success": True,
            "service_usage": service_usage,
            "credits_used": cost_breakdown["credits_used"]
        }
    
    def complete_workflow(self, workflow_id: str, status_code: int = 200, 
                         error_message: str = None) -> Dict:
        """Complete workflow tracking and record to database"""
        
        workflow_context = getattr(self, f"_workflow_{workflow_id}", None)
        if not workflow_context:
            return {"success": False, "error": "Workflow not found"}
        
        try:
            # Calculate totals
            total_credits = sum(service["credits_used"] for service in workflow_context["services_used"])
            total_cost = sum(service["cost_usd"] for service in workflow_context["services_used"])
            
            duration = (datetime.utcnow() - workflow_context["start_time"]).total_seconds()
            
            # Create database record
            usage_record = MultiServiceUsageRecord(
                id=workflow_id,
                api_key=workflow_context["api_key"],
                user_id=workflow_context["user_id"],
                session_id=workflow_context.get("session_id"),
                workflow_name=workflow_context["workflow_name"],
                business_adapter=workflow_context.get("business_adapter"),
                services_used=workflow_context["services_used"],
                total_credits_used=total_credits,
                total_cost_usd=total_cost,
                total_duration_seconds=int(duration),
                endpoint=workflow_context["endpoint"],
                status_code=status_code,
                error_message=error_message
            )
            
            self.session.add(usage_record)
            self.session.commit()
            
            # Clean up workflow context
            delattr(self, f"_workflow_{workflow_id}")
            
            logger.info(f"Completed workflow {workflow_context['workflow_name']}: {total_credits} credits, {len(workflow_context['services_used'])} services")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "total_credits_used": total_credits,
                "total_cost_usd": total_cost,
                "services_count": len(workflow_context["services_used"]),
                "duration_seconds": int(duration)
            }
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to complete workflow: {e}")
            return {"success": False, "error": str(e)}
    
    def get_workflow_analytics(self, user_id: str, days: int = 30) -> Dict:
        """Get workflow analytics for user"""
        try:
            from datetime import timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Query workflow records
            records = self.session.query(MultiServiceUsageRecord).filter(
                MultiServiceUsageRecord.user_id == user_id,
                MultiServiceUsageRecord.created_at >= start_date
            ).all()
            
            # Aggregate data
            workflow_stats = {}
            service_stats = {}
            total_credits = 0
            total_cost = 0.0
            
            for record in records:
                # Workflow breakdown
                workflow_name = record.workflow_name
                if workflow_name not in workflow_stats:
                    workflow_stats[workflow_name] = {
                        "count": 0,
                        "total_credits": 0,
                        "total_cost": 0.0,
                        "avg_duration": 0
                    }
                
                workflow_stats[workflow_name]["count"] += 1
                workflow_stats[workflow_name]["total_credits"] += record.total_credits_used
                workflow_stats[workflow_name]["total_cost"] += record.total_cost_usd
                workflow_stats[workflow_name]["avg_duration"] = (
                    workflow_stats[workflow_name]["avg_duration"] + record.total_duration_seconds
                ) / workflow_stats[workflow_name]["count"]
                
                # Service breakdown
                for service in record.services_used:
                    service_key = f"{service['service_type']}_{service['provider']}"
                    if service_key not in service_stats:
                        service_stats[service_key] = {
                            "service_type": service['service_type'],
                            "provider": service['provider'],
                            "usage_count": 0,
                            "total_credits": 0,
                            "total_cost": 0.0
                        }
                    
                    service_stats[service_key]["usage_count"] += 1
                    service_stats[service_key]["total_credits"] += service['credits_used']
                    service_stats[service_key]["total_cost"] += service['cost_usd']
                
                total_credits += record.total_credits_used
                total_cost += record.total_cost_usd
            
            return {
                "period_days": days,
                "total_workflows": len(records),
                "total_credits_used": total_credits,
                "total_cost_usd": total_cost,
                "workflow_breakdown": workflow_stats,
                "service_breakdown": list(service_stats.values()),
                "most_used_workflow": max(workflow_stats.keys(), key=lambda k: workflow_stats[k]["count"]) if workflow_stats else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow analytics: {e}")
            return {"error": str(e)}
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close()

# Convenience functions for common workflow patterns
class WorkflowTemplates:
    """Pre-defined workflow templates for common service combinations"""
    
    @staticmethod
    def phone_ai_call_workflow(tracker: MultiServiceTracker, api_key: str, user_id: str,
                              phone_minutes: float, ai_tokens: int, model: str = "gpt-4o-mini") -> str:
        """Track a phone call with AI assistance workflow"""
        workflow_id = tracker.start_workflow_tracking(
            api_key=api_key,
            user_id=user_id,
            workflow_name="phone_ai_call",
            endpoint="/api/v1/phone/call"
        )
        
        # Add phone service usage
        tracker.add_service_usage(
            workflow_id=workflow_id,
            service_type=ServiceType.PHONE,
            provider="twilio",
            units_consumed=int(phone_minutes),
            unit_type="minutes"
        )
        
        # Add AI processing usage
        tracker.add_service_usage(
            workflow_id=workflow_id,
            service_type=ServiceType.GPT,
            provider=model,
            units_consumed=ai_tokens,
            unit_type="tokens"
        )
        
        return workflow_id
    
    @staticmethod
    def voice_chat_workflow(tracker: MultiServiceTracker, api_key: str, user_id: str,
                           stt_minutes: float, ai_tokens: int, tts_chars: int,
                           model: str = "gpt-4o-mini") -> str:
        """Track voice chat: Speech-to-Text + AI + Text-to-Speech"""
        workflow_id = tracker.start_workflow_tracking(
            api_key=api_key,
            user_id=user_id,
            workflow_name="voice_chat",
            endpoint="/api/v1/agent/voice"
        )
        
        # Speech-to-Text
        tracker.add_service_usage(workflow_id, ServiceType.VOICE_STT, "openai-whisper",
                                int(stt_minutes), "minutes")
        
        # AI Processing
        tracker.add_service_usage(workflow_id, ServiceType.GPT, model, ai_tokens, "tokens")
        
        # Text-to-Speech
        tracker.add_service_usage(workflow_id, ServiceType.VOICE_TTS, "openai-tts",
                                tts_chars, "characters")
        
        return workflow_id
    
    @staticmethod
    def image_analysis_workflow(tracker: MultiServiceTracker, api_key: str, user_id: str,
                               image_count: int, ai_tokens: int, model: str = "gpt-4-vision") -> str:
        """Track image analysis with AI description workflow"""
        workflow_id = tracker.start_workflow_tracking(
            api_key=api_key,
            user_id=user_id,
            workflow_name="image_analysis",
            endpoint="/api/v1/agent/vision"
        )
        
        # Vision processing
        tracker.add_service_usage(workflow_id, ServiceType.VISION, model,
                                image_count, "images")
        
        # AI text generation
        tracker.add_service_usage(workflow_id, ServiceType.GPT, model,
                                ai_tokens, "tokens")
        
        return workflow_id