#!/usr/bin/env python3
"""
Migration Status Checker for Universal AI Platform v2.0
Checks what migrations are needed after the recent updates
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError
import psycopg2
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationChecker:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nexusai")
        self.required_env_vars = [
            "OPENAI_API_KEY",
            "DATABASE_URL"
        ]
        self.new_env_vars = [
            "CARTESIA_API_KEY", 
            "DEEPGRAM_API_KEY",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN"
        ]
        self.optional_env_vars = [
            "LIVEKIT_URL",
            "LIVEKIT_API_KEY", 
            "LIVEKIT_API_SECRET"
        ]

    def check_database_connection(self) -> bool:
        """Check if database connection works"""
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def check_required_tables(self) -> Dict[str, bool]:
        """Check if required tables exist"""
        required_tables = [
            "users",
            "api_keys", 
            "credit_transactions",
            "multi_service_usage_records"
        ]
        
        table_status = {}
        
        try:
            engine = create_engine(self.database_url)
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            for table in required_tables:
                exists = table in existing_tables
                table_status[table] = exists
                status = "✅" if exists else "❌"
                logger.info(f"{status} Table '{table}': {'EXISTS' if exists else 'MISSING'}")
                
        except Exception as e:
            logger.error(f"❌ Failed to check tables: {e}")
            return {}
            
        return table_status

    def check_user_credit_balance_column(self) -> bool:
        """Check if users table has credit_balance column"""
        try:
            engine = create_engine(self.database_url)
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            has_credit_balance = 'credit_balance' in columns
            status = "✅" if has_credit_balance else "❌"
            logger.info(f"{status} Users table credit_balance column: {'EXISTS' if has_credit_balance else 'MISSING'}")
            
            return has_credit_balance
        except Exception as e:
            logger.error(f"❌ Failed to check credit_balance column: {e}")
            return False

    def check_environment_variables(self) -> Dict[str, Tuple[bool, str]]:
        """Check environment variable status"""
        env_status = {}
        
        # Check required variables
        logger.info("\n📋 Required Environment Variables:")
        for var in self.required_env_vars:
            value = os.getenv(var)
            exists = value is not None and value != ""
            status = "✅" if exists else "❌"
            logger.info(f"{status} {var}: {'SET' if exists else 'MISSING'}")
            env_status[var] = (exists, "required")
            
        # Check new service provider variables
        logger.info("\n🆕 New Service Provider Variables:")
        for var in self.new_env_vars:
            value = os.getenv(var)
            exists = value is not None and value != ""
            status = "✅" if exists else "⚠️"
            logger.info(f"{status} {var}: {'SET' if exists else 'NOT SET (recommended)'}")
            env_status[var] = (exists, "new")
            
        # Check optional variables
        logger.info("\n🔧 Optional Service Variables:")
        for var in self.optional_env_vars:
            value = os.getenv(var)
            exists = value is not None and value != ""
            status = "✅" if exists else "⏸️"
            logger.info(f"{status} {var}: {'SET' if exists else 'NOT SET (optional)'}")
            env_status[var] = (exists, "optional")
            
        return env_status

    def check_multi_service_files(self) -> Dict[str, bool]:
        """Check if multi-service system files exist"""
        required_files = {
            "billing/multi_service_tracker.py": "Multi-service usage tracking",
            "billing/credit_manager.py": "Local credit management", 
            "adapters/service_configuration.py": "Service configuration system",
            "client_sdks/python/nexusai_sdk.py": "Updated Python SDK",
            "client_sdks/javascript/nexusai-sdk.js": "Updated JavaScript SDK"
        }
        
        file_status = {}
        logger.info("\n📁 Multi-Service System Files:")
        
        for filepath, description in required_files.items():
            exists = os.path.exists(filepath)
            status = "✅" if exists else "❌"
            logger.info(f"{status} {filepath}: {description}")
            file_status[filepath] = exists
            
        return file_status

    def generate_migration_report(self) -> Dict:
        """Generate comprehensive migration status report"""
        logger.info("🔍 UNIVERSAL AI PLATFORM - MIGRATION STATUS CHECK")
        logger.info("=" * 60)
        
        report = {
            "database_connection": self.check_database_connection(),
            "tables": self.check_required_tables(),
            "credit_balance_column": self.check_user_credit_balance_column(),
            "environment_variables": self.check_environment_variables(),
            "system_files": self.check_multi_service_files()
        }
        
        return report

    def print_migration_recommendations(self, report: Dict):
        """Print specific migration recommendations based on report"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 MIGRATION RECOMMENDATIONS")
        logger.info("=" * 60)
        
        needs_migration = []
        
        # Check database issues
        if not report["database_connection"]:
            needs_migration.append("🔧 Fix database connection")
            logger.error("❌ CRITICAL: Database connection failed")
            
        missing_tables = [table for table, exists in report["tables"].items() if not exists]
        if missing_tables:
            needs_migration.append("🗄️ Create missing database tables")
            logger.warning(f"⚠️ Missing tables: {', '.join(missing_tables)}")
            
        if not report["credit_balance_column"]:
            needs_migration.append("🔧 Add credit_balance column to users table")
            logger.warning("⚠️ Users table missing credit_balance column")
            
        # Check environment variables
        env_vars = report["environment_variables"]
        missing_required = [var for var, (exists, type_) in env_vars.items() if type_ == "required" and not exists]
        if missing_required:
            needs_migration.append("⚙️ Set required environment variables")
            logger.error(f"❌ Missing required env vars: {', '.join(missing_required)}")
            
        missing_new = [var for var, (exists, type_) in env_vars.items() if type_ == "new" and not exists]
        if missing_new:
            needs_migration.append("🆕 Add new service provider API keys")
            logger.warning(f"⚠️ Recommended new env vars: {', '.join(missing_new)}")
            
        # Check system files
        missing_files = [file for file, exists in report["system_files"].items() if not exists]
        if missing_files:
            needs_migration.append("📁 Update system files")
            logger.error(f"❌ Missing system files: {', '.join(missing_files)}")
            
        # Print final recommendations
        if not needs_migration:
            logger.info("🎉 EXCELLENT! No migration needed - system is ready!")
            logger.info("✅ All components are up to date and working")
            logger.info("🚀 You can proceed with dashboard deployment")
        else:
            logger.info(f"📝 {len(needs_migration)} migration steps needed:")
            for i, step in enumerate(needs_migration, 1):
                logger.info(f"   {i}. {step}")
                
            logger.info("\n📖 See MIGRATION_PLAN.md for detailed instructions")
            logger.info("⏱️ Estimated migration time: 20-30 minutes")

def main():
    """Main execution function"""
    checker = MigrationChecker()
    
    try:
        report = checker.generate_migration_report()
        checker.print_migration_recommendations(report)
        
        # Return appropriate exit code
        has_critical_issues = (
            not report["database_connection"] or 
            not all(report["tables"].values()) or
            not report["credit_balance_column"] or
            not all(exists for var, (exists, type_) in report["environment_variables"].items() if type_ == "required")
        )
        
        return 1 if has_critical_issues else 0
        
    except Exception as e:
        logger.error(f"❌ Migration check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())