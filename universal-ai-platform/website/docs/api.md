# NexusAI API Reference

The NexusAI platform provides a comprehensive REST API for integrating multimodal AI agents into your applications. Built specifically for African businesses with local payment integration and optimized performance.

## Base URL

```
https://nexus.bits-innovate.com
```

## Authentication

**Optional for Free Tier**: No API key required for testing (5 messages/day limit)

**For Paid Tiers**: Use your API key in the Authorization header:

```http
Authorization: Bearer YOUR_API_KEY
```

## Rate Limits

| Tier | Daily Limit | Rate Limit | Session Limit |
|------|-------------|------------|---------------|
| Free | 5 messages | 1/minute | 1 active |
| Starter | 1,000/month | 60/minute | 10 active |
| Business | Unlimited | 600/minute | Unlimited |

## Core Endpoints

### Health Check

Check the API status and your current usage.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "active_sessions": 12,
  "timestamp": "2025-08-28T22:03:19.519424"
}
```

### Create Agent Session

Create a new AI agent session with specified capabilities.

**Endpoint**: `POST /api/v1/agent/create`

**Request Body**:
```json
{
  "instructions": "You are a helpful assistant for African businesses",
  "capabilities": ["text", "voice", "vision"],
  "business_logic_adapter": "languagelearning",
  "custom_settings": {
    "level": "beginner",
    "native_language": "swahili",
    "focus": "conversation"
  },
  "client_id": "your_client_id"
}
```

**Parameters**:
- `instructions` (string, required): System instructions for the agent
- `capabilities` (array, required): Available: `["text", "voice", "vision"]`
- `business_logic_adapter` (string, optional): `"languagelearning"`, `"emergencyservices"`, or `null`
- `custom_settings` (object, optional): Adapter-specific configuration
- `client_id` (string, optional): Your application identifier

**Response**:
```json
{
  "agent_id": "ead21db9-d5a4-4a93-ba74-fdc7ef477a93",
  "session_id": "ead21db9-d5a4-4a93-ba74-fdc7ef477a93",
  "capabilities": ["text", "voice"],
  "message": "Agent session created successfully",
  "status": "success"
}
```
- `custom_settings` (object, optional): Adapter-specific configuration
- `client_id` (string, optional): Identifier for tracking usage

**Response**:
```json
{
  "session_id": "uuid-session-id",
  "agent_id": "agent_uuid",
  "status": "success",
  "capabilities": ["text", "voice", "vision"],
  "message": "Agent session created successfully"
}
```

**Example**:
```bash
curl -X POST https://nexus.bits-innovate.com/api/v1/agent/create \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "You are a helpful assistant",
    "capabilities": ["text", "voice"]
  }'
```

### Send Message

Send a text message to an agent session.

**Endpoint**: `POST /agent/{session_id}/message`

**Request Body**:
```json
{
  "message": "Hello, how can you help me?",
  "type": "text"
}
```

**Parameters**:
- `message` (string, required): The text message to send
- `type` (string, required): Message type, currently only "text" supported

**Response**:
```json
{
  "status": "success",
  "message": "Message sent successfully"
}
```

**Example**:
```bash
curl -X POST https://nexus.bits-innovate.com/api/v1/agent/abc-123/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "type": "text"
  }'
```

### Send Image

Send an image to an agent session for vision processing.

**Endpoint**: `POST /agent/{session_id}/image`

**Request Body**: Multipart form data
- `image` (file, required): Image file (JPEG, PNG, WebP supported)
- `message` (string, optional): Optional text message to accompany the image

**Response**:
```json
{
  "status": "success",
  "message": "Image sent successfully"
}
```

**Example**:
```bash
curl -X POST https://nexus.bits-innovate.com/api/v1/agent/abc-123/image \
  -F "image=@/path/to/image.jpg" \
  -F "message=What do you see in this image?"
```

### Get Messages

Retrieve all messages from an agent session.

**Endpoint**: `GET /agent/{session_id}/messages`

**Response**:
```json
{
  "messages": [
    {
      "id": "msg-1",
      "type": "user",
      "content": "Hello!",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "id": "msg-2",
      "type": "agent",
      "content": "Hello! How can I help you today?",
      "timestamp": "2024-01-15T10:30:02Z"
    }
  ],
  "session_id": "abc-123",
  "total_messages": 2
}
```

**Example**:
```bash
curl https://nexus.bits-innovate.com/api/v1/agent/abc-123/messages
```

### Get Session Status

Check the status of an agent session.

**Endpoint**: `GET /agent/{session_id}/status`

**Response**:
```json
{
  "session_id": "abc-123",
  "status": "active",
  "capabilities": ["text", "voice", "vision"],
  "adapter": "languagelearning",
  "created_at": "2024-01-15T10:00:00Z",
  "last_activity": "2024-01-15T10:30:02Z"
}
```

### Close Session

Close an agent session and clean up resources.

**Endpoint**: `DELETE /agent/{session_id}`

**Response**:
```json
{
  "status": "success",
  "message": "Session closed successfully"
}
```

## Capabilities

### Available Capabilities

The platform supports three main capabilities:

| Capability | Description | Features |
|------------|-------------|-----------|
| `text` | Natural language conversation | Chat, Q&A, reasoning |
| `voice` | Speech processing | Speech-to-text, text-to-speech |
| `vision` | Image analysis | Object detection, scene description, OCR |

### Capability Configuration

When creating an agent, specify which capabilities you need:

```json
{
  "capabilities": ["text"],           // Text only
  "capabilities": ["text", "voice"],  // Text + Voice
  "capabilities": ["text", "vision"], // Text + Vision
  "capabilities": ["text", "voice", "vision"] // All capabilities
}
```

## Business Logic Adapters

### Built-in Adapters

#### Language Learning Adapter

Optimized for educational applications:

```json
{
  "business_logic_adapter": "languagelearning",
  "custom_settings": {
    "target_language": "Spanish",
    "proficiency_level": "beginner",
    "conversation_topics": ["daily activities", "food", "travel"]
  }
}
```

**Settings**:
- `target_language`: Language to practice (e.g., "Spanish", "French")
- `proficiency_level`: "beginner", "intermediate", "advanced"
- `conversation_topics`: Array of topics to focus on

#### Emergency Services Adapter

Designed for emergency response scenarios:

```json
{
  "business_logic_adapter": "emergencyservices",
  "custom_settings": {
    "emergency_types": ["medical", "fire", "police"],
    "location_required": true,
    "escalation_keywords": ["unconscious", "bleeding", "fire"]
  }
}
```

**Settings**:
- `emergency_types`: Types of emergencies to handle
- `location_required`: Whether location is mandatory
- `escalation_keywords`: Keywords that trigger priority escalation

### Custom Adapters

You can create custom adapters for domain-specific logic. See the [Business Logic Adapters Guide](/docs/guides/adapters) for details.

## Usage Tracking & Billing

### Get Usage Summary

Retrieve usage statistics for billing and monitoring.

**Endpoint**: `GET /usage/{client_id}/summary`

**Query Parameters**:
- `start_date` (string, optional): Start date (ISO 8601 format)
- `end_date` (string, optional): End date (ISO 8601 format)

**Response**:
```json
{
  "client_id": "your_client_id",
  "usage_summary": {
    "total_sessions": 45,
    "total_messages": 1250,
    "total_images": 89,
    "total_duration_minutes": 180
  },
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  }
}
```

### Calculate Bill

Get billing information based on usage.

**Endpoint**: `GET /billing/{client_id}/calculate`

**Query Parameters**:
- `plan` (string, optional): Billing plan ("starter", "professional", "enterprise")

**Response**:
```json
{
  "client_id": "your_client_id",
  "plan": "professional",
  "total_cost": 45.50,
  "breakdown": {
    "base_fee": 25.00,
    "usage_fees": {
      "messages": 15.00,
      "images": 3.50,
      "voice_minutes": 2.00
    }
  },
  "currency": "USD"
}
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid capabilities specified",
    "details": {
      "field": "capabilities",
      "invalid_values": ["invalid_capability"]
    }
  },
  "status": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request validation failed |
| `SESSION_NOT_FOUND` | Agent session does not exist |
| `CAPABILITY_NOT_SUPPORTED` | Requested capability not available |
| `ADAPTER_NOT_FOUND` | Business logic adapter not found |
| `RATE_LIMITED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Development**: 100 requests per minute
- **Starter Plan**: 1,000 requests per hour
- **Professional Plan**: 10,000 requests per hour
- **Enterprise Plan**: Custom limits

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642176000
```

## WebSocket Support

For real-time communication, the platform supports WebSocket connections:

**Endpoint**: `wss://nexus.bits-innovate.com/ws/agent/{session_id}`

**Message Format**:
```json
{
  "type": "message",
  "content": "Hello!",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example**:
```javascript
const ws = new WebSocket('wss://nexus.bits-innovate.com/ws/agent/abc-123');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Agent:', data.content);
};

ws.send(JSON.stringify({
    type: 'message',
    content: 'Hello!'
}));
```

## Interactive Examples

### Complete Example: Creating a Multimodal Agent

```python
import requests
import json

# 1. Create agent
response = requests.post('https://nexus.bits-innovate.com/api/v1/agent/create', json={
    "instructions": "You are a vision-enabled assistant",
    "capabilities": ["text", "vision"],
    "business_logic_adapter": "languagelearning"
})

session_id = response.json()['session_id']
print(f"Created session: {session_id}")

# 2. Send text message
requests.post(f'https://nexus.bits-innovate.com/api/v1/agent/{session_id}/message', json={
    "message": "Can you help me practice Spanish?",
    "type": "text"
})

# 3. Send image
with open('image.jpg', 'rb') as f:
    files = {'image': f}
    data = {'message': 'What do you see in this image?'}
    requests.post(f'https://nexus.bits-innovate.com/api/v1/agent/{session_id}/image', 
                  files=files, data=data)

# 4. Get responses
response = requests.get(f'https://nexus.bits-innovate.com/api/v1/agent/{session_id}/messages')
messages = response.json()['messages']

for msg in messages:
    print(f"{msg['type']}: {msg['content']}")
```

### JavaScript Example

```javascript
const axios = require('axios');

async function createMultimodalAgent() {
    try {
        // 1. Create agent
        const createResponse = await axios.post('https://nexus.bits-innovate.com/api/v1/agent/create', {
            instructions: "You are a helpful assistant",
            capabilities: ["text", "voice", "vision"]
        });
        
        const sessionId = createResponse.data.session_id;
        console.log(`Created session: ${sessionId}`);
        
        // 2. Send message
        await axios.post(`https://nexus.bits-innovate.com/api/v1/agent/${sessionId}/message`, {
            message: "Hello! Can you help me?",
            type: "text"
        });
        
        // 3. Get messages
        const messagesResponse = await axios.get(`https://nexus.bits-innovate.com/api/v1/agent/${sessionId}/messages`);
        const messages = messagesResponse.data.messages;
        
        messages.forEach(msg => {
            console.log(`${msg.type}: ${msg.content}`);
        });
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

createMultimodalAgent();
```

---

**Next Steps**: Explore the [SDK Documentation](/docs/sdks) for higher-level abstractions or check out the [Getting Started Guide](/docs/getting-started) for complete setup instructions.