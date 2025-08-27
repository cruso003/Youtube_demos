# Client SDKs Documentation

## Overview

The Universal AI Agent Platform provides client SDKs in multiple programming languages to facilitate easy integration with your applications. The SDKs handle API communication, session management, and provide convenient high-level interfaces.

## Available SDKs

- **Python SDK**: Full-featured SDK with async support
- **JavaScript SDK**: Browser and Node.js compatible
- **More SDKs**: Additional languages planned (Java, C#, Go, Rust)

## Python SDK

### Installation

```bash
pip install requests  # Required dependency
```

### Quick Start

```python
from universal_ai_sdk import UniversalAIClient, AgentConfig

# Initialize client
client = UniversalAIClient("http://localhost:8000")

# Create agent
config = AgentConfig(
    instructions="You are a helpful assistant",
    capabilities=["text", "voice"]
)

result = client.create_agent(config)
session_id = result["session_id"]

# Send message
client.send_message(session_id, "Hello!")

# Get response
messages = client.get_messages(session_id)
print(messages[-1].content)
```

### High-Level Session API

```python
from universal_ai_sdk import create_simple_agent

# Create agent with simple interface
session = create_simple_agent(
    instructions="You are a Spanish tutor",
    capabilities=["text", "voice"]
)

# Send message and wait for response
session.send_message("¿Cómo estás?")
response = session.wait_for_response()
print(f"Agent: {response.content}")

# Clean up
session.close()
```

### Advanced Configuration

```python
from universal_ai_sdk import UniversalAIClient, AgentConfig

client = UniversalAIClient(
    api_url="https://your-platform.com",
    api_key="your-api-key"
)

config = AgentConfig(
    instructions="You are a emergency services dispatcher",
    capabilities=["text", "voice", "vision"],
    business_logic_adapter="emergencyservices",
    custom_settings={
        "emergency_types": ["medical", "fire", "police"],
        "location_required": True
    },
    client_id="emergency_client_001"
)

session_info = client.create_agent(config)
```

### Error Handling

```python
try:
    result = client.create_agent(config)
except Exception as e:
    print(f"Failed to create agent: {e}")
    
try:
    response = session.wait_for_response(timeout=10)
    if response is None:
        print("No response received within timeout")
except Exception as e:
    print(f"Error waiting for response: {e}")
```

### Usage Tracking

```python
from datetime import datetime, timedelta

# Get usage summary
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

usage = client.get_usage_summary(
    client_id="my_client",
    start_date=start_date,
    end_date=end_date
)

print(f"Sessions: {usage['usage']['sessions']}")
print(f"Messages: {usage['usage']['messages']}")

# Get billing information
billing = client.get_billing_info(
    client_id="my_client",
    plan_id="professional",
    start_date=start_date,
    end_date=end_date
)

print(f"Total cost: ${billing['billing_info']['costs']['total']}")
```

## JavaScript SDK

### Installation

For Node.js:
```bash
npm install node-fetch  # Required for Node.js environments
```

For browsers, include the SDK directly:
```html
<script src="universal-ai-sdk.js"></script>
```

### Quick Start

```javascript
// Browser environment
const client = new UniversalAI.UniversalAIClient('http://localhost:8000');

// Node.js environment
const { UniversalAIClient } = require('./universal-ai-sdk.js');
const client = new UniversalAIClient('http://localhost:8000');

// Create agent
const config = {
    instructions: "You are a helpful assistant",
    capabilities: ["text", "voice"]
};

const result = await client.createAgent(config);
const sessionId = result.session_id;

// Send message and get response
await client.sendMessage(sessionId, "Hello!");
const messages = await client.getMessages(sessionId);
console.log(messages[messages.length - 1].content);
```

### High-Level Session API

```javascript
const { AgentSession } = require('./universal-ai-sdk.js');

// Create simple agent
const session = await UniversalAI.createSimpleAgent(
    "You are a creative writing assistant",
    ["text"]
);

// Send message and wait for response
await session.sendMessage("Write a short story about AI");
const response = await session.waitForResponse();
console.log(`Agent: ${response.content}`);

// Clean up
await session.close();
```

### Event-Driven Programming

```javascript
const session = new AgentSession(client, sessionId);

// Listen for messages
session.on('message', (message) => {
    console.log(`New message: ${message.content}`);
});

// Listen specifically for agent responses
session.on('response', (response) => {
    console.log(`Agent responded: ${response.content}`);
});

// Start polling for messages
const pollId = session.startPolling(1000); // Poll every second

// Send messages
await session.sendMessage("Tell me a joke");

// Stop polling when done
session.stopPolling(pollId);
```

### Advanced Configuration

```javascript
const client = new UniversalAIClient(
    'https://your-platform.com',
    'your-api-key'
);

const config = {
    instructions: "You are a language learning assistant",
    capabilities: ["text", "voice", "vision"],
    businessLogicAdapter: "languagelearning",
    customSettings: {
        targetLanguage: "French",
        proficiencyLevel: "intermediate",
        conversationTopics: ["travel", "culture", "food"]
    },
    clientId: "language_app_user_123"
};

const session = await client.createAgent(config);
```

### Real-Time Integration

```javascript
// Web application example
class ChatInterface {
    constructor() {
        this.client = new UniversalAI.UniversalAIClient();
        this.session = null;
    }
    
    async initializeAgent() {
        const result = await this.client.createAgent({
            instructions: "You are a friendly chat assistant",
            capabilities: ["text"]
        });
        
        this.session = new UniversalAI.AgentSession(
            this.client, 
            result.session_id
        );
        
        // Set up real-time message handling
        this.session.on('response', (response) => {
            this.displayMessage('assistant', response.content);
        });
        
        this.session.startPolling(500);
    }
    
    async sendUserMessage(message) {
        this.displayMessage('user', message);
        await this.session.sendMessage(message);
    }
    
    displayMessage(sender, content) {
        const chatDiv = document.getElementById('chat');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = content;
        chatDiv.appendChild(messageDiv);
    }
}

// Initialize chat
const chat = new ChatInterface();
await chat.initializeAgent();
```

## Integration Examples

### React Integration

```jsx
import React, { useState, useEffect, useRef } from 'react';
import { UniversalAIClient, AgentSession } from './universal-ai-sdk';

function ChatComponent() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [session, setSession] = useState(null);
    const clientRef = useRef(new UniversalAIClient());
    
    useEffect(() => {
        initializeSession();
        return () => {
            if (session) {
                session.close();
            }
        };
    }, []);
    
    const initializeSession = async () => {
        try {
            const result = await clientRef.current.createAgent({
                instructions: "You are a helpful assistant",
                capabilities: ["text"]
            });
            
            const newSession = new AgentSession(
                clientRef.current,
                result.session_id
            );
            
            newSession.on('response', (response) => {
                setMessages(prev => [...prev, {
                    sender: 'assistant',
                    content: response.content,
                    timestamp: new Date()
                }]);
            });
            
            newSession.startPolling(1000);
            setSession(newSession);
            
        } catch (error) {
            console.error('Failed to initialize session:', error);
        }
    };
    
    const sendMessage = async () => {
        if (!input.trim() || !session) return;
        
        const userMessage = {
            sender: 'user',
            content: input,
            timestamp: new Date()
        };
        
        setMessages(prev => [...prev, userMessage]);
        
        try {
            await session.sendMessage(input);
            setInput('');
        } catch (error) {
            console.error('Failed to send message:', error);
        }
    };
    
    return (
        <div className="chat-component">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        <strong>{msg.sender}:</strong> {msg.content}
                    </div>
                ))}
            </div>
            <div className="input-area">
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

### Node.js Server Integration

```javascript
const express = require('express');
const { UniversalAIClient } = require('./universal-ai-sdk');

const app = express();
app.use(express.json());

const client = new UniversalAIClient('http://localhost:8000');
const sessions = new Map();

// Create agent endpoint
app.post('/api/create-agent', async (req, res) => {
    try {
        const { userId, config } = req.body;
        
        const result = await client.createAgent({
            instructions: config.instructions || "You are a helpful assistant",
            capabilities: config.capabilities || ["text"],
            clientId: userId
        });
        
        sessions.set(userId, result.session_id);
        
        res.json({
            success: true,
            sessionId: result.session_id
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Send message endpoint
app.post('/api/send-message', async (req, res) => {
    try {
        const { userId, message } = req.body;
        const sessionId = sessions.get(userId);
        
        if (!sessionId) {
            return res.status(404).json({
                success: false,
                error: 'No active session for user'
            });
        }
        
        await client.sendMessage(sessionId, message);
        
        // Get response
        setTimeout(async () => {
            const messages = await client.getMessages(sessionId);
            const latestMessage = messages[messages.length - 1];
            
            if (latestMessage && latestMessage.sender === 'assistant') {
                res.json({
                    success: true,
                    response: latestMessage.content
                });
            } else {
                res.json({
                    success: true,
                    response: "No response yet"
                });
            }
        }, 2000);
        
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

## Best Practices

### 1. Connection Management

```python
# Python - Use context managers for automatic cleanup
from contextlib import asynccontextmanager

@asynccontextmanager
async def agent_session(client, config):
    result = await client.create_agent(config)
    session = AgentSession(client, result["session_id"])
    try:
        yield session
    finally:
        await session.close()

# Usage
async with agent_session(client, config) as session:
    await session.send_message("Hello")
    response = await session.wait_for_response()
```

```javascript
// JavaScript - Implement proper cleanup
class ManagedSession {
    constructor(client, sessionId) {
        this.session = new AgentSession(client, sessionId);
        this.pollId = null;
    }
    
    start() {
        this.pollId = this.session.startPolling(1000);
    }
    
    async close() {
        if (this.pollId) {
            this.session.stopPolling(this.pollId);
        }
        await this.session.close();
    }
}
```

### 2. Error Recovery

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def send_message_with_retry(session, message):
    return await session.send_message(message)

# Usage
try:
    await send_message_with_retry(session, "Hello")
except Exception as e:
    print(f"Failed after retries: {e}")
```

### 3. Rate Limiting

```javascript
class RateLimitedClient {
    constructor(client, requestsPerSecond = 10) {
        this.client = client;
        this.interval = 1000 / requestsPerSecond;
        this.lastRequest = 0;
    }
    
    async sendMessage(sessionId, message) {
        const now = Date.now();
        const timeSinceLastRequest = now - this.lastRequest;
        
        if (timeSinceLastRequest < this.interval) {
            await new Promise(resolve => 
                setTimeout(resolve, this.interval - timeSinceLastRequest)
            );
        }
        
        this.lastRequest = Date.now();
        return await this.client.sendMessage(sessionId, message);
    }
}
```

### 4. Logging and Monitoring

```python
import logging

# Set up SDK logging
logging.getLogger('universal_ai_sdk').setLevel(logging.DEBUG)

# Custom metrics collection
class MetricsClient(UniversalAIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = {
            'requests_sent': 0,
            'responses_received': 0,
            'errors': 0
        }
    
    async def send_message(self, session_id, message, message_type="text"):
        self.metrics['requests_sent'] += 1
        try:
            result = await super().send_message(session_id, message, message_type)
            self.metrics['responses_received'] += 1
            return result
        except Exception as e:
            self.metrics['errors'] += 1
            raise
```

## Migration Guide

### From Direct API Calls

If you're currently using direct HTTP requests, migrating to the SDK is straightforward:

**Before (direct HTTP):**
```python
import requests

response = requests.post('http://localhost:8000/api/v1/agent/create', json={
    "instructions": "You are helpful",
    "capabilities": ["text"]
})
session_id = response.json()['session_id']

requests.post(f'http://localhost:8000/api/v1/agent/{session_id}/message', json={
    "message": "Hello",
    "type": "text"
})
```

**After (SDK):**
```python
from universal_ai_sdk import create_simple_agent

session = create_simple_agent("You are helpful", ["text"])
session.send_message("Hello")
response = session.wait_for_response()
```

### Version Compatibility

The SDK maintains backward compatibility across minor versions. When upgrading:

1. Check the changelog for breaking changes
2. Update import statements if necessary
3. Test critical functionality
4. Update error handling for new exception types

## Troubleshooting

### Common Issues

1. **Connection Timeouts**
   ```python
   # Increase timeout
   response = session.wait_for_response(timeout=60)
   ```

2. **Authentication Errors**
   ```python
   # Check API key
   client = UniversalAIClient(api_key="correct-key")
   ```

3. **Session Not Found**
   ```python
   # Verify session is still active
   status = session.get_status()
   print(status)
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# SDK will now output detailed debug information
```

```javascript
// Enable console debugging
const client = new UniversalAIClient('http://localhost:8000');
client.debug = true;  // Enable debug output
```