# Universal AI Agent Platform

A complete SaaS platform that enables businesses to integrate multimodal AI agents into their applications without building AI infrastructure themselves.

## 🏗️ Architecture Overview

- **Agent Platform**: Core multimodal AI service built on LiveKit foundation
- **API Gateway**: REST API for seamless client integration  
- **Business Logic Adapters**: Pluggable framework for customizing agent behavior
- **Usage Tracking & Billing**: Complete tracking system with multiple pricing plans
- **Client SDKs**: Full-featured Python and JavaScript SDKs
- **Demo Applications**: Working examples for language learning and emergency services

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install flask flask-cors python-dotenv

# For full functionality (optional)
pip install "livekit-agents[deepgram,openai,cartesia,silero,turn-detector]~=1.0"

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Test the platform
python test_core.py

# Start API Gateway
python api_gateway/main.py
```

## 📱 Demo Applications

### Language Learning Assistant
```bash
python demos/language_learning/app.py
```

### Emergency Services Dispatcher
```bash
python demos/emergency_services/app.py
```

## 🛠️ Client Integration

### Python SDK
```python
from universal_ai_sdk import create_simple_agent

# Create agent
session = create_simple_agent(
    instructions="You are a helpful assistant",
    capabilities=["text", "voice", "vision"]
)

# Send message and get response
session.send_message("Hello!")
response = session.wait_for_response()
print(response.content)
```

### JavaScript SDK
```javascript
const session = await UniversalAI.createSimpleAgent(
    "You are a helpful assistant",
    ["text", "voice", "vision"]
);

await session.sendMessage("Hello!");
const response = await session.waitForResponse();
console.log(response.content);
```

## 📚 Documentation

- **[API Reference](docs/api.md)**: Complete REST API documentation
- **[Business Logic Adapters](docs/adapters.md)**: Guide for customizing agent behavior  
- **[Client SDKs](docs/sdks.md)**: Python and JavaScript SDK documentation

## 🔧 Project Structure

```
universal-ai-platform/
├── agent_platform/          # Core AI agent service
├── api_gateway/             # REST API endpoints
├── adapters/                # Business logic customization
├── billing/                 # Usage tracking & billing
├── client_sdks/             # Python & JavaScript SDKs
├── demos/                   # Example applications
├── docs/                    # Complete documentation
└── requirements.txt         # Dependencies
```

## 🎯 Key Features

### Multimodal Capabilities
- **Voice**: Speech-to-text (Deepgram) and text-to-speech (Cartesia)
- **Vision**: Image analysis and OCR (OpenAI Vision)
- **Text**: Natural language conversation (OpenAI)
- **Real-time**: Live audio/video sessions (LiveKit)
- **Phone**: Voice calling integration (Twilio)

### Business Logic Adapters
- **Language Learning**: Optimized for educational applications with pronunciation feedback
- **Emergency Services**: Configured for emergency response scenarios with safety analysis
- **Custom Adapters**: Framework for building domain-specific logic

### Usage Tracking & Billing
- **Multiple Plans**: Starter, Professional, Enterprise
- **Real-time Tracking**: Sessions, messages, images, voice, real-time duration
- **Automated Billing**: Cost calculation based on multimodal usage

### Client SDKs
- **Python**: Full async support with high-level abstractions
- **JavaScript**: Browser and Node.js compatible
- **More Coming**: Java, C#, Go, Rust planned

## 🔒 Configuration

Set up your environment variables in `.env`:

```env
# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
CARTESIA_API_KEY=your_cartesia_api_key

# Phone Integration (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# LiveKit Configuration (for full functionality)
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

## 🧪 Testing

Run the test suite to verify platform functionality:

```bash
python test_core.py
```

## 🚀 Production Deployment

1. Set up environment variables
2. Configure LiveKit infrastructure
3. Deploy API Gateway
4. Set up monitoring and logging
5. Configure load balancing

## 📈 Scaling

The platform is designed for easy scaling:

- **Horizontal Scaling**: Multiple API Gateway instances
- **Database Scaling**: PostgreSQL for production
- **Agent Scaling**: LiveKit cluster deployment
- **Caching**: Redis for session management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is part of the Youtube_demos repository and follows the same licensing terms.

---

**Built with ❤️ using LiveKit, OpenAI, and modern web technologies**