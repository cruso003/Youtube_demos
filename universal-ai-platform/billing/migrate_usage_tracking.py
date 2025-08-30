"""
Database migration to add API usage tracking tables
Run this script to add detailed usage analytics
"""

import os
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)

def migrate_add_usage_tracking():
    """Add API usage tracking table"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nexusai")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if table already exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='api_usage_records'
            """))
            
            if result.fetchone():
                print("✅ api_usage_records table already exists")
                return True
            
            # Create the API usage tracking table
            conn.execute(text("""
                CREATE TABLE api_usage_records (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    api_key VARCHAR NOT NULL,
                    user_id UUID NOT NULL,
                    endpoint VARCHAR NOT NULL,
                    method VARCHAR NOT NULL,
                    model VARCHAR,
                    
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    credits_used INTEGER NOT NULL,
                    
                    input_cost DECIMAL(10,6) DEFAULT 0.0,
                    output_cost DECIMAL(10,6) DEFAULT 0.0,
                    total_cost DECIMAL(10,6) DEFAULT 0.0,
                    
                    request_size_bytes INTEGER DEFAULT 0,
                    response_size_bytes INTEGER DEFAULT 0,
                    processing_time_ms INTEGER DEFAULT 0,
                    
                    status_code INTEGER DEFAULT 200,
                    error_message TEXT,
                    session_id VARCHAR,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create indexes for performance
            conn.execute(text("""
                CREATE INDEX idx_api_usage_api_key ON api_usage_records(api_key);
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_api_usage_user_id ON api_usage_records(user_id);
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_api_usage_created_at ON api_usage_records(created_at);
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_api_usage_model ON api_usage_records(model);
            """))
            
            conn.commit()
            print("✅ Successfully created api_usage_records table with indexes")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running usage tracking migration...")
    success = migrate_add_usage_tracking()
    if success:
        print("✅ Usage tracking migration completed successfully!")
    else:
        print("❌ Usage tracking migration failed!")