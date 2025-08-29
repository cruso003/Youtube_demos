# NexusAI External Integration Examples

## 1. REST API Usage (Any Programming Language)

### Create an AI Agent Session
POST http://your-nexusai-server.com:8000/api/v1/agent/create
Content-Type: application/json

{
    "agent_id": "customer-support-bot",
    "instructions": "You are a helpful customer support agent for an African telecom company.",
    "capabilities": ["text", "voice"],
    "business_logic_adapter": "customersupport",
    "custom_settings": {
        "language": "en",
        "region": "west-africa"
    }
}

### Send a Message to the Agent
POST http://your-nexusai-server.com:8000/api/v1/agent/{session_id}/message
Content-Type: application/json

{
    "content": "Hello, I need help with my data plan",
    "message_type": "text"
}

### Get Agent Response
GET http://your-nexusai-server.com:8000/api/v1/agent/{session_id}/response

### Upload Image for Analysis
POST http://your-nexusai-server.com:8000/api/v1/agent/{session_id}/image
Content-Type: multipart/form-data

{
    "image": [file upload],
    "prompt": "What do you see in this image?"
}

## 2. Voice Integration
POST http://your-nexusai-server.com:8000/api/v1/agent/{session_id}/voice
Content-Type: audio/wav

[Audio file data]

## 3. Emergency Services Integration
POST http://your-nexusai-server.com:8000/api/v1/agent/create
{
    "business_logic_adapter": "emergencyservices",
    "capabilities": ["text", "voice", "phone"],
    "emergency_config": {
        "dispatch_number": "+234123456789",
        "severity_threshold": "high"
    }
}
