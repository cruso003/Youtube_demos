# Business Logic Adapters Guide

## Overview

Business Logic Adapters allow you to customize the behavior of AI agents for specific use cases without modifying the core platform. They provide hooks for processing user input, handling agent responses, and implementing domain-specific logic.

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
```

## Creating Custom Adapters

### Step 1: Extend the Base Class

Create a new adapter by extending `BusinessLogicAdapter`:

```python
from adapters.business_logic_adapter import BusinessLogicAdapter
from typing import Any, Dict, List, Optional
from livekit.agents import ChatContext
from livekit import rtc

class MyCustomAdapter(BusinessLogicAdapter):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Initialize your custom settings
        self.my_setting = config.get("my_setting", "default_value") if config else "default_value"
```

### Step 2: Implement Required Methods

```python
async def on_agent_enter(self, agent, room: rtc.Room):
    """Called when agent enters a room"""
    # Initialize your custom logic
    print(f"Custom adapter initialized for agent {agent.config.agent_id}")
    
    # Modify agent instructions if needed
    agent.instructions = f"Custom instructions: {agent.instructions}"

async def process_image(self, image_bytes: bytes, chat_ctx: ChatContext) -> Optional[List[Any]]:
    """Process uploaded images"""
    # Return None for default processing, or custom content list
    if self.should_process_image(image_bytes):
        return ["Custom image processing result"]
    return None  # Use default processing

async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: dict):
    """Called when user completes a turn"""
    # Add custom metadata or modify the message
    content = new_message.get('content', '')
    new_message['content'] = f"[CUSTOM CONTEXT] {content}"

async def process_text_input(self, text: str, chat_ctx: ChatContext) -> Optional[str]:
    """Process text input before sending to agent"""
    # Return modified text or None for default processing
    if self.should_modify_text(text):
        return f"Modified: {text}"
    return None
```

### Step 3: Add Helper Methods

```python
def should_process_image(self, image_bytes: bytes) -> bool:
    """Custom logic to decide if image needs special processing"""
    return len(image_bytes) > 1024  # Example condition

def should_modify_text(self, text: str) -> bool:
    """Custom logic to decide if text needs modification"""
    return "urgent" in text.lower()  # Example condition
```

## Built-in Adapters

### Language Learning Adapter

Optimized for language learning applications with features like:

- Target language detection
- Proficiency level adjustment
- Gentle error correction
- Conversation topic guidance

**Configuration:**
```python
config = {
    "target_language": "Spanish",
    "proficiency_level": "beginner",
    "conversation_topics": ["daily activities", "food", "travel"]
}
```

**Usage:**
```python
agent_config = AgentConfig(
    instructions="You are a language learning assistant",
    capabilities=["text", "voice"],
    business_logic_adapter="languagelearning",
    custom_settings=config
)
```

### Emergency Services Adapter

Designed for emergency response scenarios with:

- Priority escalation detection
- Location information extraction
- Emergency type classification
- Call logging and tracking

**Configuration:**
```python
config = {
    "emergency_types": ["medical", "fire", "police", "natural_disaster"],
    "location_required": True,
    "escalation_keywords": ["unconscious", "bleeding", "fire"]
}
```

## Adapter Registration

### Automatic Registration

Place your adapter file in the `adapters/` directory with the naming convention:
- File: `adapters/mycustom.py`
- Class: `MycustomAdapter`

The platform will automatically discover and load your adapter when referenced by name:

```python
business_logic_adapter="mycustom"
```

### Manual Registration

For more complex scenarios, you can register adapters programmatically:

```python
from adapters.business_logic_adapter import BusinessLogicAdapter

class MyAdapter(BusinessLogicAdapter):
    # ... implementation

# Register the adapter
BusinessLogicAdapter.register("myname", MyAdapter)
```

## Configuration Options

Adapters receive configuration through the `custom_settings` parameter:

```python
agent_config = AgentConfig(
    business_logic_adapter="mycustom",
    custom_settings={
        "api_endpoint": "https://api.example.com",
        "timeout": 30,
        "retry_count": 3,
        "custom_prompts": {
            "greeting": "Welcome to our service!",
            "error": "I apologize for the confusion."
        }
    }
)
```

## Best Practices

### 1. Error Handling

Always include proper error handling in your adapters:

```python
async def process_image(self, image_bytes: bytes, chat_ctx: ChatContext):
    try:
        # Your processing logic
        result = await self.analyze_image(image_bytes)
        return ["Analysis result: " + result]
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        return None  # Fall back to default processing
```

### 2. Performance Considerations

- Keep processing lightweight to avoid blocking the agent
- Use async/await for I/O operations
- Cache frequently used data

```python
class MyAdapter(BusinessLogicAdapter):
    def __init__(self, config):
        super().__init__(config)
        self._cache = {}
    
    async def process_text_input(self, text: str, chat_ctx: ChatContext):
        # Check cache first
        if text in self._cache:
            return self._cache[text]
        
        # Process and cache result
        result = await self.expensive_processing(text)
        self._cache[text] = result
        return result
```

### 3. Logging and Monitoring

Include comprehensive logging for debugging and monitoring:

```python
import logging

logger = logging.getLogger(__name__)

class MyAdapter(BusinessLogicAdapter):
    async def on_agent_enter(self, agent, room):
        logger.info(f"Adapter activated for agent {agent.config.agent_id} in room {room.name}")
        
        # Log configuration
        logger.debug(f"Adapter config: {self.config}")
```

### 4. Testing

Create unit tests for your adapters:

```python
import pytest
from adapters.mycustom import MycustomAdapter

@pytest.mark.asyncio
async def test_text_processing():
    adapter = MycustomAdapter({"setting": "test_value"})
    
    result = await adapter.process_text_input("test input", None)
    assert result == "expected output"
```

## Advanced Features

### State Management

Maintain state across adapter calls:

```python
class StatefulAdapter(BusinessLogicAdapter):
    def __init__(self, config):
        super().__init__(config)
        self.conversation_state = {
            "topic": None,
            "step": 0,
            "user_responses": []
        }
    
    async def process_text_input(self, text: str, chat_ctx: ChatContext):
        # Update state based on user input
        self.conversation_state["user_responses"].append(text)
        
        # Modify input based on current state
        if self.conversation_state["step"] == 0:
            return f"Step 1: {text}"
        else:
            return f"Step {self.conversation_state['step']}: {text}"
```

### External API Integration

Integrate with external services:

```python
import aiohttp

class APIIntegrationAdapter(BusinessLogicAdapter):
    async def process_text_input(self, text: str, chat_ctx: ChatContext):
        # Call external API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config["api_endpoint"],
                json={"text": text}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("processed_text", text)
        
        return None  # Fall back to original text
```

### Multi-Modal Processing

Handle different input types:

```python
class MultiModalAdapter(BusinessLogicAdapter):
    async def process_image(self, image_bytes: bytes, chat_ctx: ChatContext):
        # Analyze image content
        analysis = await self.analyze_image(image_bytes)
        
        return [
            f"I can see: {analysis['description']}",
            ImageContent(image=f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}")
        ]
    
    async def process_text_input(self, text: str, chat_ctx: ChatContext):
        # Check if text references recent image
        if "image" in text.lower() and self.has_recent_image(chat_ctx):
            return f"Regarding the image you shared: {text}"
        
        return None
```

## Troubleshooting

### Common Issues

1. **Adapter Not Found**
   - Check file naming convention
   - Ensure class name matches expected pattern
   - Verify adapter is in the correct directory

2. **Import Errors**
   - Check Python path configuration
   - Ensure all dependencies are installed
   - Verify package structure with `__init__.py` files

3. **Performance Issues**
   - Profile your adapter methods
   - Check for blocking operations
   - Monitor memory usage

### Debugging

Enable debug logging to troubleshoot adapter issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your adapter will now log debug information
```

## Examples Repository

Find more adapter examples in the `examples/adapters/` directory:

- `healthcare_adapter.py` - Medical consultation assistant
- `education_adapter.py` - Interactive learning assistant
- `customer_service_adapter.py` - Support ticket handling
- `creative_writing_adapter.py` - Writing assistance and feedback