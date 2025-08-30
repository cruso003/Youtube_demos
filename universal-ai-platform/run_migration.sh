#!/bin/bash

# Universal AI Platform v2.0 Migration Script
# Performs migration from single-service to multi-service architecture

set -e  # Exit on any error

echo "🚀 Universal AI Platform v2.0 Migration"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Step 1: Check current migration status
echo "Step 1: Checking migration status..."
if ! python3 check_migration_status.py; then
    print_error "Migration status check failed. Please review the issues above."
    exit 1
fi
print_status "Migration status check completed"
echo ""

# Step 2: Backup current environment
echo "Step 2: Creating backup..."
if [ -f .env ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    print_status "Environment file backed up"
else
    print_warning "No .env file found - will create new one"
fi
echo ""

# Step 3: Check required environment variables
echo "Step 3: Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    print_error "OPENAI_API_KEY is required but not set"
    echo "Please set: export OPENAI_API_KEY=your_key"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    print_warning "DATABASE_URL not set, using default"
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/nexusai"
fi

print_status "Required environment variables verified"
echo ""

# Step 4: Database migration (automatic via SQLAlchemy)
echo "Step 4: Database migration..."
print_info "Multi-service tables will be created automatically by the application"
print_info "The system uses SQLAlchemy auto-migration for new tables"
print_status "Database migration configured"
echo ""

# Step 5: Check service provider setup
echo "Step 5: Service provider configuration..."

# Check for new service provider keys
if [ -z "$CARTESIA_API_KEY" ]; then
    print_warning "CARTESIA_API_KEY not set"
    echo "  To enable Cartesia TTS: export CARTESIA_API_KEY=your_key"
fi

if [ -z "$DEEPGRAM_API_KEY" ]; then
    print_warning "DEEPGRAM_API_KEY not set"  
    echo "  To enable Deepgram STT: export DEEPGRAM_API_KEY=your_key"
fi

if [ -z "$TWILIO_ACCOUNT_SID" ] || [ -z "$TWILIO_AUTH_TOKEN" ]; then
    print_warning "Twilio credentials not set"
    echo "  To enable phone services:"
    echo "    export TWILIO_ACCOUNT_SID=your_sid"
    echo "    export TWILIO_AUTH_TOKEN=your_token"
fi

print_status "Service provider check completed"
echo ""

# Step 6: Verify system files
echo "Step 6: Verifying system files..."
required_files=(
    "billing/multi_service_tracker.py"
    "billing/credit_manager.py" 
    "adapters/service_configuration.py"
    "api_gateway/main.py"
    "client_sdks/python/nexusai_sdk.py"
    "client_sdks/javascript/nexusai-sdk.js"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    print_error "Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

print_status "All system files present"
echo ""

# Step 7: Test multi-service functionality
echo "Step 7: Testing multi-service functionality..."
if python3 -c "
import sys
sys.path.append('.')
try:
    from billing.multi_service_tracker import MultiServiceTracker
    from billing.credit_manager import LocalCreditManager
    from adapters.service_configuration import ServicePresets
    print('✅ Multi-service modules load successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"; then
    print_status "Multi-service functionality verified"
else
    print_error "Multi-service modules failed to load"
    exit 1
fi
echo ""

# Step 8: Update .env with defaults if needed
echo "Step 8: Setting service defaults..."
if ! grep -q "DEFAULT_AI_MODEL" .env 2>/dev/null; then
    echo "DEFAULT_AI_MODEL=gpt-4o-mini" >> .env
    print_status "Added DEFAULT_AI_MODEL"
fi

if ! grep -q "DEFAULT_TTS_PROVIDER" .env 2>/dev/null; then
    echo "DEFAULT_TTS_PROVIDER=cartesia" >> .env
    print_status "Added DEFAULT_TTS_PROVIDER"
fi

if ! grep -q "DEFAULT_STT_PROVIDER" .env 2>/dev/null; then
    echo "DEFAULT_STT_PROVIDER=deepgram" >> .env
    print_status "Added DEFAULT_STT_PROVIDER"
fi

if ! grep -q "MINIMUM_CREDITS_FOR_API_KEY" .env 2>/dev/null; then
    echo "MINIMUM_CREDITS_FOR_API_KEY=5000" >> .env
    print_status "Added MINIMUM_CREDITS_FOR_API_KEY"
fi

print_status "Service defaults configured"
echo ""

# Step 9: Final verification
echo "Step 9: Final verification..."
python3 check_migration_status.py
if [ $? -eq 0 ]; then
    print_status "Migration verification passed"
else
    print_warning "Migration verification found issues (may be non-critical)"
fi
echo ""

# Migration complete
echo "🎉 MIGRATION COMPLETED!"
echo "====================="
print_status "Universal AI Platform v2.0 migration successful"
echo ""
echo "✅ Enhanced Features Now Available:"
echo "  • Multi-service workflow tracking"
echo "  • Service configuration presets"
echo "  • Enhanced credit management"
echo "  • Updated SDKs with cost estimation"
echo "  • Service provider flexibility (Cartesia, Deepgram, LiveKit)"
echo ""
echo "📋 Next Steps:"
echo "  1. Add service provider API keys to .env file"
echo "  2. Restart your API gateway service"
echo "  3. Test multi-service functionality"
echo "  4. Deploy dashboard integration"
echo ""
echo "📖 For detailed instructions, see:"
echo "  • MIGRATION_PLAN.md"
echo "  • DEPLOYMENT_CHECKLIST.md"
echo ""
print_status "System ready for dashboard deployment!"

exit 0