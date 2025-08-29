# Getting Started with NexusAI

Welcome to **NexusAI** - The Universal AI Agent Platform built specifically for Africa! This guide will help you integrate intelligent AI agents into your applications in minutes.

## What is NexusAI?

Nex```python
from nexusai_sdk import NexusAIClient, AgentConfig

# Create multimodal agent
client = NexusAIClient('https://nexus.bits-innovate.com')
config = AgentConfig(
    instructions="You are a visual assistant",
    capabilities=["text", "vision", "voice"]
)

agent = client.create_agent(config)hensive AI platform that enables African businesses to deploy intelligent AI agents with voice, vision, and text capabilities. Built for the African market with local language support and optimized for mobile-first experiences.

### 🌍 Key Features

- **🎯 Multimodal AI**: Voice, vision, and text processing in one platform
- **🗣️ African Languages**: Native support for Swahili, Hausa, Yoruba, and more
- **📱 Mobile-First**: Optimized for African connectivity conditions
- **🏢 Business Adapters**: Pre-built solutions for language learning, emergency services
- **💳 Credit System**: Pay-as-you-use pricing with MTN Mobile Money support
- **🔒 Enterprise Security**: SSL encryption and secure API endpoints

## Quick Start

### 1. Get Your API Access

**Free Tier (No Signup):**
- 5 messages/day per IP
- Perfect for testing and development
- Access to all features with limits

**Sign up for more:** [https://nexus.bits-innovate.com/signup](https://nexus.bits-innovate.com/signup)

### 2. Install the SDK

Choose your preferred programming language:

```bash
# JavaScript/Node.js
npm install nexusai-sdk

# Python
pip install nexusai-sdk
```

### 3. Your First AI Agent

**JavaScript Example:**
```javascript
const { NexusAIClient } = require('nexusai-sdk');

const client = new NexusAIClient('https://nexus.bits-innovate.com');

// Create an AI agent
const agent = await client.createAgent({
  instructions: "You are a helpful assistant for African businesses",
  capabilities: ["text", "voice"],
  business_logic_adapter: "general"
});

// Send a message
const response = await client.sendMessage(
  agent.session_id,
  "Hello! Help me with my business plan."
);

console.log(response.message);
```

**Python Example:**
```python
from nexusai_sdk import NexusAIClient, AgentConfig

client = NexusAIClient('https://nexus.bits-innovate.com')

# Create an AI agent
config = AgentConfig(
    instructions="You are a helpful assistant for African businesses",
    capabilities=["text", "voice"],
    business_logic_adapter="general"
)

agent = client.create_agent(config)

# Send a message
response = client.send_message(
    agent["session_id"],
    "Hello! Help me with my business plan."
)

print(response["message"])
```

## Business Logic Adapters

NexusAI provides specialized adapters for African use cases:

### 🎓 Language Learning
Perfect for educational platforms teaching English, French, or local languages.

```javascript
const agent = await client.createAgent({
  instructions: "You are an English tutor for African students",
  business_logic_adapter: "languagelearning",
  custom_settings: {
    level: "beginner",
    native_language: "swahili"
  }
});
```

### 🚨 Emergency Services
Integrated with local emergency contacts and protocols.

```javascript
const agent = await client.createAgent({
  instructions: "You are an emergency response coordinator",
  business_logic_adapter: "emergencyservices",
  custom_settings: {
    region: "west-africa",
    emergency_contacts: {
      police: "+233-999",
      ambulance: "+233-777"
    }
  }
});
```

## API Endpoints

**Base URL:** `https://nexus.bits-innovate.com`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check API health |
| `/api/v1/agent/create` | POST | Create new agent |
| `/api/v1/agent/{id}/message` | POST | Send message |
| `/api/v1/agent/{id}/messages` | GET | Get message history |
| `/api/v1/usage/{client_id}` | GET | Check usage limits |

## Pricing & Credits

NexusAI uses a **credit-based system** - perfect for the African market:

- **Free Tier**: 5 messages/day (testing only)
- **1,000 Credits**: $1.00 USD (≈10,000 words)
- **10,000 Credits**: $9.00 USD (10% bonus)
- **100,000 Credits**: $80.00 USD (20% bonus)

### Payment Methods
- 💳 **MTN Mobile Money** (Liberia and expanding)
- 🏦 **Bank Cards** (Visa, Mastercard)
- 📱 **More mobile money networks** (coming soon)

## Next Steps

1. **[Try the SDKs](./sdks/)** - Detailed SDK documentation
2. **[API Reference](./api.md)** - Complete API documentation  
3. **[SDK Documentation](sdks)** - Official JavaScript and Python SDKs
4. **[Business Adapters](./guides/adapters.md)** - Specialized use cases

## Support

- 📧 **Email**: support@nexus.bits-innovate.com
- 💬 **Community**: Join our Discord server for discussions
- 📖 **Documentation**: [https://nexus.bits-innovate.com/docs](https://nexus.bits-innovate.com/docs)

---

*Built with ❤️ for Africa by [BITS (Building Innovative Technical Solutions)](https://bits-innovate.com)*

## Self-Hosting Setup

If you want to self-host the platform:

```bash
# Download the platform
wget https://github.com/bits-innovate/nexusai-platform/releases/latest/download/nexusai-platform.tar.gz
tar -xzf nexusai-platform.tar.gz
cd nexusai-platform

# Run automated setup
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

If you prefer manual setup or want to understand each step:

```bash
# Install dependencies
pip install flask flask-cors python-dotenv

# For full functionality (optional)
pip install "livekit-agents[deepgram,openai,cartesia,silero,turn-detector]~=1.0"

# Create environment file
cp .env.example .env
# Edit .env with your API keys (optional for development)

# Test the platform
python test_core.py

# Start API Gateway
python api_gateway/main.py
```

## API Key Setup (Optional)

While you can start developing without API keys, you'll need them for production use:

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`**:
   ```env
   # AI Service API Keys
   OPENAI_API_KEY=your_openai_api_key
   DEEPGRAM_API_KEY=your_deepgram_api_key
   CARTESIA_API_KEY=your_cartesia_api_key
   
   # LiveKit Configuration (for full functionality)
   LIVEKIT_URL=wss://your-livekit-server.com
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

3. **Where to get API keys**:
   - **OpenAI**: [OpenAI API Keys](https://platform.openai.com/api-keys)
   - **Deepgram**: [Deepgram Console](https://console.deepgram.com/)
   - **Cartesia**: [Cartesia Dashboard](https://play.cartesia.ai/)
   - **LiveKit**: [LiveKit Cloud](https://cloud.livekit.io/)

## Your First Agent

Let's create your first AI agent in just a few lines of code:

### Python Example

```python
from universal_ai_sdk import create_simple_agent

# Create a simple text agent
session = create_simple_agent(
    instructions="You are a helpful assistant",
    capabilities=["text"]
)

# Send a message
session.send_message("Hello! Can you help me?")

# Get the response
response = session.wait_for_response()
print(f"Agent: {response.content}")
```

### JavaScript Example

```javascript
import { NexusAIClient, AgentConfig } from 'nexusai-sdk';

// Create client
const client = new NexusAIClient('https://nexus.bits-innovate.com');

async function createFirstAgent() {
    // Create agent
    const config = new AgentConfig({
        instructions: "You are a helpful assistant",
        capabilities: ["text"]
    });
    
    const result = await client.createAgent(config);
    
    const sessionId = result.session_id;
    
    // Send message
    await client.sendMessage(sessionId, "Hello! Can you help me?");
    
    // Get response
    const messages = await client.getMessages(sessionId);
    const lastMessage = messages[messages.length - 1];
    console.log(`Agent: ${lastMessage.content}`);
}

createFirstAgent();
```

## Multimodal Agent Example

Here's how to create an agent with voice, vision, and text capabilities:

```python
from universal_ai_sdk import create_simple_agent

# Create multimodal agent
session = create_simple_agent(
    instructions="You are a vision-enabled assistant that can see and speak",
    capabilities=["text", "voice", "vision"]
)

# Send text message
session.send_message("What do you see in this image?")

# Send image (you can also use voice input)
session.send_image("path/to/image.jpg")

# Get response (can be text or voice)
response = session.wait_for_response()
print(f"Agent: {response.content}")
```

## Using Business Logic Adapters

Business logic adapters allow you to customize agent behavior for specific use cases:

```python
from universal_ai_sdk import create_simple_agent

# Create language learning agent
session = create_simple_agent(
    instructions="You are a Spanish tutor",
    capabilities=["text", "voice"],
    business_logic_adapter="languagelearning",
    custom_settings={
        "target_language": "Spanish",
        "proficiency_level": "beginner"
    }
)

session.send_message("Can you help me practice Spanish?")
response = session.wait_for_response()
print(f"Tutor: {response.content}")
```

## Testing Your Setup

Run the test suite to verify everything is working:

```bash
python test_core.py
```

You should see output like:
```
🚀 Universal AI Agent Platform - Core Test Suite
============================================================
🧪 Testing Usage Tracker... ✅
🧪 Testing Business Logic Adapters... ✅
🧪 Testing Python SDK... ✅
🧪 Testing JavaScript SDK... ✅
🧪 Testing Documentation... ✅
🧪 Testing Project Structure... ✅

🎉 All core tests passed!
```

## Starting the API Gateway

To start the REST API server:

```bash
python api_gateway/main.py
```

The API will be available at `http://localhost:8000/api/v1`

## Next Steps

Now that you have the platform running, explore these topics:

1. **[API Reference](api)** - Complete REST API documentation
2. **[SDK Documentation](sdks/python)** - Python and JavaScript SDK guides
3. **[Business Logic Adapters](guides/adapters)** - Customize agent behavior
4. **[Deployment Guide](guides/deployment)** - Production deployment options
5. **[Deployment](guides/deployment)** - Production deployment guides

## Getting Help

- **Documentation**: Complete guides and API reference
- **Examples**: Working code samples in the language learning guide
- **Support**: Contact us through our official channels

## Common Issues

### Connection Issues

If you can't connect to the platform:

```bash
# Check if the service is running
curl https://nexus.bits-innovate.com/health
```

### SDK Installation

```bash
# For Python
pip install --upgrade nexusai-sdk

# For JavaScript
npm install nexusai-sdk@latest
```

### API Key Issues

- API keys are optional for basic usage
- Contact support for premium features

---

**Ready to build? Let's explore the [API Reference](api) or check out the [SDK Documentation](sdks)!**