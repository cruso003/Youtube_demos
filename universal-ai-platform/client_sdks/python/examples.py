#!/usr/bin/env python3

"""
NexusAI Python SDK - Example Usage

This example demonstrates how to use the NexusAI SDK for:
1. Language Learning Applications
2. Emergency Services Integration
3. General AI Agent Creation
"""

import sys
import asyncio
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from nexusai_sdk import NexusAIClient, AgentConfig, AgentSession, create_simple_agent

def language_learning_example():
    """Demonstrate language learning capabilities"""
    print('\n🎓 Language Learning Example')
    print('=' * 40)
    
    client = NexusAIClient('https://nexus.bits-innovate.com')
    
    try:
        # Create a language learning agent
        config = AgentConfig(
            instructions="You are a friendly English tutor for African students. Focus on practical conversation skills and pronunciation.",
            capabilities=["text", "voice"],
            business_logic_adapter="languagelearning",
            custom_settings={
                "level": "beginner",
                "focus": "conversation",
                "native_language": "swahili"
            }
        )
        
        agent = client.create_agent(config)
        print(f'✅ Created Language Learning Agent: {agent["agent_id"]}')
        
        # Start a learning session using the session_id from agent creation
        session_id = agent["session_id"]
        print(f'✅ Created Learning Session: {session_id}')
        
        # Student asks for help
        response = client.send_message(
            session_id,
            "Hello! I want to learn how to introduce myself in English for job interviews."
        )
        
        print(f'🤖 Tutor Response: {response["message"]}')
        
        # Get conversation history
        messages = client.get_messages(session_id)
        print(f'📚 Conversation History: {len(messages)} messages')
        
        return agent, {"session_id": session_id}
        
    except Exception as error:
        print(f'❌ Language Learning Error: {error}')
        return None, None

def emergency_services_example():
    """Demonstrate emergency services capabilities"""
    print('\n🚨 Emergency Services Example')
    print('=' * 40)
    
    client = NexusAIClient('https://nexus.bits-innovate.com')
    
    try:
        # Create emergency services agent
        config = AgentConfig(
            instructions="You are an emergency response coordinator. Assess situations quickly and provide immediate help while coordinating with local emergency services.",
            capabilities=["text", "voice"],
            business_logic_adapter="emergencyservices",
            custom_settings={
                "region": "west-africa",
                "languages": ["english", "french"],
                "emergency_contacts": {
                    "police": "+233-999",
                    "ambulance": "+233-777",
                    "fire": "+233-888"
                }
            }
        )
        
        agent = client.create_agent(config)
        print(f'✅ Created Emergency Agent: {agent["agent_id"]}')
        
        # Emergency session using the session_id from agent creation
        session_id = agent["session_id"]
        print(f'✅ Created Emergency Session: {session_id}')
        
        # Simulate emergency report
        response = client.send_message(
            session_id,
            "URGENT: Traffic accident on Accra-Tema highway, 2 people injured, need ambulance immediately!"
        )
        
        print(f'🚨 Emergency Response: {response["message"]}')
        print('📞 Automatic emergency calls would be triggered...')
        
        return agent, {"session_id": session_id}
        
    except Exception as error:
        print(f'❌ Emergency Services Error: {error}')
        return None, None

def business_chatbot_example():
    """Demonstrate business chatbot capabilities"""
    print('\n💼 Business Chatbot Example')
    print('=' * 40)
    
    try:
        # Quick setup for business use
        client, agent, session = create_simple_agent(
            'https://nexus.bits-innovate.com',
            'You are a customer service agent for an African e-commerce platform. Help customers with orders, payments, and product inquiries.',
            ['text', 'voice']
        )
        
        print('✅ Quick Business Agent Setup Complete')
        print(f'   Agent ID: {agent["id"]}')
        print(f'   Session ID: {session.session_id}')
        
        # Customer inquiry
        response = session.send_message(
            "Hi, I ordered a phone 3 days ago but haven't received tracking information. My order number is AF-123456."
        )
        
        print(f'🤖 Business Bot Response: {response["message"]}')
        
        # Multiple follow-up messages
        follow_up1 = session.send_message(
            "When will it be delivered? I need it urgently for work."
        )
        
        print(f'🤖 Follow-up Response: {follow_up1["message"]}')
        
        # Get full conversation
        history = session.get_history(limit=10)
        print(f'💬 Total Conversation Messages: {len(history)}')
        
        # Clean up
        session.close()
        print('✅ Session closed successfully')
        
        return client, agent, session
        
    except Exception as error:
        print(f'❌ Business Chatbot Error: {error}')
        return None, None, None

def health_check_example():
    """Check NexusAI platform health"""
    print('\n🏥 Health Check Example')
    print('=' * 40)
    
    client = NexusAIClient('https://nexus.bits-innovate.com')
    
    try:
        health = client.health_check()
        print(f'✅ NexusAI Platform Status: {health}')
        
        # Check API connectivity
        print(f'🌐 API Endpoint: {client.api_url}')
        print(f'🔒 Using HTTPS: {client.api_url.startswith("https")}')
        
        return health
        
    except Exception as error:
        print(f'❌ Health Check Error: {error}')
        return None

def multimodal_example():
    """Demonstrate multimodal capabilities"""
    print('\n🎭 Multimodal Example')
    print('=' * 40)
    
    client = NexusAIClient('https://nexus.bits-innovate.com')
    
    try:
        # Create multimodal agent
        config = AgentConfig(
            instructions="You are a multimodal AI assistant that can process text, voice, and images for African users.",
            capabilities=["text", "voice", "vision"],
            custom_settings={
                "supports_local_languages": True,
                "image_analysis": True,
                "voice_synthesis": True
            }
        )
        
        agent = client.create_agent(config)
        print(f'✅ Created Multimodal Agent: {agent["agent_id"]}')
        
        # Use the session from agent creation
        session_id = agent["session_id"]
        print(f'✅ Created Multimodal Session: {session_id}')
        
        # Text message
        text_response = client.send_message(
            session_id,
            "I will send you an image of a document. Please help me understand what it says."
        )
        
        print(f'🤖 Text Response: {text_response["message"]}')
        
        # Note: In real usage, you would send actual audio/image data
        print('📷 Image analysis capabilities available')
        print('🎤 Voice message capabilities available')
        print('🗣️ Text-to-speech synthesis available')
        
        return agent, {"session_id": session_id}
        
    except Exception as error:
        print(f'❌ Multimodal Error: {error}')
        return None, None

def main():
    """Run all examples"""
    print('🚀 NexusAI Python SDK - Examples')
    print('=' * 35)
    print('🌍 Built for the African Market')
    print('🔗 API: https://nexus.bits-innovate.com')
    
    # Run examples
    health_check_example()
    language_learning_example()
    emergency_services_example()
    business_chatbot_example()
    multimodal_example()
    
    print('\n✨ All examples completed!')
    print('📚 Check README.md for more documentation')
    print('🤝 Support: hello@bits-innovate.com')

if __name__ == "__main__":
    main()
