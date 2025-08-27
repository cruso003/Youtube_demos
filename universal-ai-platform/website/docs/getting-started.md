# Getting Started

Welcome to the Universal AI Agent Platform! This guide will help you get up and running with multimodal AI agents in minutes.

## What is the Universal AI Platform?

The Universal AI Agent Platform is a complete SaaS solution that enables businesses to integrate multimodal AI agents (voice, vision, text) into their applications without building AI infrastructure themselves.

### Key Benefits

- **🚀 Quick Integration**: Get started in minutes with our SDKs
- **🎯 Multimodal**: Voice, vision, and text processing in one platform
- **🔧 Customizable**: Business logic adapters for domain-specific behavior
- **📊 Enterprise Ready**: Usage tracking, billing, and scalable infrastructure
- **⚡ Developer Friendly**: Comprehensive SDKs and documentation

## Prerequisites

- **Python 3.8+** or **Node.js 16+** for SDK usage
- **API Key** (optional for development)
- Basic understanding of REST APIs

## Quick Setup

### Option 1: Automated Setup

The fastest way to get started is using our automated setup script:

```bash
# Clone the repository
git clone https://github.com/cruso003/Youtube_demos.git
cd Youtube_demos/universal-ai-platform

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
const { UniversalAIClient } = require('./client_sdks/javascript/universal-ai-sdk.js');

// Create client
const client = new UniversalAIClient('http://localhost:8000');

async function createFirstAgent() {
    // Create agent
    const result = await client.createAgent({
        instructions: "You are a helpful assistant",
        capabilities: ["text"]
    });
    
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
4. **[Examples](examples/language-learning)** - Working examples for different use cases
5. **[Deployment](guides/deployment)** - Production deployment guides

## Getting Help

- **Documentation**: Complete guides and API reference
- **Examples**: Working code samples in the `/demos` directory
- **GitHub**: [Report issues and contribute](https://github.com/cruso003/Youtube_demos/tree/main/universal-ai-platform)

## Common Issues

### Port Already in Use
If you get a "port already in use" error:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Missing Dependencies
If you get import errors:
```bash
pip install -r requirements.txt
```

### API Key Issues
- API keys are optional for development
- Check your `.env` file format
- Ensure no extra spaces in your keys

---

**Ready to build? Let's explore the [API Reference](api) or dive into some [Examples](/examples/language-learning)!**