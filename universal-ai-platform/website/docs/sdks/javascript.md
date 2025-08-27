# JavaScript SDK

The JavaScript SDK provides a comprehensive interface for integrating AI agents into both browser and Node.js applications.

## Installation

### Node.js

```bash
# Copy SDK to your project
cp client_sdks/javascript/universal-ai-sdk.js your_project/
```

### Browser

```html
<!-- Include the SDK directly -->
<script src="universal-ai-sdk.js"></script>
```

### ES6 Modules

```javascript
// Import the SDK
import { UniversalAIClient } from './universal-ai-sdk.js';
```

## Quick Start

### Node.js Environment

```javascript
const { UniversalAIClient } = require('./universal-ai-sdk.js');

// Create client
const client = new UniversalAIClient('http://localhost:8000');

// Create agent
const config = {
    instructions: "You are a helpful assistant",
    capabilities: ["text", "voice"]
};

async function quickStart() {
    try {
        const result = await client.createAgent(config);
        const sessionId = result.session_id;
        
        // Send message and get response
        await client.sendMessage(sessionId, "Hello!");
        const messages = await client.getMessages(sessionId);
        
        console.log('Agent:', messages[messages.length - 1].content);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

quickStart();
```

### Browser Environment

```javascript
// Browser usage
const client = new UniversalAI.UniversalAIClient('http://localhost:8000');

async function createChatBot() {
    const config = {
        instructions: "You are a friendly chatbot",
        capabilities: ["text"]
    };
    
    const session = await client.createAgent(config);
    const sessionId = session.session_id;
    
    // Send message
    await client.sendMessage(sessionId, "Hi there!");
    
    // Get response
    const messages = await client.getMessages(sessionId);
    const lastMessage = messages[messages.length - 1];
    
    document.getElementById('chat').innerHTML += 
        `<div>Bot: ${lastMessage.content}</div>`;
}
```

## Core Classes

### UniversalAIClient

The main client class for API communication.

```javascript
class UniversalAIClient {
    constructor(baseUrl = 'http://localhost:8000', apiKey = null) {
        /**
         * Initialize the Universal AI client.
         * 
         * @param {string} baseUrl - API gateway URL
         * @param {string} apiKey - Optional API key for authentication
         */
    }
}
```

**Methods**:

#### createAgent(config) → Promise\<Object\>
```javascript
const result = await client.createAgent({
    instructions: "You are a helpful assistant",
    capabilities: ["text", "voice", "vision"],
    businessLogicAdapter: "languagelearning",
    customSettings: {
        targetLanguage: "Spanish",
        proficiencyLevel: "beginner"
    },
    clientId: "user_123"
});
```

#### sendMessage(sessionId, message) → Promise\<boolean\>
```javascript
const success = await client.sendMessage(sessionId, "Hello!");
```

#### sendImage(sessionId, imageFile, message) → Promise\<boolean\>
```javascript
// Browser file input
const fileInput = document.getElementById('imageInput');
const file = fileInput.files[0];
const success = await client.sendImage(sessionId, file, "What do you see?");

// Node.js
const fs = require('fs');
const imageBuffer = fs.readFileSync('image.jpg');
const success = await client.sendImage(sessionId, imageBuffer, "Analyze this image");
```

#### getMessages(sessionId) → Promise\<Array\>
```javascript
const messages = await client.getMessages(sessionId);
messages.forEach(msg => {
    console.log(`${msg.type}: ${msg.content}`);
});
```

#### getSessionStatus(sessionId) → Promise\<Object\>
```javascript
const status = await client.getSessionStatus(sessionId);
console.log(`Session status: ${status.status}`);
```

#### closeSession(sessionId) → Promise\<boolean\>
```javascript
await client.closeSession(sessionId);
```

#### getUsageSummary(clientId, startDate, endDate) → Promise\<Object\>
```javascript
const usage = await client.getUsageSummary("user_123", "2024-01-01", "2024-01-31");
console.log(`Total sessions: ${usage.usage_summary.total_sessions}`);
```

### AgentSession

High-level wrapper for agent interactions.

```javascript
class AgentSession {
    constructor(sessionId, client) {
        /**
         * Agent session for simplified communication.
         * 
         * @param {string} sessionId - Unique session identifier
         * @param {UniversalAIClient} client - Client instance
         */
    }
}
```

**Methods**:

#### sendMessage(message) → Promise\<void\>
```javascript
await session.sendMessage("How can you help me?");
```

#### waitForResponse(timeout = 30000) → Promise\<Object\>
```javascript
const response = await session.waitForResponse(60000);
console.log(response.content);
```

#### sendImage(imageFile, message) → Promise\<void\>
```javascript
await session.sendImage(file, "What's in this image?");
```

#### close() → Promise\<void\>
```javascript
await session.close();
```

## Usage Examples

### Simple Chat Application

```html
<!DOCTYPE html>
<html>
<head>
    <title>AI Chat</title>
    <script src="universal-ai-sdk.js"></script>
</head>
<body>
    <div id="chat"></div>
    <input type="text" id="messageInput" placeholder="Type your message...">
    <button onclick="sendMessage()">Send</button>
    
    <script>
        const client = new UniversalAI.UniversalAIClient('http://localhost:8000');
        let sessionId = null;
        
        // Initialize chat
        async function initChat() {
            const result = await client.createAgent({
                instructions: "You are a friendly chatbot",
                capabilities: ["text"]
            });
            sessionId = result.session_id;
            console.log('Chat initialized!');
        }
        
        // Send message
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message || !sessionId) return;
            
            // Display user message
            addMessageToChat('You', message);
            input.value = '';
            
            try {
                // Send to AI
                await client.sendMessage(sessionId, message);
                
                // Get response
                const messages = await client.getMessages(sessionId);
                const lastMessage = messages[messages.length - 1];
                
                if (lastMessage.type === 'agent') {
                    addMessageToChat('AI', lastMessage.content);
                }
            } catch (error) {
                addMessageToChat('System', 'Error: ' + error.message);
            }
        }
        
        function addMessageToChat(sender, message) {
            const chat = document.getElementById('chat');
            chat.innerHTML += `<div><strong>${sender}:</strong> ${message}</div>`;
            chat.scrollTop = chat.scrollHeight;
        }
        
        // Initialize on page load
        initChat();
        
        // Send message on Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
```

### Language Learning App

```javascript
class LanguageLearningApp {
    constructor() {
        this.client = new UniversalAI.UniversalAIClient('http://localhost:8000');
        this.sessions = new Map(); // user_id -> session_id
    }
    
    async createTutorSession(userId, targetLanguage, proficiencyLevel) {
        const config = {
            instructions: `You are a ${targetLanguage} tutor. Help the user practice conversation.`,
            capabilities: ["text", "voice"],
            businessLogicAdapter: "languagelearning",
            customSettings: {
                targetLanguage: targetLanguage,
                proficiencyLevel: proficiencyLevel,
                conversationTopics: ["daily activities", "travel", "food"]
            },
            clientId: userId
        };
        
        const result = await this.client.createAgent(config);
        this.sessions.set(userId, result.session_id);
        
        return result.session_id;
    }
    
    async sendPracticeMessage(userId, message) {
        const sessionId = this.sessions.get(userId);
        if (!sessionId) {
            throw new Error('No active session for user');
        }
        
        await this.client.sendMessage(sessionId, message);
        
        // Wait a bit for response
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const messages = await this.client.getMessages(sessionId);
        return messages[messages.length - 1];
    }
    
    async endSession(userId) {
        const sessionId = this.sessions.get(userId);
        if (sessionId) {
            await this.client.closeSession(sessionId);
            this.sessions.delete(userId);
        }
    }
}

// Usage
const app = new LanguageLearningApp();

async function startLearning() {
    try {
        // Start Spanish learning session
        await app.createTutorSession("user_123", "Spanish", "beginner");
        
        // Practice conversation
        const response1 = await app.sendPracticeMessage("user_123", "Hola! ¿Cómo estás?");
        console.log('Tutor:', response1.content);
        
        const response2 = await app.sendPracticeMessage("user_123", "Estoy bien, gracias. ¿Y tú?");
        console.log('Tutor:', response2.content);
        
        // End session
        await app.endSession("user_123");
    } catch (error) {
        console.error('Error:', error.message);
    }
}

startLearning();
```

### Voice-Enabled Chat

```javascript
class VoiceChat {
    constructor() {
        this.client = new UniversalAI.UniversalAIClient('http://localhost:8000');
        this.sessionId = null;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
    }
    
    async initialize() {
        // Create voice-enabled agent
        const result = await this.client.createAgent({
            instructions: "You are a voice assistant. Keep responses conversational and brief.",
            capabilities: ["text", "voice"]
        });
        
        this.sessionId = result.session_id;
        
        // Setup speech recognition
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = async (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('You said:', transcript);
                await this.sendVoiceMessage(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isListening = false;
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
            };
        }
    }
    
    startListening() {
        if (this.recognition && !this.isListening) {
            this.isListening = true;
            this.recognition.start();
            console.log('Listening...');
        }
    }
    
    async sendVoiceMessage(message) {
        try {
            await this.client.sendMessage(this.sessionId, message);
            
            // Get response
            const messages = await this.client.getMessages(this.sessionId);
            const lastMessage = messages[messages.length - 1];
            
            if (lastMessage.type === 'agent') {
                this.speakResponse(lastMessage.content);
            }
        } catch (error) {
            console.error('Error:', error.message);
        }
    }
    
    speakResponse(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        this.synthesis.speak(utterance);
    }
}

// Usage
const voiceChat = new VoiceChat();

async function startVoiceChat() {
    await voiceChat.initialize();
    console.log('Voice chat ready! Click the button to start talking.');
    
    // Add button to page
    const button = document.createElement('button');
    button.textContent = 'Start Talking';
    button.onclick = () => voiceChat.startListening();
    document.body.appendChild(button);
}

startVoiceChat();
```

### Image Analysis App

```javascript
class ImageAnalyzer {
    constructor() {
        this.client = new UniversalAI.UniversalAIClient('http://localhost:8000');
        this.sessionId = null;
    }
    
    async initialize() {
        const result = await this.client.createAgent({
            instructions: "You are an image analysis expert. Describe what you see in detail.",
            capabilities: ["text", "vision"]
        });
        
        this.sessionId = result.session_id;
    }
    
    async analyzeImage(imageFile, question = "What do you see in this image?") {
        try {
            await this.client.sendImage(this.sessionId, imageFile, question);
            
            // Wait for analysis
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            const messages = await this.client.getMessages(this.sessionId);
            const lastMessage = messages[messages.length - 1];
            
            return lastMessage.content;
        } catch (error) {
            console.error('Image analysis error:', error.message);
            return 'Error analyzing image';
        }
    }
}

// HTML interface
function createImageAnalyzerInterface() {
    const html = `
        <div>
            <h3>Image Analyzer</h3>
            <input type="file" id="imageInput" accept="image/*">
            <input type="text" id="questionInput" placeholder="What would you like to know about the image?">
            <button onclick="analyzeSelectedImage()">Analyze Image</button>
            <div id="result"></div>
        </div>
    `;
    
    document.body.innerHTML = html;
}

const analyzer = new ImageAnalyzer();

async function analyzeSelectedImage() {
    const fileInput = document.getElementById('imageInput');
    const questionInput = document.getElementById('questionInput');
    const resultDiv = document.getElementById('result');
    
    if (!fileInput.files[0]) {
        alert('Please select an image first');
        return;
    }
    
    const file = fileInput.files[0];
    const question = questionInput.value || "What do you see in this image?";
    
    resultDiv.innerHTML = 'Analyzing image...';
    
    const analysis = await analyzer.analyzeImage(file, question);
    resultDiv.innerHTML = `<strong>Analysis:</strong> ${analysis}`;
}

// Initialize
analyzer.initialize().then(() => {
    createImageAnalyzerInterface();
    console.log('Image analyzer ready!');
});
```

## Advanced Features

### Error Handling

```javascript
class RobustAIClient {
    constructor(baseUrl, apiKey) {
        this.client = new UniversalAI.UniversalAIClient(baseUrl, apiKey);
        this.maxRetries = 3;
        this.retryDelay = 1000; // ms
    }
    
    async sendMessageWithRetry(sessionId, message) {
        for (let attempt = 0; attempt < this.maxRetries; attempt++) {
            try {
                await this.client.sendMessage(sessionId, message);
                return await this.client.getMessages(sessionId);
            } catch (error) {
                console.warn(`Attempt ${attempt + 1} failed:`, error.message);
                
                if (attempt < this.maxRetries - 1) {
                    await this.delay(this.retryDelay * Math.pow(2, attempt));
                } else {
                    throw error;
                }
            }
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

### WebSocket Real-time Communication

```javascript
class RealTimeChat {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.ws = null;
        this.sessionId = null;
        this.messageHandlers = [];
    }
    
    async connect() {
        // First create agent session
        const client = new UniversalAI.UniversalAIClient(this.baseUrl);
        const result = await client.createAgent({
            instructions: "You are a real-time chat assistant",
            capabilities: ["text"]
        });
        
        this.sessionId = result.session_id;
        
        // Connect WebSocket
        const wsUrl = this.baseUrl.replace('http', 'ws') + `/ws/agent/${this.sessionId}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('Real-time connection established');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.messageHandlers.forEach(handler => handler(data));
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        this.ws.onclose = () => {
            console.log('Real-time connection closed');
        };
    }
    
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'message',
                content: message,
                timestamp: new Date().toISOString()
            }));
        }
    }
    
    onMessage(handler) {
        this.messageHandlers.push(handler);
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Usage
const realTimeChat = new RealTimeChat('http://localhost:8000');

realTimeChat.onMessage((data) => {
    console.log('Received:', data.content);
    // Update UI with new message
});

await realTimeChat.connect();
realTimeChat.sendMessage('Hello in real-time!');
```

### Session Management

```javascript
class SessionManager {
    constructor() {
        this.client = new UniversalAI.UniversalAIClient('http://localhost:8000');
        this.activeSessions = new Map();
        this.sessionConfigs = new Map();
    }
    
    async createSession(userId, config) {
        const result = await this.client.createAgent(config);
        const sessionId = result.session_id;
        
        this.activeSessions.set(userId, sessionId);
        this.sessionConfigs.set(userId, config);
        
        // Auto-cleanup after inactivity
        this.scheduleCleanup(userId, 30 * 60 * 1000); // 30 minutes
        
        return sessionId;
    }
    
    async getOrCreateSession(userId, config) {
        let sessionId = this.activeSessions.get(userId);
        
        if (!sessionId) {
            sessionId = await this.createSession(userId, config);
        }
        
        return sessionId;
    }
    
    async sendMessage(userId, message) {
        const sessionId = this.activeSessions.get(userId);
        if (!sessionId) {
            throw new Error('No active session for user');
        }
        
        await this.client.sendMessage(sessionId, message);
        return await this.client.getMessages(sessionId);
    }
    
    scheduleCleanup(userId, delay) {
        setTimeout(async () => {
            await this.closeSession(userId);
        }, delay);
    }
    
    async closeSession(userId) {
        const sessionId = this.activeSessions.get(userId);
        if (sessionId) {
            await this.client.closeSession(sessionId);
            this.activeSessions.delete(userId);
            this.sessionConfigs.delete(userId);
        }
    }
    
    async closeAllSessions() {
        const promises = Array.from(this.activeSessions.keys()).map(userId => 
            this.closeSession(userId)
        );
        await Promise.all(promises);
    }
}

// Usage
const sessionManager = new SessionManager();

// Auto-cleanup on page unload
window.addEventListener('beforeunload', () => {
    sessionManager.closeAllSessions();
});
```

## Configuration

### Environment-based Configuration

```javascript
class ConfigurableClient {
    constructor(config = {}) {
        const defaultConfig = {
            baseUrl: process.env.UNIVERSAL_AI_BASE_URL || 'http://localhost:8000',
            apiKey: process.env.UNIVERSAL_AI_API_KEY || null,
            timeout: parseInt(process.env.UNIVERSAL_AI_TIMEOUT) || 30000,
            maxRetries: parseInt(process.env.UNIVERSAL_AI_MAX_RETRIES) || 3,
            debug: process.env.UNIVERSAL_AI_DEBUG === 'true'
        };
        
        this.config = { ...defaultConfig, ...config };
        this.client = new UniversalAI.UniversalAIClient(
            this.config.baseUrl, 
            this.config.apiKey
        );
        
        if (this.config.debug) {
            console.log('Universal AI Client Config:', this.config);
        }
    }
}
```

## Testing

### Unit Testing with Jest

```javascript
// universal-ai.test.js
const { UniversalAIClient } = require('../universal-ai-sdk.js');

// Mock fetch for testing
global.fetch = jest.fn();

describe('UniversalAIClient', () => {
    let client;
    
    beforeEach(() => {
        client = new UniversalAIClient('http://test.com');
        fetch.mockClear();
    });
    
    test('should create agent successfully', async () => {
        const mockResponse = {
            session_id: 'test-session-123',
            status: 'success'
        };
        
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockResponse
        });
        
        const config = {
            instructions: 'Test agent',
            capabilities: ['text']
        };
        
        const result = await client.createAgent(config);
        
        expect(result.session_id).toBe('test-session-123');
        expect(fetch).toHaveBeenCalledWith(
            'http://test.com/api/v1/agent/create',
            expect.objectContaining({
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })
        );
    });
    
    test('should handle API errors', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 400,
            json: async () => ({
                error: { message: 'Invalid request' }
            })
        });
        
        await expect(client.createAgent({})).rejects.toThrow('Invalid request');
    });
});
```

### Integration Testing

```javascript
// integration.test.js
describe('Integration Tests', () => {
    let client;
    let sessionId;
    
    beforeAll(() => {
        client = new UniversalAI.UniversalAIClient('http://localhost:8000');
    });
    
    test('full conversation flow', async () => {
        // Create agent
        const result = await client.createAgent({
            instructions: 'You are a test assistant',
            capabilities: ['text']
        });
        
        sessionId = result.session_id;
        expect(sessionId).toBeDefined();
        
        // Send message
        await client.sendMessage(sessionId, 'Hello!');
        
        // Get messages
        const messages = await client.getMessages(sessionId);
        expect(messages.length).toBeGreaterThan(0);
        
        // Verify response
        const lastMessage = messages[messages.length - 1];
        expect(lastMessage.type).toBe('agent');
        expect(lastMessage.content).toBeDefined();
    });
    
    afterAll(async () => {
        if (sessionId) {
            await client.closeSession(sessionId);
        }
    });
});
```

---

**Next**: Explore [Business Logic Adapters](/docs/guides/adapters) or check out complete [Examples](/examples/language-learning).