# Python SDK

The Python SDK provides a high-level interface for integrating AI agents into your Python applications with full async support and comprehensive error handling.

## Installation

### From Source
```bash
# Clone the repository
git clone https://github.com/cruso003/Youtube_demos.git
cd Youtube_demos/universal-ai-platform

# Install the SDK
pip install -e ./client_sdks/python/
```

### Direct Usage
```bash
# Copy the SDK file to your project
cp client_sdks/python/universal_ai_sdk.py your_project/
```

## Quick Start

### Simple Agent Creation

```python
from universal_ai_sdk import create_simple_agent

# Create a basic text agent
session = create_simple_agent(
    instructions="You are a helpful assistant",
    capabilities=["text"]
)

# Send message and get response
session.send_message("Hello!")
response = session.wait_for_response()
print(f"Agent: {response.content}")
```

### Advanced Configuration

```python
from universal_ai_sdk import UniversalAIClient, AgentConfig

# Create client with custom configuration
client = UniversalAIClient(
    base_url="http://localhost:8000",
    api_key="your_api_key"  # Optional
)

# Create agent with custom settings
config = AgentConfig(
    instructions="You are a language learning assistant",
    capabilities=["text", "voice", "vision"],
    business_logic_adapter="languagelearning",
    custom_settings={
        "target_language": "French",
        "proficiency_level": "intermediate",
        "conversation_topics": ["travel", "culture", "food"]
    },
    client_id="language_app_user_123"
)

session = client.create_agent(config)
```

## Core Classes

### UniversalAIClient

The main client class for API communication.

```python
class UniversalAIClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        """
        Initialize the Universal AI client.
        
        Args:
            base_url: API gateway URL
            api_key: Optional API key for authentication
        """
```

**Methods**:

#### create_agent(config: AgentConfig) → AgentSession
```python
# Create a new agent session
session = client.create_agent(config)
```

#### get_usage_summary(client_id: str, start_date: str = None, end_date: str = None) → dict
```python
# Get usage statistics
usage = client.get_usage_summary("user_123", "2024-01-01", "2024-01-31")
```

#### calculate_bill(client_id: str, plan: str = "professional") → dict
```python
# Calculate billing information
bill = client.calculate_bill("user_123", plan="professional")
```

### AgentSession

Represents an active agent session with communication methods.

```python
class AgentSession:
    def __init__(self, session_id: str, client: UniversalAIClient):
        """
        Agent session for communication.
        
        Args:
            session_id: Unique session identifier
            client: UniversalAI client instance
        """
```

**Methods**:

#### send_message(message: str) → bool
```python
# Send text message
success = session.send_message("How can you help me?")
```

#### send_image(image_path: str, message: str = None) → bool
```python
# Send image with optional text
success = session.send_image("photo.jpg", "What do you see?")
```

#### wait_for_response(timeout: int = 30) → AgentResponse
```python
# Wait for agent response
response = session.wait_for_response(timeout=60)
print(response.content)
```

#### get_messages() → List[dict]
```python
# Get all session messages
messages = session.get_messages()
for msg in messages:
    print(f"{msg['type']}: {msg['content']}")
```

#### close() → bool
```python
# Close the session
session.close()
```

### AgentConfig

Configuration object for agent creation.

```python
class AgentConfig:
    def __init__(
        self,
        instructions: str,
        capabilities: List[str],
        business_logic_adapter: str = None,
        custom_settings: dict = None,
        client_id: str = None
    ):
        """
        Agent configuration.
        
        Args:
            instructions: System instructions for the agent
            capabilities: List of capabilities ["text", "voice", "vision"]
            business_logic_adapter: Optional adapter name
            custom_settings: Adapter-specific settings
            client_id: Client identifier for usage tracking
        """
```

### AgentResponse

Response object from agent interactions.

```python
class AgentResponse:
    def __init__(self, content: str, message_type: str, timestamp: str):
        """
        Agent response data.
        
        Attributes:
            content: Response text content
            message_type: Type of message ("text", "voice", "image")
            timestamp: Response timestamp
        """
```

## Usage Examples

### Multimodal Agent

```python
from universal_ai_sdk import create_simple_agent

# Create agent with all capabilities
session = create_simple_agent(
    instructions="You are a vision-enabled assistant that can see and speak",
    capabilities=["text", "voice", "vision"]
)

# Send text message
session.send_message("Hello! I have an image to show you.")

# Send image for analysis
session.send_image("vacation_photo.jpg", "Can you describe this vacation photo?")

# Get the response
response = session.wait_for_response()
print(f"Agent: {response.content}")

# Close session when done
session.close()
```

### Language Learning Application

```python
from universal_ai_sdk import UniversalAIClient, AgentConfig

def create_language_tutor(user_id: str, target_language: str, level: str):
    client = UniversalAIClient()
    
    config = AgentConfig(
        instructions=f"You are a {target_language} tutor. Help the user practice conversation.",
        capabilities=["text", "voice"],
        business_logic_adapter="languagelearning",
        custom_settings={
            "target_language": target_language,
            "proficiency_level": level,
            "conversation_topics": ["daily activities", "travel", "food"]
        },
        client_id=user_id
    )
    
    return client.create_agent(config)

# Usage
session = create_language_tutor("user_123", "Spanish", "beginner")
session.send_message("Hola! ¿Cómo estás?")
response = session.wait_for_response()
print(f"Tutor: {response.content}")
```

### Emergency Services Integration

```python
from universal_ai_sdk import UniversalAIClient, AgentConfig

def create_emergency_dispatcher():
    client = UniversalAIClient()
    
    config = AgentConfig(
        instructions="You are an emergency services dispatcher. Gather information and determine emergency type.",
        capabilities=["text", "voice"],
        business_logic_adapter="emergencyservices",
        custom_settings={
            "emergency_types": ["medical", "fire", "police", "natural_disaster"],
            "location_required": True,
            "escalation_keywords": ["unconscious", "bleeding", "fire", "chest_pain"]
        }
    )
    
    return client.create_agent(config)

# Usage
dispatcher = create_emergency_dispatcher()
dispatcher.send_message("I need help! There's been an accident!")
response = dispatcher.wait_for_response()
print(f"Dispatcher: {response.content}")
```

### Batch Processing

```python
from universal_ai_sdk import UniversalAIClient, AgentConfig
import asyncio

async def process_multiple_requests():
    client = UniversalAIClient()
    
    # Create multiple agents for parallel processing
    sessions = []
    for i in range(5):
        config = AgentConfig(
            instructions="You are a helpful assistant",
            capabilities=["text"],
            client_id=f"batch_user_{i}"
        )
        session = client.create_agent(config)
        sessions.append(session)
    
    # Send messages to all agents
    tasks = []
    for i, session in enumerate(sessions):
        session.send_message(f"Process request {i}")
        tasks.append(session.wait_for_response())
    
    # Wait for all responses
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses):
        print(f"Agent {i}: {response.content}")
    
    # Clean up
    for session in sessions:
        session.close()

# Run batch processing
asyncio.run(process_multiple_requests())
```

## Error Handling

### Exception Types

```python
from universal_ai_sdk import (
    UniversalAIError,
    AuthenticationError,
    SessionNotFoundError,
    RateLimitError,
    ValidationError
)

try:
    session = create_simple_agent(
        instructions="Test agent",
        capabilities=["invalid_capability"]  # This will fail
    )
except ValidationError as e:
    print(f"Validation error: {e.message}")
except UniversalAIError as e:
    print(f"General error: {e.message}")
```

### Robust Error Handling

```python
import time
from universal_ai_sdk import create_simple_agent, RateLimitError

def send_message_with_retry(session, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            session.send_message(message)
            return session.wait_for_response()
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise

# Usage
session = create_simple_agent(
    instructions="You are a helpful assistant",
    capabilities=["text"]
)

response = send_message_with_retry(session, "Hello!")
print(f"Agent: {response.content}")
```

## Advanced Features

### Custom Request Handlers

```python
from universal_ai_sdk import UniversalAIClient

class CustomClient(UniversalAIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_count = 0
    
    def _make_request(self, method, endpoint, **kwargs):
        self.request_count += 1
        print(f"Making request #{self.request_count}: {method} {endpoint}")
        return super()._make_request(method, endpoint, **kwargs)

# Usage
client = CustomClient()
```

### Session Persistence

```python
import json
from universal_ai_sdk import UniversalAIClient, AgentConfig

def save_session(session, filename):
    """Save session state to file"""
    session_data = {
        "session_id": session.session_id,
        "config": session.config.__dict__,
        "messages": session.get_messages()
    }
    with open(filename, 'w') as f:
        json.dump(session_data, f)

def load_session(filename, client):
    """Load session state from file"""
    with open(filename, 'r') as f:
        session_data = json.load(f)
    
    # Recreate session (note: this creates a new session)
    config = AgentConfig(**session_data["config"])
    return client.create_agent(config)

# Usage
client = UniversalAIClient()
session = client.create_agent(AgentConfig(
    instructions="You are a helpful assistant",
    capabilities=["text"]
))

# Save session
save_session(session, "my_session.json")

# Load session later
restored_session = load_session("my_session.json", client)
```

## Configuration

### Environment Variables

The SDK respects these environment variables:

```bash
# API Configuration
UNIVERSAL_AI_BASE_URL=http://localhost:8000
UNIVERSAL_AI_API_KEY=your_api_key

# Request Configuration
UNIVERSAL_AI_TIMEOUT=30
UNIVERSAL_AI_MAX_RETRIES=3

# Development
UNIVERSAL_AI_DEBUG=true
```

### Client Configuration

```python
from universal_ai_sdk import UniversalAIClient

# Configure with custom settings
client = UniversalAIClient(
    base_url="https://your-api.com",
    api_key="your_key",
    timeout=60,
    max_retries=5,
    debug=True
)
```

## Testing

### Unit Testing with Mock

```python
import unittest
from unittest.mock import patch, MagicMock
from universal_ai_sdk import create_simple_agent

class TestUniversalAI(unittest.TestCase):
    
    @patch('universal_ai_sdk.UniversalAIClient')
    def test_create_agent(self, mock_client):
        # Mock the client
        mock_session = MagicMock()
        mock_client.return_value.create_agent.return_value = mock_session
        
        # Test agent creation
        session = create_simple_agent(
            instructions="Test agent",
            capabilities=["text"]
        )
        
        # Verify the session was created
        self.assertIsNotNone(session)
        mock_client.return_value.create_agent.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
import pytest
from universal_ai_sdk import create_simple_agent

@pytest.fixture
def test_session():
    session = create_simple_agent(
        instructions="You are a test assistant",
        capabilities=["text"]
    )
    yield session
    session.close()

def test_basic_conversation(test_session):
    # Send message
    success = test_session.send_message("Hello!")
    assert success
    
    # Get response
    response = test_session.wait_for_response()
    assert response.content
    assert len(response.content) > 0

def test_message_history(test_session):
    # Send multiple messages
    test_session.send_message("First message")
    test_session.wait_for_response()
    
    test_session.send_message("Second message")
    test_session.wait_for_response()
    
    # Check message history
    messages = test_session.get_messages()
    assert len(messages) >= 4  # 2 user + 2 agent messages
```

## Best Practices

### Resource Management

```python
from contextlib import contextmanager
from universal_ai_sdk import UniversalAIClient, AgentConfig

@contextmanager
def ai_session(instructions, capabilities):
    """Context manager for automatic session cleanup"""
    client = UniversalAIClient()
    config = AgentConfig(instructions=instructions, capabilities=capabilities)
    session = client.create_agent(config)
    
    try:
        yield session
    finally:
        session.close()

# Usage
with ai_session("You are a helpful assistant", ["text"]) as session:
    session.send_message("Hello!")
    response = session.wait_for_response()
    print(response.content)
# Session automatically closed
```

### Connection Pooling

```python
from universal_ai_sdk import UniversalAIClient
import threading

class AIClientPool:
    def __init__(self, pool_size=5):
        self.pool = [UniversalAIClient() for _ in range(pool_size)]
        self.lock = threading.Lock()
        self.index = 0
    
    def get_client(self):
        with self.lock:
            client = self.pool[self.index]
            self.index = (self.index + 1) % len(self.pool)
            return client

# Usage
pool = AIClientPool()
client = pool.get_client()
```

---

**Next**: Check out the [JavaScript SDK](sdks/javascript) or explore [Examples](/examples/language-learning) for complete applications.