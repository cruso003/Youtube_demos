# 🔄 MIGRATION PLAN - Universal AI Platform v2.0

## Overview
This migration updates the Universal AI Platform from single-service to multi-service architecture with enhanced credit management and service configuration system.

## 🗄️ **Database Migrations Needed**

### **1. Multi-Service Usage Tracking**
The `multi_service_usage_records` table is already created by the system automatically, but ensure it exists:

```sql
-- Already handled by MultiServiceUsageRecord model in billing/multi_service_tracker.py
-- No manual migration needed - SQLAlchemy creates this automatically
```

### **2. Enhanced User Credit Management**
The `credit_balance` field is already added to the User model in `billing/models.py`:

```sql
-- Already handled - credit_balance column exists in users table
-- Verify with: SELECT credit_balance FROM users LIMIT 1;
```

### **3. API Key Service Associations** (NEW)
This is optional for now but recommended for future service-specific API key management:

```sql
-- Optional: Create API key service associations table
CREATE TABLE IF NOT EXISTS api_key_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id UUID NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    cost_limit_per_request INTEGER DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE CASCADE
);
```

## ⚙️ **Environment Configuration Updates**

### **Current .env Requirements**
```bash
# Core Services (Already Required)
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:password@localhost:5432/nexusai

# NEW SERVICE PROVIDERS (Add These)
CARTESIA_API_KEY=your_cartesia_key
DEEPGRAM_API_KEY=your_deepgram_key  
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# OPTIONAL: Real-time Services
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret

# NEW: Service Configuration Defaults
DEFAULT_AI_MODEL=gpt-4o-mini
DEFAULT_TTS_PROVIDER=cartesia
DEFAULT_STT_PROVIDER=deepgram
COST_OPTIMIZATION_ENABLED=true
MINIMUM_CREDITS_FOR_API_KEY=5000
```

## 📊 **Data Migration Requirements**

### **✅ No Existing Data Migration Needed**

**Good news!** The system was designed to be **backward compatible**:

1. **Existing Users**: Continue working with enhanced credit management
2. **Existing API Keys**: Continue working with multi-service tracking
3. **Existing Credit Balances**: Work with new local credit manager
4. **Existing Usage Records**: Complement new multi-service tracking

### **New Users Get Enhanced Features**
- Multi-service workflow tracking
- Service configuration presets
- Advanced usage analytics
- Cost optimization recommendations

## 🔧 **Service Provider Integration**

### **New Service Provider Setup**

#### **1. Cartesia (Primary TTS)**
```bash
# Sign up at cartesia.ai
# Get API key
export CARTESIA_API_KEY=your_cartesia_key
```

#### **2. Deepgram (Primary STT)**
```bash
# Sign up at deepgram.com  
# Get API key
export DEEPGRAM_API_KEY=your_deepgram_key
```

#### **3. Twilio (Phone Services)**
```bash
# Existing Twilio setup enhanced with better cost tracking
export TWILIO_ACCOUNT_SID=your_sid
export TWILIO_AUTH_TOKEN=your_token
```

#### **4. LiveKit (Optional - Real-time Services)**
```bash
# For advanced real-time voice/video features
export LIVEKIT_URL=wss://your-server.com
export LIVEKIT_API_KEY=your_key  
export LIVEKIT_API_SECRET=your_secret
```

## 🚀 **Migration Execution Steps**

### **Step 1: Update Environment Variables** (5 minutes)
```bash
# 1. Add new service provider API keys to your .env file
cp .env .env.backup
echo "CARTESIA_API_KEY=your_key" >> .env
echo "DEEPGRAM_API_KEY=your_key" >> .env
echo "DEFAULT_AI_MODEL=gpt-4o-mini" >> .env
echo "DEFAULT_TTS_PROVIDER=cartesia" >> .env
echo "DEFAULT_STT_PROVIDER=deepgram" >> .env
```

### **Step 2: Restart Services** (2 minutes)
```bash
# Restart your API gateway to load new environment variables
sudo systemctl restart nexusai-api-gateway
# OR
docker-compose restart api-gateway
```

### **Step 3: Verify Multi-Service Tracking** (5 minutes)
```bash
# Test that multi-service usage tracking is working
curl -X POST "http://localhost:8000/api/v1/agent/create" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "You are a helpful assistant",
    "capabilities": ["text"],
    "business_logic_adapter": "languagelearning",
    "custom_settings": {
      "service_configuration": {
        "primary_ai_model": "gpt-4o-mini",
        "tts_provider": "cartesia",
        "stt_provider": "deepgram",
        "cost_optimization": true
      }
    }
  }'
```

### **Step 4: Update Client SDKs** (Optional - 10 minutes)
```bash
# If using the Python SDK
pip install --upgrade nexusai-sdk

# If using the JavaScript SDK  
npm install --save nexusai-sdk@latest
```

## ✅ **Post-Migration Verification**

### **1. Check Multi-Service Tracking**
```sql
-- Verify multi-service usage records are being created
SELECT workflow_name, total_credits_used, services_used 
FROM multi_service_usage_records 
ORDER BY created_at DESC 
LIMIT 5;
```

### **2. Check Credit Management**
```sql
-- Verify local credit management is working
SELECT id, credit_balance 
FROM users 
WHERE credit_balance > 0 
LIMIT 5;
```

### **3. Test Service Configuration**
```python
# Test Python SDK with service configuration
from nexusai_sdk import NexusAIClient, ServicePresets

client = NexusAIClient(api_key="your_api_key")
config = ServicePresets.cost_optimized()

# Should work with new service providers
cost_estimate = client.estimate_workflow_cost({
    "ai_tokens": 1000,
    "voice_minutes": 2
}, config)
print(cost_estimate)  # Should show Cartesia and Deepgram costs
```

## 🛡️ **Rollback Plan**

If issues arise, the system is designed to gracefully degrade:

### **1. Service Provider Fallback**
```bash
# If new providers fail, system falls back to OpenAI
# Set these to temporarily disable new providers:
export CARTESIA_API_KEY=""
export DEEPGRAM_API_KEY=""
```

### **2. Multi-Service Tracking Rollback**
```bash
# Multi-service tracking failures fall back to basic tracking
# No data loss - both systems run in parallel
```

### **3. Complete Rollback** (Not Recommended)
```bash
# Restore previous .env file
cp .env.backup .env
sudo systemctl restart nexusai-api-gateway
```

## 📈 **Expected Benefits After Migration**

1. **Enhanced Cost Tracking**: Per-service credit breakdown
2. **Service Optimization**: Automatic model selection for cost/quality balance  
3. **Multi-Service Workflows**: Track complex workflows across services
4. **Business Adapter Integration**: Pre-configured service stacks
5. **SDK Enhancements**: Cost estimation and service configuration
6. **Better User Experience**: Transparent pricing and usage analytics

## ⚠️ **Important Notes**

1. **Backward Compatibility**: All existing functionality continues to work
2. **Gradual Migration**: New features are opt-in, not breaking changes
3. **Service Provider Flexibility**: Easy to switch providers in the future
4. **Credit System Enhanced**: Local credit management improves reliability
5. **No Downtime Required**: Migration can be done with rolling updates

## 📞 **Support**

If you encounter issues during migration:
1. Check logs: `tail -f /var/log/nexusai/api-gateway.log`
2. Verify environment variables: `env | grep -E "(CARTESIA|DEEPGRAM|OPENAI)"`
3. Test service endpoints individually
4. Contact support with specific error messages

---

**✅ MIGRATION SUMMARY**

This migration is **low-risk** and **backward-compatible**. The main changes are:
- ✅ Enhanced multi-service credit tracking
- ✅ Service provider integration (Cartesia, Deepgram)
- ✅ Local credit management improvements
- ✅ SDK updates with service configuration support

**Total Migration Time**: ~20-30 minutes
**Downtime Required**: None (rolling updates supported)
**Risk Level**: Low (backward compatible)