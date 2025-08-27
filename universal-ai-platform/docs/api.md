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

---

## Multimodal Capabilities

### Voice Processing

#### Generate Speech Response

Convert text to speech with customizable voice settings.

**Endpoint:** `POST /agent/{session_id}/speak`

**Request Body:**
```json
{
  "text": "¡Hola! ¿Cómo estás?",
  "voice_settings": {
    "speed": 0.9,
    "emotion": "encouraging",
    "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "audio_data": "base64_encoded_audio",
  "audio_format": "pcm_16000",
  "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",
  "duration_estimate": 3.2
}
```

#### Process Voice Input

Upload audio file for speech-to-text processing.

**Endpoint:** `POST /agent/{session_id}/voice`

**Request:** Multipart form with audio file

**Response:**
```json
{
  "status": "success",
  "transcript": "Hello, how are you?",
  "confidence": 0.95,
  "language": "en",
  "ready_for_ai_processing": true
}
```

#### Complete Voice Conversation

Full voice workflow: STT → AI Processing → TTS

**Endpoint:** `POST /agent/{session_id}/voice-conversation`

**Request:** Multipart form with audio file

**Response:**
```json
{
  "status": "success",
  "transcript": "Hola, como estas",
  "transcript_confidence": 0.92,
  "response_text": "¡Hola! Estoy muy bien, gracias. ¿Y tú?",
  "response_audio": "base64_encoded_audio",
  "audio_format": "pcm_16000"
}
```

### Vision Processing

#### Analyze Image

Upload and analyze images with AI vision.

**Endpoint:** `POST /agent/{session_id}/image`

**Request:** Multipart form with image file

**Response:**
```json
{
  "status": "success",
  "image_analysis": "I can see a restaurant menu in Spanish with various dishes...",
  "image_format": "jpeg",
  "image_size": [1024, 768],
  "ready_for_conversation": true
}
```

#### Extract Text from Image (OCR)

Extract text content from uploaded images.

**Endpoint:** `POST /agent/{session_id}/image-text`

**Request:** Multipart form with image file and optional language

**Response:**
```json
{
  "status": "success",
  "extracted_text": "MENÚ DEL DÍA\nPaella Valenciana - €15\nGazpacho - €8",
  "language": "es",
  "confidence": 0.89
}
```

#### Image Conversation

Complete image workflow with conversational response.

**Endpoint:** `POST /agent/{session_id}/image-conversation`

**Request:** Multipart form with image file and optional prompt

**Response:**
```json
{
  "status": "success",
  "image_analysis": "This is a Spanish restaurant menu showing traditional dishes...",
  "user_prompt": "Help me understand this menu",
  "response_text": "I can help you understand this Spanish menu! The dishes shown are..."
}
```

#### Specialized Scene Analysis

Domain-specific image analysis based on business adapter.

**Endpoint:** `POST /agent/{session_id}/analyze-scene`

**Request:** Multipart form with image and analysis_type

**Response:**
```json
{
  "status": "success",
  "scene_analysis": "SAFETY ASSESSMENT: No immediate hazards visible...",
  "analysis_type": "safety",
  "adapter": "emergencyservices",
  "confidence_indicators": {
    "has_uncertainty_words": false,
    "detail_level": "high"
  }
}
```

### Real-time Sessions

#### Start Real-time Session

Create LiveKit room for multimodal real-time interaction.

**Endpoint:** `POST /agent/{session_id}/realtime/start`

**Request Body:**
```json
{
  "max_participants": 5,
  "audio_enabled": true,
  "video_enabled": true,
  "recording_enabled": false
}
```

**Response:**
```json
{
  "status": "success",
  "room_details": {
    "room_name": "session_uuid-session-id",
    "access_token": "livekit_access_token",
    "livekit_url": "wss://your-livekit-server.com"
  },
  "agent_details": {
    "agent_id": "agent_session_uuid",
    "capabilities": ["text", "voice", "vision"],
    "status": "starting"
  }
}
```

#### Get Real-time Status

Check status of active real-time session.

**Endpoint:** `GET /agent/{session_id}/realtime/status`

**Response:**
```json
{
  "status": "success",
  "realtime_active": true,
  "room_name": "session_uuid-session-id",
  "duration_seconds": 145.7,
  "session_status": "realtime_active"
}
```

#### Stop Real-time Session

End real-time session and cleanup resources.

**Endpoint:** `POST /agent/{session_id}/realtime/stop`

**Response:**
```json
{
  "status": "success",
  "message": "Real-time session stopped successfully",
  "duration_seconds": 180.5
}
```

### Phone Integration

#### Initiate Phone Call

Start phone call via Twilio integration.

**Endpoint:** `POST /agent/{session_id}/phone/call`

**Request Body:**
```json
{
  "to_number": "+15551234567"
}
```

**Response:**
```json
{
  "status": "success",
  "call_details": {
    "call_sid": "CA1234567890abcdef",
    "to_number": "+15551234567",
    "from_number": "+15559876543",
    "status": "initiated"
  }
}
```

#### End Phone Call

Terminate active phone call.

**Endpoint:** `POST /agent/{session_id}/phone/end`

**Response:**
```json
{
  "status": "success",
  "message": "Phone call ended successfully",
  "call_sid": "CA1234567890abcdef"
}
```

#### TwiML Webhook

Handle TwiML webhook from Twilio (internal endpoint).

**Endpoint:** `POST /phone/twiml/{session_id}`

Returns TwiML XML for call handling.

## Usage Examples

### Language Learning with Voice and Vision

```python
import requests

# Create language learning session
session = requests.post('/api/v1/agent/create', json={
    "instructions": "You are a Spanish language tutor",
    "capabilities": ["text", "voice", "vision"],
    "business_logic_adapter": "languagelearning",
    "custom_settings": {
        "target_language": "Spanish",
        "proficiency_level": "beginner"
    }
}).json()

session_id = session['session_id']

# Upload image of Spanish menu
with open('spanish_menu.jpg', 'rb') as f:
    image_response = requests.post(
        f'/api/v1/agent/{session_id}/image-conversation',
        files={'image': f},
        data={'prompt': 'Help me understand this menu in Spanish'}
    ).json()

print("Vision Analysis:", image_response['response_text'])

# Generate pronunciation audio
audio_response = requests.post(
    f'/api/v1/agent/{session_id}/speak',
    json={
        "text": "Paella Valenciana se pronuncia: pa-EH-ya va-len-see-AH-na",
        "voice_settings": {"speed": 0.8, "emotion": "encouraging"}
    }
).json()

# Save audio for playback
with open('pronunciation.wav', 'wb') as f:
    f.write(base64.b64decode(audio_response['audio_data']))
```

### Emergency Services with Real-time Communication

```python
# Create emergency services session
session = requests.post('/api/v1/agent/create', json={
    "instructions": "You are an emergency services AI dispatcher",
    "capabilities": ["text", "voice", "vision"],
    "business_logic_adapter": "emergencyservices"
}).json()

session_id = session['session_id']

# Start real-time session for live communication
realtime = requests.post(f'/api/v1/agent/{session_id}/realtime/start', json={
    "audio_enabled": True,
    "video_enabled": True,
    "recording_enabled": True
}).json()

# Initiate emergency call
call = requests.post(f'/api/v1/agent/{session_id}/phone/call', json={
    "to_number": "+15551234567"
}).json()

# Process emergency scene image
with open('accident_scene.jpg', 'rb') as f:
    scene_analysis = requests.post(
        f'/api/v1/agent/{session_id}/analyze-scene',
        files={'image': f},
        data={'analysis_type': 'safety'}
    ).json()

print("Emergency Analysis:", scene_analysis['scene_analysis'])
```