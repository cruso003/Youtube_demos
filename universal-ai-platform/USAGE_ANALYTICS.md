# 📊 COMPREHENSIVE USAGE ANALYTICS SYSTEM

## ✅ **WHAT WE NOW HAVE**: Advanced Credit & Usage Management

### 🎯 **Per-API-Key Usage Tracking**
- **Individual Key Analytics**: Track usage for each API key separately
- **Credit Attribution**: Know exactly which key is "burning credits"
- **Model-Specific Pricing**: Different credit costs per AI model
- **Detailed Breakdowns**: Input/output tokens, processing time, costs

### 💰 **Smart Credit Calculation System**

#### **Model-Based Pricing** (`billing/api_usage_tracker.py:33-70`):
```python
PRICING = {
    "gpt-4o-mini": 1 credit per 1K tokens    # Cheapest
    "gpt-4o":      8 credits per 1K tokens   # Standard GPT-4
    "gpt-4":       25 credits per 1K tokens  # Most expensive
    "claude-3-haiku": 1 credit per 1K tokens # Anthropic cheap
    "claude-3-sonnet": 12 credits per 1K tokens # Anthropic premium
}
```

#### **Accurate Token Tracking**:
- **Input tokens**: System prompts + user messages
- **Output tokens**: AI response generation
- **Total cost**: Model-specific pricing applied
- **Real-time deduction**: Credits deducted immediately after API call

### 📈 **Usage Analytics Endpoints**

#### **1. User Overview** - `/api/v1/users/{user_id}/usage/summary`
```json
{
  "current_credit_balance": 8500,
  "active_api_keys": 3,
  "last_7_days": {
    "total_requests": 150,
    "total_credits_used": 1200,
    "models_used": ["gpt-4o-mini", "claude-3-haiku"]
  },
  "top_consuming_keys": [
    {"api_key": "nexus_ab...de12", "credits_used": 800},
    {"api_key": "nexus_cd...fg34", "credits_used": 300}
  ]
}
```

#### **2. Detailed Analytics** - `/api/v1/users/{user_id}/usage/analytics?days=30`
```json
{
  "total_statistics": {
    "total_requests": 450,
    "total_credits": 3200,
    "total_cost": 3.20,
    "models_used": ["gpt-4o-mini", "gpt-4o"]
  },
  "api_key_breakdown": [
    {
      "api_key": "ab12cd34",
      "requests": 200,
      "credits_used": 1800,
      "models": {"gpt-4o-mini": 150, "gpt-4o": 50},
      "endpoints": {"/api/v1/agent/message": 200},
      "avg_processing_time": 1200,
      "error_rate": 2.5
    }
  ]
}
```

#### **3. Model Breakdown** - `/api/v1/users/{user_id}/usage/models?days=30`
```json
{
  "model_breakdown": [
    {
      "model": "gpt-4o-mini",
      "requests": 300,
      "credits_used": 900,
      "total_cost": 0.45,
      "avg_credits_per_request": 3,
      "avg_tokens_per_request": 3000
    },
    {
      "model": "gpt-4o", 
      "requests": 50,
      "credits_used": 2300,
      "total_cost": 2.30,
      "avg_credits_per_request": 46,
      "avg_tokens_per_request": 5750
    }
  ]
}
```

#### **4. Individual API Key Usage** - `/api/v1/api-keys/{api_key}/usage?days=7&limit=50`
```json
{
  "api_key": "nexus_ab...de12",
  "usage_records": [
    {
      "endpoint": "/api/v1/agent/message",
      "model": "gpt-4o-mini",
      "input_tokens": 150,
      "output_tokens": 300,
      "total_tokens": 450,
      "credits_used": 1,
      "total_cost": 0.00045,
      "processing_time_ms": 1200,
      "created_at": "2025-08-30T10:30:00Z"
    }
  ]
}
```

## 🔍 **HOW CREDITS ARE CALCULATED**

### **Current Smart Calculation** (`api_gateway/main.py:347-394`):
1. **Get Actual Usage**: Extract input/output tokens from OpenAI response
2. **Model-Specific Pricing**: Apply correct credit rate per model
3. **Real-time Tracking**: Record detailed usage immediately
4. **Credit Deduction**: Subtract from user balance atomically

### **Example Credit Calculation**:
```python
# User makes API call with gpt-4o-mini
input_tokens = 200    # System prompt + user message
output_tokens = 400   # AI response
total_tokens = 600

# Model pricing: 1 credit per 1K tokens for gpt-4o-mini
credits_used = max(1, (600 / 1000) * 1) = 1 credit

# If they used gpt-4o instead:
credits_used = max(1, (600 / 1000) * 8) = 5 credits
```

## 📊 **USAGE PATTERNS YOU CAN NOW TRACK**

### **Per API Key Analytics**:
- Which key is making the most requests?
- Which key is consuming the most credits?
- Error rates per key
- Average processing time per key
- Model preference per key

### **Cost Optimization Insights**:
- Which models are most cost-effective?
- Are users choosing expensive models unnecessarily?
- Peak usage times and patterns
- Token efficiency per request

### **Business Intelligence**:
- User engagement levels
- Feature adoption (which endpoints used most)
- Revenue per user calculations
- Credit consumption forecasting

## 🚀 **DEPLOYMENT INSTRUCTIONS**

### **1. Run Database Migration**
```bash
cd /path/to/universal-ai-platform
python billing/migrate_usage_tracking.py
```

### **2. Restart API Gateway**
```bash
python api_gateway/main.py
```

### **3. Test the New Analytics**
```bash
# Get user usage summary
curl -H "Authorization: Bearer {jwt_token}" \
     http://localhost:8000/api/v1/users/{user_id}/usage/summary

# Get detailed analytics
curl -H "Authorization: Bearer {jwt_token}" \
     http://localhost:8000/api/v1/users/{user_id}/usage/analytics?days=30

# Get specific API key usage
curl -H "Authorization: Bearer {jwt_token}" \
     http://localhost:8000/api/v1/api-keys/{api_key}/usage?days=7
```

## 🎯 **KEY BENEFITS FOR USERS**

1. **Credit Visibility**: Users know exactly where their credits are going
2. **Cost Control**: Identify expensive usage patterns
3. **Performance Monitoring**: Track API response times
4. **Multi-Key Management**: Monitor separate applications/environments
5. **Model Optimization**: Choose cost-effective AI models
6. **Usage Forecasting**: Predict when to purchase more credits

## 🔒 **SECURITY & PRIVACY**

- **API Key Masking**: Only show last 8 chars in analytics
- **User Isolation**: Users can only see their own analytics
- **Admin Override**: Admins can view any user's analytics
- **JWT Authentication**: All analytics endpoints require valid JWT
- **Data Retention**: Configurable retention periods for usage data

---

**✅ COMPLETE SOLUTION**: Your platform now has enterprise-grade usage analytics with per-API-key tracking, model-specific pricing, and comprehensive cost breakdowns!