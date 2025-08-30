# 🚀 MULTI-SERVICE CREDIT MANAGEMENT SYSTEM

## ✅ **COMPLETE SOLUTION FOR MULTI-SERVICE WORKFLOWS**

Your question about **phone service + GPT** combinations is now fully solved! Here's how the system handles complex service combinations and gives developers complete control.

## 🎯 **HOW MULTI-SERVICE CREDIT ALLOCATION WORKS**

### **Example 1: Phone Call with AI Assistant**
```json
{
  "workflow_name": "phone_ai_call",
  "services_used": [
    {
      "service_type": "phone",
      "provider": "twilio",
      "units_consumed": 5,
      "unit_type": "minutes",
      "credits_used": 100
    },
    {
      "service_type": "gpt",
      "provider": "gpt-4o-mini",
      "units_consumed": 3000,
      "unit_type": "tokens", 
      "credits_used": 3
    }
  ],
  "total_credits_used": 103
}
```

### **Example 2: Voice Chat (STT + AI + TTS)**
```json
{
  "workflow_name": "voice_chat",
  "services_used": [
    {
      "service_type": "voice_stt",
      "provider": "openai-whisper",
      "units_consumed": 2,
      "unit_type": "minutes",
      "credits_used": 20
    },
    {
      "service_type": "gpt", 
      "provider": "gpt-4o",
      "units_consumed": 1500,
      "unit_type": "tokens",
      "credits_used": 12
    },
    {
      "service_type": "voice_tts",
      "provider": "elevenlabs",
      "units_consumed": 450,
      "unit_type": "characters",
      "credits_used": 1
    }
  ],
  "total_credits_used": 33
}
```

## 🛠️ **DEVELOPER CONTROL THROUGH BUSINESS ADAPTERS**

### **Service Configuration in Custom Settings**
Developers can control which services to use via the `custom_settings` when creating an agent:

```python
# Emergency Services Adapter - Premium Quality
config = {
    "business_logic_adapter": "emergencyservices",
    "custom_settings": {
        "service_configuration": {
            "primary_ai_model": "gpt-4o",      # 8 credits/1K tokens
            "voice_enabled": True,
            "tts_provider": "openai-tts",      # Fast and reliable
            "stt_provider": "openai-whisper",  # High accuracy
            "phone_enabled": True,
            "phone_provider": "twilio",
            "vision_enabled": True,
            "cost_optimization": False,        # Don't optimize cost for emergencies
            "max_credits_per_request": None    # No limits for critical services
        },
        "emergency_type": "medical",
        "location": "accra_ghana"
    }
}

# Language Learning Adapter - Cost Optimized
config = {
    "business_logic_adapter": "languagelearning",
    "custom_settings": {
        "service_configuration": {
            "primary_ai_model": "gpt-4o-mini",    # 1 credit/1K tokens
            "fallback_ai_model": "claude-3-haiku", # Backup option
            "voice_enabled": True,
            "tts_provider": "cartesia",             # High-quality pronunciation
            "stt_provider": "deepgram",            # Cost-effective
            "phone_enabled": False,                # Not needed for learning
            "vision_enabled": True,                # For text recognition
            "cost_optimization": True,
            "max_credits_per_request": 75          # Budget control
        },
        "target_language": "french",
        "proficiency_level": "intermediate"
    }
}
```

## 🎮 **PRE-CONFIGURED SERVICE PRESETS**

Developers can choose from pre-built configurations:

### **1. Cost Optimized**
```python
from adapters.service_configuration import ServicePresets

config = ServicePresets.cost_optimized()
# - GPT-4o-mini (1 credit/1K tokens)
# - Deepgram STT (8 credits/minute) 
# - OpenAI TTS (0.001 credits/char)
# - Max 50 credits per request
```

### **2. Premium Quality**
```python
config = ServicePresets.premium_quality()
# - GPT-4 (25 credits/1K tokens)
# - ElevenLabs TTS (0.002 credits/char)
# - OpenAI Whisper STT (10 credits/minute)
# - No cost optimization
```

### **3. Emergency Services**
```python
config = ServicePresets.emergency_services()
# - GPT-4o (8 credits/1K tokens)
# - All services enabled
# - No cost limits
# - Prioritizes accuracy and speed
```

## 📊 **INTELLIGENT SERVICE SELECTION**

The system automatically selects the best services based on:

### **Context-Aware Model Selection**
```python
# Simple request → Auto-downgrade to cheaper model
if request_complexity == 'low' and cost_optimization == True:
    model = "gpt-4o-mini"  # Instead of expensive GPT-4

# Credit limit enforcement
if estimated_credits > max_credits_per_request:
    model = find_cheaper_alternative()
```

### **Dynamic Provider Selection**
```python
# High accuracy required → Premium provider
if accuracy_requirement == 'high':
    stt_provider = "openai-whisper"  # More expensive but accurate

# Cost optimization → Cheaper provider
if cost_optimization == True:
    stt_provider = "deepgram"  # Less expensive
```

## 🔍 **COMPREHENSIVE USAGE TRACKING**

### **Workflow-Level Analytics**
Users can see exactly how credits are used across different services:

```json
{
  "workflow_breakdown": {
    "phone_ai_call": {
      "count": 15,
      "total_credits": 1500,
      "avg_duration": 300
    },
    "voice_chat": {
      "count": 45,
      "total_credits": 900,
      "avg_duration": 120
    }
  },
  "service_breakdown": [
    {
      "service_type": "phone",
      "provider": "twilio",
      "usage_count": 15,
      "total_credits": 1200
    },
    {
      "service_type": "gpt",
      "provider": "gpt-4o-mini", 
      "usage_count": 60,
      "total_credits": 400
    }
  ]
}
```

### **Per-API-Key Breakdown**
```json
{
  "api_key": "nexus_ab12cd34",
  "workflows_used": {
    "phone_ai_call": 800,    // credits used
    "voice_chat": 300,
    "image_analysis": 150
  },
  "top_consuming_services": [
    {"service": "phone_twilio", "credits": 800},
    {"service": "gpt_gpt-4o-mini", "credits": 300}
  ]
}
```

## 🎯 **REAL-WORLD USAGE SCENARIOS**

### **Scenario 1: Emergency Medical Call**
```python
# User calls emergency service
workflow = multi_tracker.start_workflow_tracking(
    api_key="nexus_emergency_key",
    user_id="user_123", 
    workflow_name="emergency_medical_call",
    business_adapter="emergencyservices"
)

# 1. Phone call (5 minutes)
multi_tracker.add_service_usage(workflow, ServiceType.PHONE, "twilio", 5, "minutes")
# Cost: 100 credits

# 2. AI processing of medical emergency (high-quality model)
multi_tracker.add_service_usage(workflow, ServiceType.GPT, "gpt-4o", 2500, "tokens")  
# Cost: 20 credits

# 3. Text-to-speech for instructions
multi_tracker.add_service_usage(workflow, ServiceType.VOICE_TTS, "openai-tts", 800, "characters")
# Cost: 1 credit

# Total: 121 credits for critical emergency service
```

### **Scenario 2: Language Learning Session**
```python
# User practices French conversation
workflow = multi_tracker.start_workflow_tracking(
    api_key="nexus_learning_key",
    user_id="user_456",
    workflow_name="language_learning_voice_chat", 
    business_adapter="languagelearning"
)

# 1. Speech-to-text (student speaks)
multi_tracker.add_service_usage(workflow, ServiceType.VOICE_STT, "deepgram", 2, "minutes")
# Cost: 16 credits

# 2. AI language correction/feedback (cost-optimized)
multi_tracker.add_service_usage(workflow, ServiceType.GPT, "gpt-4o-mini", 1800, "tokens")
# Cost: 2 credits

# 3. Pronunciation feedback (premium voice)
multi_tracker.add_service_usage(workflow, ServiceType.VOICE_TTS, "cartesia", 600, "characters")
# Cost: 1 credit

# Total: 19 credits for educational session
```

## 💡 **KEY BENEFITS FOR DEVELOPERS**

1. **Full Service Control**: Choose exactly which AI services to use
2. **Cost Management**: Set credit limits and optimization preferences  
3. **Business Logic Integration**: Services adapt to your specific use case
4. **Transparent Pricing**: See exactly what each service costs
5. **Workflow Analytics**: Understand usage patterns across service combinations
6. **Flexible Configuration**: Switch between cost-optimized and premium quality modes

## 🚀 **HOW TO USE IN YOUR APPLICATION**

### **Step 1: Configure Services in Business Adapter**
```python
# In your custom adapter
def get_service_configuration(self):
    if self.use_case == "emergency":
        return ServicePresets.emergency_services()
    elif self.use_case == "learning":
        return ServicePresets.balanced()
    else:
        return ServicePresets.cost_optimized()
```

### **Step 2: Create Agent with Service Config**
```python
# API call to create agent
POST /api/v1/agent/create
{
    "business_logic_adapter": "emergencyservices",
    "custom_settings": {
        "service_configuration": {
            "primary_ai_model": "gpt-4o",
            "voice_enabled": true,
            "phone_enabled": true,
            "cost_optimization": false
        }
    }
}
```

### **Step 3: Track Usage Automatically**
The system automatically tracks all service usage and provides detailed breakdowns through analytics endpoints.

---

**✅ COMPLETE SOLUTION**: Your platform now handles complex multi-service workflows with transparent credit allocation, developer control, and comprehensive analytics. Users can see exactly which services are consuming credits, and developers can optimize for cost or quality based on their specific needs!