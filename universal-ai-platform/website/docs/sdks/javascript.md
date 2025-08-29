# NexusAI JavaScript SDK

The official JavaScript SDK for NexusAI - The Universal AI Agent Platform for Africa. Build intelligent AI-powered applications with multimodal capabilities for both browser and Node.js environments.

[![npm version](https://badge.fury.io/js/nexusai-sdk.svg)](https://badge.fury.io/js/nexusai-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

### npm

```bash
npm install nexusai-sdk
```

### yarn

```bash
yarn add nexusai-sdk
```

### CDN (Browser)

```html
<script src="https://unpkg.com/nexusai-sdk@latest/dist/nexusai-sdk.min.js"></script>
```

## Quick Start

### Node.js/ES6 Modules

```javascript
import { NexusAIClient, AgentConfig } from 'nexusai-sdk';

// Initialize the client
const client = new NexusAIClient('https://nexus.bits-innovate.com');

// Create an AI agent
const config = new AgentConfig({
    instructions: "You are a helpful assistant for African businesses",
    capabilities: ["text", "voice"]
});

async function quickStart() {
    try {
        const agent = await client.createAgent(config);
        console.log(`Agent created: ${agent.session_id}`);
        
        // Send a message
        const response = await client.sendMessage(
            agent.session_id,
            "Hello! Help me with my business plan."
        );
        
        console.log(response.message);
    } catch (error) {
        console.error('Error:', error);
    }
}

quickStart();
```

### Browser

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/nexusai-sdk@latest/dist/nexusai-sdk.min.js"></script>
</head>
<body>
    <script>
        const client = new NexusAI.Client('https://nexus.bits-innovate.com');
        
        async function createAgent() {
            const config = {
                instructions: "You are a helpful assistant",
                capabilities: ["text"]
            };
            
            const agent = await client.createAgent(config);
            const response = await client.sendMessage(
                agent.session_id,
                "Hello from the browser!"
            );
            
            document.body.innerHTML = `<p>Agent: ${response.message}</p>`;
        }
        
        createAgent();
    </script>
</body>
</html>
```

## API Reference

### NexusAIClient

Main client class for interacting with the NexusAI platform.

#### Constructor

```javascript
const client = new NexusAIClient(baseUrl);
```

**Parameters:**
- `baseUrl` (string): The API endpoint URL (default: 'https://nexus.bits-innovate.com')

#### Methods

##### createAgent(config) → Promise&lt;Object&gt;

Creates a new AI agent session.

```javascript
const config = new AgentConfig({
    instructions: "Your role instructions",
    capabilities: ["text", "voice", "file"]
});

const agent = await client.createAgent(config);
```

##### sendMessage(sessionId, message, filePath?) → Promise&lt;Object&gt;

Send a message to an agent session.

```javascript
const response = await client.sendMessage(
    "your-session-id",
    "Hello!",
    "/path/to/file.jpg"  // Optional
);
```

##### getMessages(sessionId) → Promise&lt;Array&gt;

Get all messages from a session.

```javascript
const messages = await client.getMessages("your-session-id");
```

##### healthCheck() → Promise&lt;Object&gt;

Check platform health status.

```javascript
const status = await client.healthCheck();
```

### AgentConfig

Configuration class for creating agents.

```javascript
const config = new AgentConfig({
    instructions: "Your instructions",
    capabilities: ["text", "voice", "file"],  // Optional
    domain: "business_logic"  // Optional
});
```

## Error Handling

The SDK includes comprehensive error handling:

```javascript
import { NexusAIClient, NexusAIError } from 'nexusai-sdk';

try {
    const client = new NexusAIClient('https://nexus.bits-innovate.com');
    const agent = await client.createAgent(config);
} catch (error) {
    if (error instanceof NexusAIError) {
        console.error('API Error:', error.message);
    } else {
        console.error('Unexpected error:', error);
    }
}
```

## Advanced Usage

### File Upload

```javascript
// Browser file upload
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

const response = await client.sendMessage(
    sessionId,
    "Analyze this document",
    file
);
```

### Streaming Responses

```javascript
// Listen for streaming responses
client.onMessage(sessionId, (message) => {
    console.log('New message:', message);
});

await client.sendMessage(sessionId, "Tell me a long story");
```

### Custom Domain Adapters

```javascript
// Emergency services domain
const config = new AgentConfig({
    instructions: "Emergency response coordinator for African communities",
    domain: "emergency_services",
    capabilities: ["text", "voice"]
});

const emergencyAgent = await client.createAgent(config);
```

## Examples

### Language Learning Assistant

```javascript
import { NexusAIClient, AgentConfig } from 'nexusai-sdk';

class LanguageLearningApp {
    constructor() {
        this.client = new NexusAIClient('https://nexus.bits-innovate.com');
        this.agent = null;
    }
    
    async initializeTutor(language, level) {
        const config = new AgentConfig({
            instructions: `Help African students learn ${language}`,
            domain: "language_learning",
            capabilities: ["text", "voice"]
        });
        
        this.agent = await this.client.createAgent(config);
        return this.agent.session_id;
    }
    
    async practiceConversation(message) {
        const response = await this.client.sendMessage(
            this.agent.session_id,
            message
        );
        return response.message;
    }
}

// Usage
const app = new LanguageLearningApp();
await app.initializeTutor("Swahili", "beginner");
const response = await app.practiceConversation("Jambo! Habari za asubuhi?");
console.log("Tutor:", response);
```

### Business Assistant

```javascript
import { NexusAIClient, AgentConfig } from 'nexusai-sdk';

class BusinessAssistant {
    constructor() {
        this.client = new NexusAIClient('https://nexus.bits-innovate.com');
    }
    
    async createBusinessAdvisor() {
        const config = new AgentConfig({
            instructions: "Business advisor for African SMEs",
            domain: "business_logic",
            capabilities: ["text", "file"]
        });
        
        return await this.client.createAgent(config);
    }
    
    async analyzeBusinessPlan(sessionId, planFile) {
        return await this.client.sendMessage(
            sessionId,
            "Please review my business plan and provide feedback",
            planFile
        );
    }
}

// Usage
const assistant = new BusinessAssistant();
const advisor = await assistant.createBusinessAdvisor();
const analysis = await assistant.analyzeBusinessPlan(
    advisor.session_id,
    businessPlanFile
);
```

### React Integration

```jsx
import React, { useState, useEffect } from 'react';
import { NexusAIClient, AgentConfig } from 'nexusai-sdk';

function ChatComponent() {
    const [client] = useState(() => new NexusAIClient('https://nexus.bits-innovate.com'));
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    
    useEffect(() => {
        initializeAgent();
    }, []);
    
    const initializeAgent = async () => {
        const config = new AgentConfig({
            instructions: "You are a helpful assistant",
            capabilities: ["text"]
        });
        
        const agent = await client.createAgent(config);
        setSessionId(agent.session_id);
    };
    
    const sendMessage = async () => {
        if (!input.trim() || !sessionId) return;
        
        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        
        const response = await client.sendMessage(sessionId, input);
        const agentMessage = { role: 'agent', content: response.message };
        setMessages(prev => [...prev, agentMessage]);
        
        setInput('');
    };
    
    return (
        <div>
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        <strong>{msg.role}:</strong> {msg.content}
                    </div>
                ))}
            </div>
            <div>
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type your message..."
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}

export default ChatComponent;
```

## TypeScript Support

The SDK includes TypeScript definitions:

```typescript
import { NexusAIClient, AgentConfig, AgentResponse } from 'nexusai-sdk';

interface BusinessConfig {
    industry: string;
    size: 'small' | 'medium' | 'large';
    location: string;
}

class TypedBusinessAssistant {
    private client: NexusAIClient;
    
    constructor(baseUrl: string) {
        this.client = new NexusAIClient(baseUrl);
    }
    
    async createAgent(businessConfig: BusinessConfig): Promise<string> {
        const config = new AgentConfig({
            instructions: `Business advisor for ${businessConfig.industry} businesses`,
            domain: "business_logic",
            capabilities: ["text", "file"]
        });
        
        const agent = await this.client.createAgent(config);
        return agent.session_id;
    }
    
    async getAdvice(sessionId: string, query: string): Promise<AgentResponse> {
        return await this.client.sendMessage(sessionId, query);
    }
}
```

## Configuration Options

### Environment Variables

```javascript
// Configure using environment variables
const client = new NexusAIClient(
    process.env.NEXUS_AI_BASE_URL || 'https://nexus.bits-innovate.com'
);
```

### Custom Configuration

```javascript
const client = new NexusAIClient('https://nexus.bits-innovate.com', {
    timeout: 30000,
    retries: 3,
    apiKey: 'your-api-key'  // If required
});
```

## Browser Compatibility

The SDK supports:
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

For older browsers, use the polyfilled version:

```html
<script src="https://unpkg.com/nexusai-sdk@latest/dist/nexusai-sdk.polyfill.min.js"></script>
```

## Support

- **Documentation**: [https://nexus.bits-innovate.com/docs](https://nexus.bits-innovate.com/docs)
- **npm Package**: [https://www.npmjs.com/package/nexusai-sdk](https://www.npmjs.com/package/nexusai-sdk)
- **Issues**: Report issues through our support channels

**Next**: Check out the [Python SDK](python) or explore our [Getting Started Guide](../getting-started) for complete setup instructions.
