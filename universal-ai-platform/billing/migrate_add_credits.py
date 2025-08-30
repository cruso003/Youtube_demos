"""
Database migration to add credit_balance column to users table
Run this script to update your existing database
"""

import os
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)

def migrate_add_credit_balance():
    """Add credit_balance column to users table"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nexusai")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='credit_balance'
            """))
            
            if result.fetchone():
                print("✅ credit_balance column already exists")
                return True
            
            # Add the credit_balance column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN credit_balance INTEGER DEFAULT 0
            """))
            
            # Update existing users to have 0 credits
            conn.execute(text("""
                UPDATE users 
                SET credit_balance = 0 
                WHERE credit_balance IS NULL
            """))
            
            conn.commit()
            print("✅ Successfully added credit_balance column to users table")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running database migration...")
    success = migrate_add_credit_balance()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")