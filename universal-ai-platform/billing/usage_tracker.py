"""
Usage Tracking and Billing System
Tracks API usage and manages billing for the Universal AI Agent Platform
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class UsageMetrics:
    """Usage metrics for billing"""
    agent_id: str
    session_id: str
    timestamp: datetime
    event_type: str  # "session_start", "message_processed", "image_processed", "session_end"
    duration_seconds: Optional[float] = None
    tokens_used: Optional[int] = None
    data_size_bytes: Optional[int] = None

    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class BillingPlan:
    """Billing plan configuration"""
    plan_id: str
    name: str
    price_per_session: float
    price_per_message: float
    price_per_image: float
    price_per_minute: float
    included_sessions: int
    included_messages: int
    included_images: int
    included_minutes: int

    def to_dict(self):
        return asdict(self)

class UsageTracker:
    """Tracks usage metrics for billing purposes"""
    
    def __init__(self, db_path: str = "usage_tracking.db"):
        self.db_path = db_path
        self.active_sessions: Dict[str, datetime] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for usage tracking"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    duration_seconds REAL,
                    tokens_used INTEGER,
                    data_size_bytes INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS billing_plans (
                    plan_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    price_per_session REAL,
                    price_per_message REAL,
                    price_per_image REAL,
                    price_per_minute REAL,
                    included_sessions INTEGER,
                    included_messages INTEGER,
                    included_images INTEGER,
                    included_minutes INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS client_subscriptions (
                    client_id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    subscription_start TEXT NOT NULL,
                    subscription_end TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (plan_id) REFERENCES billing_plans (plan_id)
                )
            """)
            
            # Insert default billing plans
            self._insert_default_plans(conn)
    
    def _insert_default_plans(self, conn):
        """Insert default billing plans"""
        default_plans = [
            BillingPlan(
                plan_id="starter",
                name="Starter Plan",
                price_per_session=0.10,
                price_per_message=0.01,
                price_per_image=0.05,
                price_per_minute=0.02,
                included_sessions=100,
                included_messages=1000,
                included_images=100,
                included_minutes=300
            ),
            BillingPlan(
                plan_id="professional",
                name="Professional Plan",
                price_per_session=0.08,
                price_per_message=0.008,
                price_per_image=0.04,
                price_per_minute=0.015,
                included_sessions=500,
                included_messages=5000,
                included_images=500,
                included_minutes=1500
            ),
            BillingPlan(
                plan_id="enterprise",
                name="Enterprise Plan",
                price_per_session=0.05,
                price_per_message=0.005,
                price_per_image=0.03,
                price_per_minute=0.01,
                included_sessions=2000,
                included_messages=20000,
                included_images=2000,
                included_minutes=6000
            )
        ]
        
        for plan in default_plans:
            conn.execute("""
                INSERT OR IGNORE INTO billing_plans 
                (plan_id, name, price_per_session, price_per_message, price_per_image, 
                 price_per_minute, included_sessions, included_messages, included_images, included_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan.plan_id, plan.name, plan.price_per_session, plan.price_per_message,
                plan.price_per_image, plan.price_per_minute, plan.included_sessions,
                plan.included_messages, plan.included_images, plan.included_minutes
            ))
    
    async def track_session_start(self, agent_id: str, session_id: str):
        """Track the start of an agent session"""
        timestamp = datetime.now()
        self.active_sessions[f"{agent_id}:{session_id}"] = timestamp
        
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=timestamp,
            event_type="session_start"
        )
        
        await self._record_usage(metrics)
        logger.info(f"Session started: {agent_id}:{session_id}")
    
    async def track_session_end(self, agent_id: str, session_id: str):
        """Track the end of an agent session"""
        session_key = f"{agent_id}:{session_id}"
        start_time = self.active_sessions.get(session_key)
        
        timestamp = datetime.now()
        duration = (timestamp - start_time).total_seconds() if start_time else 0
        
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=timestamp,
            event_type="session_end",
            duration_seconds=duration
        )
        
        await self._record_usage(metrics)
        
        if session_key in self.active_sessions:
            del self.active_sessions[session_key]
        
        logger.info(f"Session ended: {agent_id}:{session_id}, duration: {duration}s")
    
    async def track_message_processed(self, agent_id: str, session_id: str = "default", tokens_used: int = None):
        """Track message processing"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="message_processed",
            tokens_used=tokens_used
        )
        
        await self._record_usage(metrics)
    
    async def track_image_processed(self, agent_id: str, session_id: str = "default", data_size_bytes: int = None):
        """Track image processing"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="image_processed",
            data_size_bytes=data_size_bytes
        )
        
        await self._record_usage(metrics)
    
    async def _record_usage(self, metrics: UsageMetrics):
        """Record usage metrics to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO usage_metrics 
                    (agent_id, session_id, timestamp, event_type, duration_seconds, tokens_used, data_size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.agent_id, metrics.session_id, metrics.timestamp.isoformat(),
                    metrics.event_type, metrics.duration_seconds, metrics.tokens_used, metrics.data_size_bytes
                ))
        except Exception as e:
            logger.error(f"Failed to record usage metrics: {e}")
    
    async def get_usage_summary(self, agent_id: str = None, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Get usage summary for billing"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Build query conditions
                conditions = []
                params = []
                
                if agent_id:
                    conditions.append("agent_id = ?")
                    params.append(agent_id)
                
                if start_date:
                    conditions.append("timestamp >= ?")
                    params.append(start_date.isoformat())
                
                if end_date:
                    conditions.append("timestamp <= ?")
                    params.append(end_date.isoformat())
                
                where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
                
                # Get counts by event type
                cursor = conn.execute(f"""
                    SELECT event_type, COUNT(*), SUM(duration_seconds), SUM(tokens_used), SUM(data_size_bytes)
                    FROM usage_metrics
                    {where_clause}
                    GROUP BY event_type
                """, params)
                
                results = cursor.fetchall()
                
                summary = {
                    "sessions": 0,
                    "messages": 0,
                    "images": 0,
                    "total_duration_minutes": 0,
                    "total_tokens": 0,
                    "total_data_mb": 0
                }
                
                for event_type, count, duration_sum, tokens_sum, data_sum in results:
                    if event_type == "session_start":
                        summary["sessions"] = count
                        summary["total_duration_minutes"] = (duration_sum or 0) / 60
                    elif event_type == "message_processed":
                        summary["messages"] = count
                        summary["total_tokens"] = tokens_sum or 0
                    elif event_type == "image_processed":
                        summary["images"] = count
                        summary["total_data_mb"] = (data_sum or 0) / (1024 * 1024)
                
                return summary
                
        except Exception as e:
            logger.error(f"Failed to get usage summary: {e}")
            return {}
    
    async def calculate_bill(self, client_id: str, plan_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate bill for a client based on usage and plan"""
        try:
            # Get plan details
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM billing_plans WHERE plan_id = ?", (plan_id,))
                plan_row = cursor.fetchone()
                
                if not plan_row:
                    raise ValueError(f"Plan {plan_id} not found")
                
                # Convert row to plan object
                plan = BillingPlan(
                    plan_id=plan_row[0], name=plan_row[1], price_per_session=plan_row[2],
                    price_per_message=plan_row[3], price_per_image=plan_row[4], price_per_minute=plan_row[5],
                    included_sessions=plan_row[6], included_messages=plan_row[7], 
                    included_images=plan_row[8], included_minutes=plan_row[9]
                )
            
            # Get usage summary for the client (assuming agent_id corresponds to client_id)
            usage = await self.get_usage_summary(agent_id=client_id, start_date=start_date, end_date=end_date)
            
            # Calculate billable usage (usage above included amounts)
            billable_sessions = max(0, usage["sessions"] - plan.included_sessions)
            billable_messages = max(0, usage["messages"] - plan.included_messages)
            billable_images = max(0, usage["images"] - plan.included_images)
            billable_minutes = max(0, usage["total_duration_minutes"] - plan.included_minutes)
            
            # Calculate costs
            session_cost = billable_sessions * plan.price_per_session
            message_cost = billable_messages * plan.price_per_message
            image_cost = billable_images * plan.price_per_image
            minute_cost = billable_minutes * plan.price_per_minute
            
            total_cost = session_cost + message_cost + image_cost + minute_cost
            
            return {
                "client_id": client_id,
                "plan": plan.to_dict(),
                "billing_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "usage": usage,
                "billable_usage": {
                    "sessions": billable_sessions,
                    "messages": billable_messages,
                    "images": billable_images,
                    "minutes": billable_minutes
                },
                "costs": {
                    "sessions": round(session_cost, 4),
                    "messages": round(message_cost, 4),
                    "images": round(image_cost, 4),
                    "minutes": round(minute_cost, 4),
                    "total": round(total_cost, 4)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate bill: {e}")
            return {}
    
    # New multimodal usage tracking methods
    async def track_voice_processed(self, agent_id: str, session_id: str, duration_seconds: float, data_size_bytes: int):
        """Track voice processing usage"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="voice_processed",
            duration_seconds=duration_seconds,
            data_size_bytes=data_size_bytes
        )
        await self._record_metrics(metrics)
    
    async def track_voice_generated(self, agent_id: str, session_id: str, text_length: int, audio_size_bytes: int):
        """Track voice generation (TTS) usage"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="voice_generated",
            tokens_used=text_length,  # Using text length as token approximation
            data_size_bytes=audio_size_bytes
        )
        await self._record_metrics(metrics)
    
    async def track_voice_conversation(self, agent_id: str, session_id: str, input_duration: float, output_text_length: int, input_size_bytes: int):
        """Track complete voice conversation usage"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="voice_conversation",
            duration_seconds=input_duration,
            tokens_used=output_text_length,
            data_size_bytes=input_size_bytes
        )
        await self._record_metrics(metrics)
    
    async def track_ocr_processed(self, agent_id: str, session_id: str, data_size_bytes: int, language: str = "en"):
        """Track OCR processing usage"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="ocr_processed",
            data_size_bytes=data_size_bytes
        )
        await self._record_metrics(metrics)
    
    async def track_image_conversation(self, agent_id: str, session_id: str, image_size_bytes: int, response_text_length: int, has_text_prompt: bool = False):
        """Track complete image conversation usage"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="image_conversation",
            tokens_used=response_text_length,
            data_size_bytes=image_size_bytes
        )
        await self._record_metrics(metrics)
    
    async def track_scene_analysis(self, agent_id: str, session_id: str, analysis_type: str, data_size_bytes: int):
        """Track specialized scene analysis usage"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="scene_analysis",
            data_size_bytes=data_size_bytes
        )
        await self._record_metrics(metrics)
    
    async def track_realtime_session_start(self, agent_id: str, session_id: str, room_name: str):
        """Track real-time session start"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="realtime_session_start"
        )
        await self._record_metrics(metrics)
    
    async def track_realtime_session_end(self, agent_id: str, session_id: str, duration_seconds: float):
        """Track real-time session end"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="realtime_session_end",
            duration_seconds=duration_seconds
        )
        await self._record_metrics(metrics)
    
    async def track_phone_call_start(self, agent_id: str, session_id: str, to_number: str, call_sid: str):
        """Track phone call initiation"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="phone_call_start"
        )
        await self._record_metrics(metrics)
    
    async def track_phone_call_end(self, agent_id: str, session_id: str, call_sid: str, duration_seconds: float):
        """Track phone call completion"""
        metrics = UsageMetrics(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="phone_call_end",
            duration_seconds=duration_seconds
        )
        await self._record_metrics(metrics)