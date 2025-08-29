# Business Logic Adapters Guide

Business Logic Adapters are the heart of the Universal AI Platform's customization system. They allow you to tailor agent behavior for specific use cases without modifying the core platform.

## What Are Business Logic Adapters?

Business Logic Adapters are pluggable components that:

- **Process user input** before it reaches the AI agent
- **Modify agent responses** based on domain-specific rules
- **Implement custom workflows** for specific industries or use cases
- **Add validation and safety checks** for critical applications
- **Integrate with external systems** and APIs

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│ Business Logic   │───▶│  AI Agent       │
│                 │    │ Adapter          │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Custom Processing│    │  Agent Response │
                       │ & Validation     │    │                 │
                       └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ External Systems │
                       │ APIs, Databases  │
                       └──────────────────┘
```

## Built-in Adapters

### Language Learning Adapter

Optimized for educational applications with features like:

- **Target language detection** and context switching
- **Proficiency level adjustment** for appropriate difficulty
- **Gentle error correction** without discouraging users
- **Conversation topic guidance** based on learning objectives
- **Progress tracking** and vocabulary building

**Configuration**:
```python
config = {
    "target_language": "Spanish",
    "proficiency_level": "beginner",
    "conversation_topics": ["daily activities", "food", "travel"],
    "correction_style": "gentle",
    "vocabulary_focus": ["present_tense", "basic_nouns"]
}
```

**Example Usage**:
```python
from universal_ai_sdk import UniversalAIClient, AgentConfig

client = UniversalAIClient()
config = AgentConfig(
    instructions="You are a language learning assistant",
    capabilities=["text", "voice"],
    business_logic_adapter="languagelearning",
    custom_settings={
        "target_language": "Spanish",
        "proficiency_level": "beginner"
    }
)

session = client.create_agent(config)
```

### Emergency Services Adapter

Designed for emergency response scenarios with:

- **Priority escalation detection** based on keywords and urgency
- **Location information extraction** and validation
- **Emergency type classification** (medical, fire, police, etc.)
- **Call logging and tracking** for compliance
- **Integration with dispatch systems**

**Configuration**:
```python
config = {
    "emergency_types": ["medical", "fire", "police", "natural_disaster"],
    "location_required": True,
    "escalation_keywords": ["unconscious", "bleeding", "fire", "chest_pain"],
    "response_time_critical": True,
    "dispatch_integration": {
        "api_endpoint": "https://dispatch.emergency.gov/api/v1",
        "api_key": "your_dispatch_api_key"
    }
}
```

**Example Usage**:
```python
config = AgentConfig(
    instructions="You are an emergency services dispatcher. Gather critical information quickly.",
    capabilities=["text", "voice"],
    business_logic_adapter="emergencyservices",
    custom_settings={
        "emergency_types": ["medical", "fire", "police"],
        "location_required": True
    }
)
```

## Creating Custom Adapters

### Step 1: Define the Adapter Class

```python
from adapters.business_logic_adapter import BusinessLogicAdapter

class HealthcareAdapter(BusinessLogicAdapter):
    def __init__(self, custom_settings=None):
        super().__init__(custom_settings)
        
        # Healthcare-specific settings
        self.hipaa_compliance = custom_settings.get('hipaa_compliance', True)
        self.specialty = custom_settings.get('specialty', 'general')
        self.patient_privacy_level = custom_settings.get('patient_privacy_level', 'strict')
        
        # Initialize medical knowledge base
        self.medical_terms = self._load_medical_terms()
        self.drug_interactions = self._load_drug_interactions()
    
    def process_user_input(self, user_input, session_context):
        """Process user input for healthcare context"""
        
        # Remove any PII if HIPAA compliance is enabled
        if self.hipaa_compliance:
            user_input = self._sanitize_pii(user_input)
        
        # Extract medical symptoms and concerns
        medical_context = self._extract_medical_context(user_input)
        
        # Add to session context
        session_context['medical_context'] = medical_context
        session_context['requires_physician_review'] = self._requires_physician_review(medical_context)
        
        return user_input, session_context
    
    def process_agent_response(self, agent_response, session_context):
        """Process agent response for healthcare safety"""
        
        # Check for medical advice disclaimer
        if self._contains_medical_advice(agent_response):
            agent_response = self._add_medical_disclaimer(agent_response)
        
        # Check for drug interaction warnings
        if 'medications' in session_context.get('medical_context', {}):
            agent_response = self._check_drug_interactions(agent_response, session_context)
        
        # Flag for physician review if needed
        if session_context.get('requires_physician_review'):
            self._flag_for_physician_review(session_context)
        
        return agent_response
    
    def _sanitize_pii(self, text):
        """Remove personally identifiable information"""
        # Implement PII detection and removal
        # This is a simplified example
        import re
        
        # Remove SSN patterns
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED]', text)
        # Remove phone patterns
        text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[REDACTED]', text)
        
        return text
    
    def _extract_medical_context(self, text):
        """Extract medical symptoms and context"""
        medical_context = {
            'symptoms': [],
            'medications': [],
            'allergies': [],
            'urgency_level': 'low'
        }
        
        # Use NLP to extract medical entities
        # This would integrate with medical NLP libraries
        symptoms = self._extract_symptoms(text)
        medications = self._extract_medications(text)
        
        medical_context['symptoms'] = symptoms
        medical_context['medications'] = medications
        
        # Determine urgency based on symptoms
        if any(urgent in text.lower() for urgent in ['chest pain', 'difficulty breathing', 'severe bleeding']):
            medical_context['urgency_level'] = 'high'
        
        return medical_context
    
    def _requires_physician_review(self, medical_context):
        """Determine if case needs physician review"""
        high_risk_symptoms = ['chest pain', 'stroke symptoms', 'severe allergic reaction']
        
        for symptom in medical_context.get('symptoms', []):
            if any(risk in symptom.lower() for risk in high_risk_symptoms):
                return True
        
        return medical_context.get('urgency_level') == 'high'
    
    def _add_medical_disclaimer(self, response):
        """Add medical disclaimer to responses"""
        disclaimer = "\n\n⚠️ **Medical Disclaimer**: This information is for educational purposes only and is not a substitute for professional medical advice. Please consult with a healthcare provider for medical concerns."
        return response + disclaimer
```

### Step 2: Register the Adapter

```python
# In adapters/__init__.py
from .healthcare_adapter import HealthcareAdapter

# Register the adapter
AVAILABLE_ADAPTERS = {
    'languagelearning': 'adapters.language_learning_adapter.LanguageLearningAdapter',
    'emergencyservices': 'adapters.emergency_services_adapter.EmergencyServicesAdapter',
    'healthcare': 'adapters.healthcare_adapter.HealthcareAdapter',  # New adapter
}

def get_adapter(adapter_name, custom_settings=None):
    """Get adapter instance by name"""
    if adapter_name not in AVAILABLE_ADAPTERS:
        raise ValueError(f"Unknown adapter: {adapter_name}")
    
    module_path, class_name = AVAILABLE_ADAPTERS[adapter_name].rsplit('.', 1)
    module = __import__(module_path, fromlist=[class_name])
    adapter_class = getattr(module, class_name)
    
    return adapter_class(custom_settings)
```

### Step 3: Configure and Use

```python
# Using the new healthcare adapter
from universal_ai_sdk import UniversalAIClient, AgentConfig

client = UniversalAIClient()

healthcare_config = AgentConfig(
    instructions="""You are a healthcare assistant. Help patients understand their symptoms and guide them to appropriate care.
    
    Guidelines:
    - Always recommend consulting with healthcare providers
    - Never provide specific medical diagnoses
    - Be empathetic and supportive
    - Focus on symptom documentation and care guidance
    """,
    capabilities=["text", "voice"],
    business_logic_adapter="healthcare",
    custom_settings={
        "hipaa_compliance": True,
        "specialty": "primary_care",
        "patient_privacy_level": "strict",
        "require_physician_review": True
    }
)

session = client.create_agent(healthcare_config)
```

## Advanced Adapter Features

### External API Integration

```python
class ECommerceAdapter(BusinessLogicAdapter):
    def __init__(self, custom_settings=None):
        super().__init__(custom_settings)
        self.product_api = custom_settings.get('product_api_url')
        self.inventory_api = custom_settings.get('inventory_api_url')
        self.api_key = custom_settings.get('api_key')
    
    async def process_user_input(self, user_input, session_context):
        """Process e-commerce queries with real-time data"""
        
        # Extract product queries
        if self._is_product_query(user_input):
            product_info = await self._fetch_product_info(user_input)
            session_context['product_context'] = product_info
        
        # Check inventory for mentioned products
        if self._mentions_products(user_input):
            inventory_status = await self._check_inventory(user_input)
            session_context['inventory_status'] = inventory_status
        
        return user_input, session_context
    
    async def _fetch_product_info(self, query):
        """Fetch real-time product information"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.product_api}/search",
                params={'q': query},
                headers={'Authorization': f'Bearer {self.api_key}'}
            ) as response:
                return await response.json()
```

### State Management

```python
class ConversationStateAdapter(BusinessLogicAdapter):
    def __init__(self, custom_settings=None):
        super().__init__(custom_settings)
        self.conversation_states = {}
        self.max_context_turns = custom_settings.get('max_context_turns', 10)
    
    def process_user_input(self, user_input, session_context):
        """Maintain conversation state and context"""
        session_id = session_context.get('session_id')
        
        # Initialize state if new session
        if session_id not in self.conversation_states:
            self.conversation_states[session_id] = {
                'turns': [],
                'topics': [],
                'user_preferences': {},
                'conversation_goal': None
            }
        
        state = self.conversation_states[session_id]
        
        # Add current turn to history
        state['turns'].append({
            'type': 'user',
            'content': user_input,
            'timestamp': time.time()
        })
        
        # Limit context size
        if len(state['turns']) > self.max_context_turns * 2:
            state['turns'] = state['turns'][-self.max_context_turns * 2:]
        
        # Extract topics and preferences
        self._update_conversation_context(user_input, state)
        
        # Add state to session context
        session_context['conversation_state'] = state
        
        return user_input, session_context
    
    def _update_conversation_context(self, user_input, state):
        """Update conversation topics and user preferences"""
        # Extract topics using NLP
        topics = self._extract_topics(user_input)
        state['topics'].extend(topics)
        
        # Keep only recent topics
        state['topics'] = list(set(state['topics'][-20:]))
        
        # Extract preferences
        preferences = self._extract_preferences(user_input)
        state['user_preferences'].update(preferences)
```

### Multi-Language Support

```python
class MultiLanguageAdapter(BusinessLogicAdapter):
    def __init__(self, custom_settings=None):
        super().__init__(custom_settings)
        self.supported_languages = custom_settings.get('supported_languages', ['en', 'es', 'fr'])
        self.auto_detect_language = custom_settings.get('auto_detect_language', True)
        self.translation_service = custom_settings.get('translation_service', 'google')
    
    def process_user_input(self, user_input, session_context):
        """Handle multi-language input"""
        
        # Detect language if enabled
        if self.auto_detect_language:
            detected_language = self._detect_language(user_input)
            session_context['detected_language'] = detected_language
            
            # Translate to primary language if needed
            if detected_language not in self.supported_languages:
                translated_input = self._translate_text(user_input, detected_language, 'en')
                session_context['original_input'] = user_input
                session_context['translation_applied'] = True
                user_input = translated_input
        
        return user_input, session_context
    
    def process_agent_response(self, agent_response, session_context):
        """Translate response back to user's language if needed"""
        
        if session_context.get('translation_applied'):
            original_language = session_context.get('detected_language')
            if original_language:
                agent_response = self._translate_text(agent_response, 'en', original_language)
        
        return agent_response
```

## Adapter Configuration

### Environment-Based Configuration

```python
# config/adapter_config.py
import os

class AdapterConfig:
    # Language Learning Adapter
    LANGUAGE_LEARNING_SETTINGS = {
        'supported_languages': os.environ.get('SUPPORTED_LANGUAGES', 'Spanish,French,German').split(','),
        'default_proficiency': os.environ.get('DEFAULT_PROFICIENCY', 'beginner'),
        'max_session_length': int(os.environ.get('MAX_SESSION_LENGTH', '60')),  # minutes
    }
    
    # Emergency Services Adapter
    EMERGENCY_SERVICES_SETTINGS = {
        'dispatch_api_url': os.environ.get('DISPATCH_API_URL'),
        'dispatch_api_key': os.environ.get('DISPATCH_API_KEY'),
        'location_service_url': os.environ.get('LOCATION_SERVICE_URL'),
        'emergency_contacts': os.environ.get('EMERGENCY_CONTACTS', '911,112,999').split(','),
    }
    
    # Healthcare Adapter
    HEALTHCARE_SETTINGS = {
        'hipaa_compliance': os.environ.get('HIPAA_COMPLIANCE', 'true').lower() == 'true',
        'medical_api_url': os.environ.get('MEDICAL_API_URL'),
        'medical_api_key': os.environ.get('MEDICAL_API_KEY'),
        'physician_review_threshold': float(os.environ.get('PHYSICIAN_REVIEW_THRESHOLD', '0.8')),
    }
```

## Testing Adapters

### Unit Testing

```python
import unittest
from adapters.healthcare_adapter import HealthcareAdapter

class TestHealthcareAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = HealthcareAdapter({
            'hipaa_compliance': True,
            'specialty': 'general'
        })
    
    def test_pii_sanitization(self):
        """Test PII removal"""
        input_text = "My SSN is 123-45-6789 and phone is 555-123-4567"
        sanitized = self.adapter._sanitize_pii(input_text)
        
        self.assertNotIn('123-45-6789', sanitized)
        self.assertNotIn('555-123-4567', sanitized)
        self.assertIn('[REDACTED]', sanitized)
    
    def test_medical_context_extraction(self):
        """Test medical context extraction"""
        input_text = "I have chest pain and difficulty breathing"
        context = self.adapter._extract_medical_context(input_text)
        
        self.assertEqual(context['urgency_level'], 'high')
        self.assertIn('chest pain', str(context['symptoms']))
    
    def test_physician_review_requirement(self):
        """Test physician review detection"""
        high_risk_context = {
            'symptoms': ['chest pain'],
            'urgency_level': 'high'
        }
        
        requires_review = self.adapter._requires_physician_review(high_risk_context)
        self.assertTrue(requires_review)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
import pytest
from universal_ai_sdk import UniversalAIClient, AgentConfig

@pytest.fixture
def healthcare_client():
    client = UniversalAIClient('http://localhost:8000')
    config = AgentConfig(
        instructions="You are a healthcare assistant",
        capabilities=["text"],
        business_logic_adapter="healthcare",
        custom_settings={
            'hipaa_compliance': True,
            'specialty': 'general'
        }
    )
    
    session = client.create_agent(config)
    yield session
    session.close()

def test_healthcare_conversation(healthcare_client):
    """Test healthcare adapter in conversation"""
    
    # Send medical query
    healthcare_client.send_message("I have a headache and fever")
    
    # Get response
    messages = healthcare_client.get_messages()
    last_response = messages[-1]['content']
    
    # Check for medical disclaimer
    assert "Medical Disclaimer" in last_response or "consult" in last_response.lower()
```

## Best Practices

### Design Principles

1. **Single Responsibility**: Each adapter should handle one domain
2. **Composability**: Adapters should work together when needed
3. **Configuration**: Make adapters highly configurable
4. **Error Handling**: Graceful fallbacks for adapter failures
5. **Performance**: Minimize latency in input/output processing

### Security Considerations

1. **Input Validation**: Always validate and sanitize user input
2. **Output Filtering**: Review and filter agent responses
3. **Data Privacy**: Respect privacy regulations (GDPR, HIPAA, etc.)
4. **Access Control**: Implement proper authorization
5. **Audit Logging**: Log all adapter decisions and actions

### Performance Optimization

1. **Caching**: Cache expensive operations (API calls, NLP processing)
2. **Async Operations**: Use async/await for I/O operations
3. **Resource Management**: Properly manage connections and resources
4. **Monitoring**: Track adapter performance and errors

---

**Next**: Learn about [Deployment](/docs/guides/deployment) or explore the [SDK Documentation](/docs/sdks) for implementation details.