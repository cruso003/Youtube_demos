"""
Data migration script for Service Configuration System
Migrates existing users to default service configurations
"""

import os
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from billing.models import User, ServiceConfiguration
from adapters.service_configuration import ServicePresets

logger = logging.getLogger(__name__)

def migrate_service_configurations():
    """Migrate existing users to use default service configurations"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nexusai")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all existing users
        users = session.query(User).all()
        logger.info(f"Found {len(users)} users to migrate")
        
        # Default configurations for each business adapter
        default_configs = {
            'general': ServicePresets.balanced(),
            'emergencyservices': ServicePresets.emergency_services(),
            'languagelearning': ServicePresets.language_learning(),
            'cost_optimized': ServicePresets.cost_optimized(),
            'premium_quality': ServicePresets.premium_quality()
        }
        
        migration_count = 0
        
        for user in users:
            logger.info(f"Migrating user: {user.email}")
            
            # Check if user already has configurations
            existing_configs = session.query(ServiceConfiguration).filter_by(user_id=user.id).count()
            
            if existing_configs > 0:
                logger.info(f"User {user.email} already has {existing_configs} configurations, skipping")
                continue
            
            # Create default configurations for each adapter
            for adapter_name, config in default_configs.items():
                service_config = ServiceConfiguration(
                    user_id=user.id,
                    business_adapter=adapter_name,
                    config_name="default",
                    is_active=True,
                    config_data=config.to_dict()
                )
                session.add(service_config)
                migration_count += 1
            
            logger.info(f"Added {len(default_configs)} default configurations for {user.email}")
        
        session.commit()
        logger.info(f"Migration completed successfully. Created {migration_count} service configurations.")
        
        return {
            "success": True,
            "users_migrated": len(users),
            "configurations_created": migration_count
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Migration failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        session.close()

def migrate_api_key_services():
    """Migrate existing API keys to use default service associations"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nexusai")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        from billing.models import APIKey, APIKeyService
        
        # Get all existing API keys
        api_keys = session.query(APIKey).filter_by(revoked=False).all()
        logger.info(f"Found {len(api_keys)} active API keys to migrate")
        
        # Default service associations
        default_services = [
            {"service_type": "gpt", "provider": "gpt-4o-mini", "enabled": True},
            {"service_type": "voice_tts", "provider": "cartesia", "enabled": True}, 
            {"service_type": "voice_stt", "provider": "deepgram", "enabled": True},
            {"service_type": "vision", "provider": "gpt-4o-vision", "enabled": True},
            {"service_type": "phone", "provider": "twilio", "enabled": True},
            {"service_type": "realtime", "provider": "livekit", "enabled": True}
        ]
        
        migration_count = 0
        
        for api_key in api_keys:
            logger.info(f"Migrating API key: {api_key.api_key[-8:]}...")
            
            # Check if API key already has service associations
            existing_services = session.query(APIKeyService).filter_by(api_key=api_key.api_key).count()
            
            if existing_services > 0:
                logger.info(f"API key {api_key.api_key[-8:]} already has {existing_services} service associations, skipping")
                continue
            
            # Create default service associations
            for service_config in default_services:
                api_key_service = APIKeyService(
                    api_key=api_key.api_key,
                    user_id=api_key.user_id,
                    service_type=service_config["service_type"],
                    provider=service_config["provider"],
                    enabled=service_config["enabled"],
                    cost_limits={"max_credits_per_request": 100}  # Default limit
                )
                session.add(api_key_service)
                migration_count += 1
            
            logger.info(f"Added {len(default_services)} service associations for API key {api_key.api_key[-8:]}")
        
        session.commit()
        logger.info(f"API key service migration completed successfully. Created {migration_count} service associations.")
        
        return {
            "success": True,
            "api_keys_migrated": len(api_keys),
            "service_associations_created": migration_count
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"API key service migration failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🔄 Starting Service Configuration Migration...")
    result1 = migrate_service_configurations()
    
    if result1["success"]:
        print(f"✅ Service configuration migration completed successfully!")
        print(f"   Users migrated: {result1['users_migrated']}")
        print(f"   Configurations created: {result1['configurations_created']}")
    else:
        print(f"❌ Service configuration migration failed: {result1['error']}")
        exit(1)
    
    print("\n🔄 Starting API Key Service Migration...")
    result2 = migrate_api_key_services()
    
    if result2["success"]:
        print(f"✅ API key service migration completed successfully!")
        print(f"   API keys migrated: {result2['api_keys_migrated']}")
        print(f"   Service associations created: {result2['service_associations_created']}")
    else:
        print(f"❌ API key service migration failed: {result2['error']}")
        exit(1)
    
    print("\n🎉 All migrations completed successfully!")