# NexusAI Python SDK

The official Python SDK for NexusAI - The Universal AI Agent Platform for Africa. Build intelligent AI-powered applications with multimodal capabilities.

[![PyPI version](https://badge.fury.io/py/nexusai-sdk.svg)](https://badge.fury.io/py/nexusai-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

Install from PyPI using pip:

```bash
pip install nexusai-sdk
```

## Quick Start

### Simple Agent Creation

```python
from nexusai_sdk import NexusAIClient, AgentConfig

# Initialize the client
client = NexusAIClient('https://nexus.bits-innovate.com')

# Create an AI agent
config = AgentConfig(
    instructions="You are a helpful assistant for African businesses",
    capabilities=["text", "voice"]
)

agent = client.create_agent(config)
print(f"Agent created: {agent['session_id']}")

# Send a message
response = client.send_message(
    agent["session_id"],
    "Hello! Help me with my business plan."
)

print(response["message"])
```

### Business Logic Integration

```python
# Use with business domain adapters
config = AgentConfig(
    instructions="You are a language learning assistant for African students",
    capabilities=["text", "voice", "file"],
    domain="language_learning"
)

# Create a specialized agent
agent = client.create_agent(config)

# Process multimodal input
response = client.send_message(
    agent["session_id"],
    "Help me practice French pronunciation",
    file_path="/path/to/audio.mp3"
)
```

## API Reference

### NexusAIClient

Main client class for interacting with the NexusAI platform.

#### Constructor

```python
client = NexusAIClient(base_url="https://nexus.bits-innovate.com")
```

#### Methods

##### create_agent(config: AgentConfig) → dict

Creates a new AI agent session.

```python
config = AgentConfig(
    instructions="Your role instructions",
    capabilities=["text", "voice", "file"]
)
agent = client.create_agent(config)
```

##### send_message(session_id: str, message: str, file_path: str = None) → dict

Send a message to an agent session.

```python
response = client.send_message(
    session_id="your-session-id",
    message="Hello!",
    file_path="/path/to/file.jpg"  # Optional
)
```

##### get_messages(session_id: str) → list

Get all messages from a session.

```python
messages = client.get_messages("your-session-id")
```

##### health_check() → dict

Check platform health status.

```python
status = client.health_check()
```

### AgentConfig

Configuration class for creating agents.

```python
config = AgentConfig(
    instructions="Your instructions",
    capabilities=["text", "voice", "file"],  # Optional
    domain="business_logic"  # Optional
)
```

## Error Handling

The SDK includes comprehensive error handling:

```python
from nexusai_sdk import NexusAIClient, NexusAIError

try:
    client = NexusAIClient('https://nexus.bits-innovate.com')
    agent = client.create_agent(config)
except NexusAIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Custom Domain Adapters

```python
# Emergency services domain
config = AgentConfig(
    instructions="Emergency response coordinator for African communities",
    domain="emergency_services",
    capabilities=["text", "voice"]
)

emergency_agent = client.create_agent(config)
```

### File Processing

```python
# Send documents, images, or audio
response = client.send_message(
    agent["session_id"],
    "Analyze this document",
    file_path="/path/to/document.pdf"
)
```

## Examples

### Language Learning Assistant

```python
from nexusai_sdk import NexusAIClient, AgentConfig

client = NexusAIClient('https://nexus.bits-innovate.com')

# Create language learning agent
config = AgentConfig(
    instructions="Help African students learn local and international languages",
    domain="language_learning",
    capabilities=["text", "voice"]
)

agent = client.create_agent(config)

# Practice conversation
response = client.send_message(
    agent["session_id"],
    "I want to practice Swahili greetings"
)

print(response["message"])
```

### Business Assistant

```python
# Business logic domain
config = AgentConfig(
    instructions="Business advisor for African SMEs",
    domain="business_logic",
    capabilities=["text", "file"]
)

business_agent = client.create_agent(config)

# Analyze business plan
response = client.send_message(
    business_agent["session_id"],
    "Review my business plan",
    file_path="/path/to/business_plan.pdf"
)
```

## Support

- **Documentation**: [https://nexus.bits-innovate.com/docs](https://nexus.bits-innovate.com/docs)
- **PyPI Package**: [https://pypi.org/project/nexusai-sdk/](https://pypi.org/project/nexusai-sdk/)
- **Issues**: Report issues through our support channels

**Next**: Check out the [JavaScript SDK](javascript) or explore our [Getting Started Guide](../getting-started) for complete setup instructions.
