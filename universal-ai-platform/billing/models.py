from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)  # hashed password
    role = Column(String, default="USER", nullable=False)  # USER, ADMIN, SUPER_ADMIN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    first_payment_at = Column(DateTime, nullable=True)  # Set on first successful payment
    credit_balance = Column(Integer, default=0)  # Current credit balance

class APIKey(Base):
    __tablename__ = 'api_keys'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)

class CreditTransaction(Base):
    __tablename__ = 'credit_transactions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    credits = Column(Integer, nullable=False)
    amount_usd = Column(Float)
    transaction_id = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ServiceConfiguration(Base):
    """Service configuration per user/business adapter"""
    __tablename__ = 'service_configurations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    business_adapter = Column(String, nullable=False)  # 'emergencyservices', 'languagelearning', etc.
    config_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    config_data = Column(JSON, nullable=False)  # ServiceConfiguration as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APIKeyService(Base):
    """Service-specific API key configurations"""
    __tablename__ = 'api_key_services'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key = Column(String, ForeignKey('api_keys.api_key'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    service_type = Column(String, nullable=False)  # 'gpt', 'voice_tts', 'voice_stt', etc.
    provider = Column(String, nullable=False)      # 'cartesia', 'deepgram', 'twilio', etc.
    enabled = Column(Boolean, default=True)
    cost_limits = Column(JSON, nullable=True)      # Per-service cost limits
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
