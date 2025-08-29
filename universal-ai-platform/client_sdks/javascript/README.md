# NexusAI JavaScript SDK

Official JavaScript SDK for **NexusAI** - The Universal AI Agent Platform designed for Africa.

[![npm version](https://badge.fury.io/js/nexusai-sdk.svg)](https://badge.fury.io/js/nexusai-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌍 About NexusAI

NexusAI is a comprehensive AI agent platform built specifically for the African market, offering:

- **🎯 Business Logic Adapters** - Language Learning, Emergency Services, and more
- **🎤 Multimodal Capabilities** - Voice, vision, and text interactions
- **📱 Mobile-First Design** - Optimized for African connectivity conditions
- **🔒 Enterprise Security** - SSL encryption and secure API endpoints

## 🚀 Quick Start

### Installation

```bash
npm install nexusai-sdk
```

### Basic Usage

```javascript
const { NexusAIClient } = require('nexusai-sdk');

// Initialize client with production endpoint
const client = new NexusAIClient('https://nexus.bits-innovate.com');

// Create an AI agent for language learning
const agent = await client.createAgent({
  instructions: "You are a friendly language tutor for African students learning English",
  capabilities: ["text", "voice"],
  business_logic_adapter: "languagelearning"
});

// Start a conversation session
const session = await client.createSession({
  agent_id: agent.id,
  client_id: "mobile-app-v1"
});

// Send a message
const response = await client.sendMessage(session.session_id, "Hello, help me learn English!");
console.log(response.message);
```

## 📚 Documentation

### Client Initialization

```javascript
// Production (Recommended)
const client = new NexusAIClient('https://nexus.bits-innovate.com', 'your-api-key');

// Local Development
const client = new NexusAIClient('http://localhost:8000');
```

### Agent Management

```javascript
// Create specialized agents
const languageAgent = await client.createAgent({
  instructions: "Expert English tutor for African students",
  capabilities: ["text", "voice"],
  business_logic_adapter: "languagelearning",
  custom_settings: {
    level: "beginner",
    focus: "conversation"
  }
});

const emergencyAgent = await client.createAgent({
  instructions: "Emergency response coordinator for urgent situations",
  capabilities: ["text", "voice"],
  business_logic_adapter: "emergencyservices",
  custom_settings: {
    region: "west-africa",
    languages: ["english", "french"]
  }
});
```

### Advanced Session Management

```javascript
// Create session
const session = await client.createSession({
  agent_id: agent.id,
  client_id: "mobile-app-user-123"
});

// Send messages
const response = await client.sendMessage(
  session.session_id, 
  "I need help with English pronunciation"
);

// Get conversation history
const messages = await client.getMessages(session.session_id, 10);
```

### Multimodal Features

```javascript
// Voice messages (for language learning)
const audioResponse = await client.sendVoiceMessage(
  session.session_id,
  audioBuffer
);

// Image analysis
const imageResponse = await client.sendImageMessage(
  session.session_id,
  imageBuffer
);
```

### Emergency Services Integration

```javascript
// Emergency agent with phone integration
const emergencyAgent = await client.createAgent({
  instructions: "Emergency response coordinator",
  capabilities: ["text", "voice"],
  business_logic_adapter: "emergencyservices"
});

// Emergency message triggers automatic escalation
const response = await client.sendMessage(
  emergencySession.session_id,
  "Medical emergency - need ambulance immediately!"
);
// Automatically triggers phone call to emergency services
```

## 🏗️ Advanced Usage

### Error Handling

```javascript
try {
  const response = await client.sendMessage(sessionId, message);
  console.log(response.message);
} catch (error) {
  if (error.message.includes('session not found')) {
    // Handle session expiry
    const newSession = await client.createSession(sessionConfig);
  } else if (error.message.includes('rate limit')) {
    // Handle rate limiting
    await delay(1000);
    // Retry request
  }
  console.error('Error:', error.message);
}
```

### Session Management

```javascript
// Using AgentSession class for easier management
const { AgentSession } = require('nexusai-sdk');

const session = new AgentSession(client, sessionId);
await session.sendMessage("Hello!");
await session.sendVoice(audioBuffer);
const history = await session.getHistory(20);
await session.close();
```

### Quick Setup Helper

```javascript
const { createSimpleAgent } = require('nexusai-sdk');

// Quick setup for prototyping
const { client, agent, session } = await createSimpleAgent(
  'https://nexus.bits-innovate.com',
  'You are a helpful AI assistant for African businesses',
  ['text', 'voice']
);

const response = await session.sendMessage("Help me with my business plan");
```

## 🌍 African Market Features

### Language Learning Adapter

- **Beginner/Intermediate/Advanced** levels
- **Pronunciation coaching** with voice feedback
- **Cultural context** for African English variants
- **Offline-capable** vocabulary building

### Emergency Services Adapter

- **Automatic phone integration** with Twilio
- **Geographic awareness** for African regions
- **Multi-language support** (English, French, Swahili, etc.)
- **Hospital/clinic database** integration

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Set default API endpoint
NEXUSAI_API_URL=https://nexus.bits-innovate.com

# Optional: Set API key for authenticated requests
NEXUSAI_API_KEY=your-api-key-here
```

### Custom Business Logic

```javascript
// Create custom adapter for your business
const customAgent = await client.createAgent({
  instructions: "Customer service agent for my e-commerce platform",
  capabilities: ["text", "voice"],
  business_logic_adapter: "custom",
  custom_settings: {
    company: "MyAfrican Business",
    products: ["electronics", "clothing"],
    languages: ["english", "swahili"]
  }
});
```

## 📱 Mobile Integration

Perfect for African mobile apps with:

- **Low bandwidth optimization**
- **Offline capability** for cached responses
- **Progressive enhancement** based on connection quality
- **SMS fallback** for emergency services

```javascript
// Mobile-optimized configuration
const mobileClient = new NexusAIClient('https://nexus.bits-innovate.com');

// Enable compression for slower connections
const response = await mobileClient.sendMessage(
  sessionId, 
  message,
  { compress: true, timeout: 30000 }
);
```

## 🔒 Security

- **HTTPS only** in production
- **API key authentication** for sensitive operations
- **Rate limiting** protection
- **Input validation** and sanitization

## 🤝 Support

- **Documentation**: [https://nexus.bits-innovate.com/docs](https://nexus.bits-innovate.com/docs)
- **GitHub Issues**: [https://github.com/cruso003/nexusai-javascript-sdk/issues](https://github.com/cruso003/nexusai-javascript-sdk/issues)
- **Email Support**: [hello@bits-innovate.com](mailto:hello@bits-innovate.com)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🌟 Contributing

We welcome contributions from the African developer community! Please read our contributing guidelines and submit pull requests.

---

**Built with ❤️ for Africa by [Bits Innovate](https://bits-innovate.com)**
