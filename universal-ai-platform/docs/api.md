# Universal AI Agent Platform - API Reference

## Overview

The Universal AI Agent Platform provides a REST API for integrating multimodal AI agents into your applications. The platform supports voice, vision, and text capabilities with customizable business logic adapters.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the platform supports optional API key authentication via the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Agent Management

### Create Agent Session

Create a new AI agent session with specified capabilities and configuration.

**Endpoint:** `POST /agent/create`

**Request Body:**
```json
{
  "instructions": "You are a helpful AI assistant",
  "capabilities": ["text", "voice", "vision"],
  "business_logic_adapter": "languagelearning",
  "custom_settings": {
    "target_language": "Spanish",
    "proficiency_level": "beginner"
  },
  "client_id": "your_client_id"
}
```

**Response:**
```json
{
  "session_id": "uuid-session-id",
  "agent_id": "agent_uuid",
  "status": "success",
  "capabilities": ["text", "voice", "vision"],
  "message": "Agent session created successfully"
}
```

### Send Message

Send a message to an active agent session.

**Endpoint:** `POST /agent/{session_id}/message`

**Request Body:**
```json
{
  "message": "Hello, can you help me?",
  "type": "text"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Message sent successfully"
}
```

### Get Messages

Retrieve messages from an agent session.

**Endpoint:** `GET /agent/{session_id}/messages`

**Response:**
```json
{
  "status": "success",
  "messages": [
    {
      "id": "message-uuid",
      "type": "text",
      "content": "Hello! How can I help you today?",
      "timestamp": "2024-01-15T10:30:00Z",
      "sender": "assistant"
    }
  ],
  "session_status": "active"
}
```

### Get Session Status

Get the current status of an agent session.

**Endpoint:** `GET /agent/{session_id}/status`

**Response:**
```json
{
  "session_id": "uuid-session-id",
  "agent_id": "agent_uuid",
  "status": "active",
  "capabilities": ["text", "voice", "vision"],
  "created_at": "2024-01-15T10:00:00Z",
  "business_logic_adapter": "languagelearning"
}
```

### Delete Session

Delete an agent session and clean up resources.

**Endpoint:** `DELETE /agent/{session_id}`

**Response:**
```json
{
  "status": "success",
  "message": "Session deleted successfully"
}
```

### List Active Sessions

Get a list of all active agent sessions.

**Endpoint:** `GET /agents`

**Response:**
```json
{
  "status": "success",
  "sessions": [
    {
      "session_id": "uuid-1",
      "agent_id": "agent-1",
      "status": "active",
      "capabilities": ["text", "voice"],
      "created_at": "2024-01-15T10:00:00Z",
      "client_id": "client_1"
    }
  ],
  "total_sessions": 1
}
```

## Usage Tracking & Billing

### Get Usage Summary

Get usage statistics for billing purposes.

**Endpoint:** `GET /usage/{client_id}`

**Query Parameters:**
- `start_date` (optional): ISO 8601 date string
- `end_date` (optional): ISO 8601 date string

**Response:**
```json
{
  "status": "success",
  "client_id": "client_1",
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "usage": {
    "sessions": 50,
    "messages": 1250,
    "images": 25,
    "total_duration_minutes": 180.5
  }
}
```

### Get Billing Information

Calculate billing based on usage and plan.

**Endpoint:** `GET /billing/{client_id}`

**Query Parameters:**
- `plan_id` (default: "starter"): Billing plan identifier
- `start_date` (optional): ISO 8601 date string
- `end_date` (optional): ISO 8601 date string

**Response:**
```json
{
  "status": "success",
  "billing_info": {
    "client_id": "client_1",
    "plan": {
      "plan_id": "starter",
      "name": "Starter Plan",
      "price_per_session": 0.10,
      "price_per_message": 0.01,
      "price_per_image": 0.05,
      "price_per_minute": 0.02,
      "included_sessions": 100,
      "included_messages": 1000,
      "included_images": 100,
      "included_minutes": 300
    },
    "usage": {
      "sessions": 50,
      "messages": 1250,
      "images": 25,
      "total_duration_minutes": 180.5
    },
    "billable_usage": {
      "sessions": 0,
      "messages": 250,
      "images": 0,
      "minutes": 0
    },
    "costs": {
      "sessions": 0.0,
      "messages": 2.50,
      "images": 0.0,
      "minutes": 0.0,
      "total": 2.50
    }
  }
}
```

## Capabilities

### Supported Capabilities

The platform supports the following agent capabilities:

- **text**: Text-based conversation
- **voice**: Speech-to-text and text-to-speech
- **vision**: Image analysis and processing

### Message Types

- **text**: Plain text messages
- **image**: Base64-encoded images or image URLs
- **audio**: Audio data for voice processing

## Business Logic Adapters

Business logic adapters allow customization of agent behavior for specific use cases:

### Available Adapters

- **languagelearning**: Optimized for language learning applications
- **emergencyservices**: Configured for emergency response scenarios
- **default**: Standard behavior with no special processing

### Custom Adapters

You can create custom business logic adapters by extending the `BusinessLogicAdapter` base class.

## Error Handling

All API endpoints return standardized error responses:

```json
{
  "status": "error",
  "message": "Description of the error"
}
```

### Common HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

The platform implements rate limiting based on your billing plan:

- **Starter Plan**: 100 requests/minute
- **Professional Plan**: 500 requests/minute
- **Enterprise Plan**: 2000 requests/minute

## WebSocket Support

For real-time communication, the platform also supports WebSocket connections for streaming responses and live interactions.

**WebSocket Endpoint:** `ws://localhost:8000/ws/agent/{session_id}`

## Examples

### Creating a Simple Chat Agent

```python
import requests

# Create agent
response = requests.post('http://localhost:8000/api/v1/agent/create', json={
    "instructions": "You are a helpful assistant",
    "capabilities": ["text"]
})

session_id = response.json()['session_id']

# Send message
requests.post(f'http://localhost:8000/api/v1/agent/{session_id}/message', json={
    "message": "Hello!",
    "type": "text"
})

# Get response
response = requests.get(f'http://localhost:8000/api/v1/agent/{session_id}/messages')
messages = response.json()['messages']
```

### Creating a Multimodal Agent

```javascript
const client = new UniversalAIClient('http://localhost:8000');

const session = await client.createAgent({
    instructions: "You are a vision-enabled assistant",
    capabilities: ["text", "vision", "voice"],
    businessLogicAdapter: "languagelearning"
});

await session.sendMessage("Can you help me practice Spanish?");
const response = await session.waitForResponse();
console.log(response.content);
```