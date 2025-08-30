"""
NexusAI Python SDK
Official client library for NexusAI - The Universal AI Agent Platform for Africa
https://nexus.bits-innovate.com
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AIModel(Enum):
    """Available AI models with cost tiers"""
    GPT_4O_MINI = "gpt-4o-mini"      # 1 credit per 1K tokens
    GPT_4O = "gpt-4o"                # 8 credits per 1K tokens
    GPT_4 = "gpt-4"                  # 25 credits per 1K tokens
    CLAUDE_3_HAIKU = "claude-3-haiku"     # 1 credit per 1K tokens
    CLAUDE_3_SONNET = "claude-3-sonnet"   # 12 credits per 1K tokens
    GPT_4_VISION = "gpt-4-vision"         # 50 credits per image
    CLAUDE_3_VISION = "claude-3-vision"   # 40 credits per image

class VoiceProvider(Enum):
    """Voice service providers"""
    CARTESIA = "cartesia"            # 0.8 credits per 1K chars (Primary TTS)
    OPENAI_TTS = "openai-tts"        # 1 credit per 1K chars (Backup TTS)
    DEEPGRAM = "deepgram"            # 8 credits per minute (Primary STT)
    OPENAI_WHISPER = "openai-whisper"    # 10 credits per minute (Backup STT)

class PhoneProvider(Enum):
    """Phone service providers"""
    TWILIO = "twilio"                # 20 credits per minute
    TWILIO_INTERNATIONAL = "twilio-intl"  # 35 credits per minute

@dataclass
class ServiceConfiguration:
    """Configuration for AI services"""
    primary_ai_model: str = "gpt-4o-mini"
    fallback_ai_model: Optional[str] = None
    tts_provider: str = "cartesia"
    stt_provider: str = "deepgram"
    voice_enabled: bool = False
    vision_model: str = "gpt-4o-vision"
    vision_enabled: bool = False
    phone_provider: str = "twilio"
    phone_enabled: bool = False
    realtime_enabled: bool = False
    max_credits_per_request: Optional[int] = None
    cost_optimization: bool = True
    service_priorities: Dict[str, str] = None
    
    def __post_init__(self):
        if self.service_priorities is None:
            self.service_priorities = {"cost": "medium", "accuracy": "medium", "speed": "high"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class AgentConfig:
    """Configuration for creating an AI agent"""
    instructions: str
    capabilities: List[str]  # ["voice", "vision", "text"]
    business_logic_adapter: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None
    service_configuration: Optional[ServiceConfiguration] = None
    client_id: Optional[str] = None

@dataclass
class Message:
    """Represents a message in the conversation"""
    id: str
    type: str  # "text", "image", "audio"
    content: str
    timestamp: str
    sender: str  # "user" or "assistant"

class NexusAIClient:
    """Main client for interacting with NexusAI - The Universal AI Agent Platform"""
    
    def __init__(self, api_url: str = "https://nexus.bits-innovate.com", api_key: Optional[str] = None):
        """
        Initialize the NexusAI client
        
        Args:
            api_url: Base URL of the NexusAI API (default: production endpoint)
            api_key: Optional API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "UniversalAI-Python-SDK/1.0.0"
        })
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status
        
        Returns:
            Dictionary with health status information
        """
        try:
            response = self.session.get(f"{self.api_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    def create_agent(self, config: AgentConfig) -> Dict[str, Any]:
        """
        Create a new AI agent session
        
        Args:
            config: Agent configuration
            
        Returns:
            Dictionary with session information
        """
        try:
            custom_settings = config.custom_settings or {}
            
            # Include service configuration in custom settings if provided
            if config.service_configuration:
                custom_settings["service_configuration"] = config.service_configuration.to_dict()
            
            payload = {
                "instructions": config.instructions,
                "capabilities": config.capabilities,
                "business_logic_adapter": config.business_logic_adapter,
                "custom_settings": custom_settings,
                "client_id": config.client_id
            }
            
            response = self.session.post(
                f"{self.api_url}/api/v1/agent/create",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to create agent: {e}")
            raise Exception(f"Failed to create agent: {e}")
    
    def create_session(self, config: AgentConfig) -> Dict[str, Any]:
        """
        Create a new session (alias for create_agent for backwards compatibility)
        
        Args:
            config: Session configuration
            
        Returns:
            Dictionary with session information
        """
        return self.create_agent(config)
    
    def send_message(self, session_id: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Send a message to an agent session
        
        Args:
            session_id: Agent session ID
            message: Message content
            message_type: Type of message ("text", "image", "audio")
            
        Returns:
            Response from the API
        """
        try:
            payload = {
                "message": message,
                "type": message_type
            }
            
            response = self.session.post(
                f"{self.api_url}/api/v1/agent/{session_id}/message",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            raise Exception(f"Failed to send message: {e}")
    
    def get_messages(self, session_id: str) -> List[Message]:
        """
        Get messages from an agent session
        
        Args:
            session_id: Agent session ID
            
        Returns:
            List of messages
        """
        try:
            response = self.session.get(
                f"{self.api_url}/api/v1/agent/{session_id}/messages"
            )
            response.raise_for_status()
            
            data = response.json()
            messages = []
            
            for msg_data in data.get("messages", []):
                messages.append(Message(
                    id=msg_data["id"],
                    type=msg_data["type"],
                    content=msg_data["content"],
                    timestamp=msg_data["timestamp"],
                    sender=msg_data["sender"]
                ))
            
            return messages
            
        except requests.RequestException as e:
            logger.error(f"Failed to get messages: {e}")
            raise Exception(f"Failed to get messages: {e}")
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get status of an agent session
        
        Args:
            session_id: Agent session ID
            
        Returns:
            Session status information
        """
        try:
            response = self.session.get(
                f"{self.api_url}/api/v1/agent/{session_id}/status"
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to get session status: {e}")
            raise Exception(f"Failed to get session status: {e}")
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Delete an agent session
        
        Args:
            session_id: Agent session ID
            
        Returns:
            Deletion confirmation
        """
        try:
            response = self.session.delete(
                f"{self.api_url}/api/v1/agent/{session_id}"
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to delete session: {e}")
            raise Exception(f"Failed to delete session: {e}")
    
    def get_usage_summary(self, client_id: str, start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get usage summary for billing
        
        Args:
            client_id: Client identifier
            start_date: Start date for usage period
            end_date: End date for usage period
            
        Returns:
            Usage summary
        """
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            
            response = self.session.get(
                f"{self.api_url}/api/v1/usage/{client_id}",
                params=params
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to get usage summary: {e}")
            raise Exception(f"Failed to get usage summary: {e}")
    
    def get_billing_info(self, client_id: str,
                        start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get credit-based billing information
        
        Args:
            client_id: Client identifier
            start_date: Start date for billing period
            end_date: End date for billing period
        Returns:
            Billing information (credit usage)
        """
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            
            response = self.session.get(
                f"{self.api_url}/api/v1/billing/{client_id}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get billing info: {e}")
            raise Exception(f"Failed to get billing info: {e}")
    
    def estimate_workflow_cost(self, workflow_description: Dict[str, Any], 
                              service_config: Optional[ServiceConfiguration] = None) -> Dict[str, Any]:
        """
        Estimate cost for a multi-service workflow
        
        Args:
            workflow_description: Description of expected usage
            service_config: Service configuration to use for estimates
            
        Returns:
            Cost estimation breakdown
        """
        if not service_config:
            service_config = ServiceConfiguration()
        
        estimated_cost = {
            "total_credits": 0,
            "total_cost_usd": 0.0,
            "service_breakdown": [],
            "warnings": []
        }
        
        # AI model costs
        if workflow_description.get('ai_tokens'):
            model_costs = {
                "gpt-4o-mini": (1, 0.00015),
                "gpt-4o": (8, 0.0025),
                "gpt-4": (25, 0.03),
                "claude-3-haiku": (1, 0.00025),
                "claude-3-sonnet": (12, 0.003)
            }
            
            credits_per_1k, cost_per_1k = model_costs.get(service_config.primary_ai_model, (1, 0.001))
            tokens = workflow_description['ai_tokens']
            
            ai_credits = max(1, int((tokens / 1000) * credits_per_1k))
            ai_cost = (tokens / 1000) * cost_per_1k
            
            estimated_cost["total_credits"] += ai_credits
            estimated_cost["total_cost_usd"] += ai_cost
            estimated_cost["service_breakdown"].append({
                "service": "AI Model",
                "provider": service_config.primary_ai_model,
                "credits": ai_credits,
                "cost_usd": ai_cost
            })
        
        # Voice services
        if workflow_description.get('voice_minutes') and service_config.voice_enabled:
            minutes = workflow_description['voice_minutes']
            
            # STT cost (Deepgram: 8 credits/min, Whisper: 10 credits/min)
            stt_credits = 8 if service_config.stt_provider == "deepgram" else 10
            stt_credits = max(1, int(minutes * stt_credits))
            stt_cost = minutes * (0.0043 if service_config.stt_provider == "deepgram" else 0.006)
            
            # TTS cost (Cartesia: 0.8 credits/1K chars, OpenAI: 1 credit/1K chars)
            chars = int(minutes * 150)  # Estimate 150 chars per minute of speech
            tts_rate = 0.8 if service_config.tts_provider == "cartesia" else 1.0
            tts_credits = max(1, int((chars / 1000) * tts_rate))
            tts_cost = chars * (0.000011 if service_config.tts_provider == "cartesia" else 0.000015)
            
            voice_credits = stt_credits + tts_credits
            voice_cost = stt_cost + tts_cost
            
            estimated_cost["total_credits"] += voice_credits
            estimated_cost["total_cost_usd"] += voice_cost
            estimated_cost["service_breakdown"].append({
                "service": "Voice Processing",
                "provider": f"{service_config.stt_provider} + {service_config.tts_provider}",
                "credits": voice_credits,
                "cost_usd": voice_cost
            })
        
        # Phone services
        if workflow_description.get('phone_minutes') and service_config.phone_enabled:
            minutes = workflow_description['phone_minutes']
            phone_credits = max(1, int(minutes * (20 if service_config.phone_provider == "twilio" else 35)))
            phone_cost = minutes * (0.0085 if service_config.phone_provider == "twilio" else 0.015)
            
            estimated_cost["total_credits"] += phone_credits
            estimated_cost["total_cost_usd"] += phone_cost
            estimated_cost["service_breakdown"].append({
                "service": "Phone Service",
                "provider": service_config.phone_provider,
                "credits": phone_credits,
                "cost_usd": phone_cost
            })
        
        # Vision services
        if workflow_description.get('image_count') and service_config.vision_enabled:
            images = workflow_description['image_count']
            vision_credits = images * (40 if "gpt-4o" in service_config.vision_model else 50)
            vision_cost = images * (0.008 if "gpt-4o" in service_config.vision_model else 0.01)
            
            estimated_cost["total_credits"] += vision_credits
            estimated_cost["total_cost_usd"] += vision_cost
            estimated_cost["service_breakdown"].append({
                "service": "Vision Analysis",
                "provider": service_config.vision_model,
                "credits": vision_credits,
                "cost_usd": vision_cost
            })
        
        # Add warnings for high costs
        if estimated_cost["total_credits"] > 100:
            estimated_cost["warnings"].append("High credit usage expected (>100 credits)")
        
        if service_config.max_credits_per_request and estimated_cost["total_credits"] > service_config.max_credits_per_request:
            estimated_cost["warnings"].append(f"Exceeds max credits per request ({service_config.max_credits_per_request})")
        
        return estimated_cost
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active agent sessions
        
        Returns:
            List of active sessions
        """
        try:
            response = self.session.get(
                f"{self.api_url}/api/v1/agents"
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("sessions", [])
            
        except requests.RequestException as e:
            logger.error(f"Failed to list sessions: {e}")
            raise Exception(f"Failed to list sessions: {e}")

class AgentSession:
    """High-level wrapper for managing an agent session"""
    
    def __init__(self, client: NexusAIClient, session_id: str):
        """
        Initialize agent session
        
        Args:
            client: UniversalAI client instance
            session_id: Session ID from create_agent
        """
        self.client = client
        self.session_id = session_id
        self._messages: List[Message] = []
    
    def send_message(self, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Send a message to the agent"""
        return self.client.send_message(self.session_id, message, message_type)
    
    def get_new_messages(self) -> List[Message]:
        """Get new messages since last call"""
        all_messages = self.client.get_messages(self.session_id)
        
        # Filter out messages we already have
        known_ids = {msg.id for msg in self._messages}
        new_messages = [msg for msg in all_messages if msg.id not in known_ids]
        
        # Update our message list
        self._messages.extend(new_messages)
        
        return new_messages
    
    def get_all_messages(self) -> List[Message]:
        """Get all messages in the session"""
        self._messages = self.client.get_messages(self.session_id)
        return self._messages
    
    def get_history(self, limit: Optional[int] = None) -> List[Message]:
        """
        Get message history (alias for get_all_messages)
        
        Args:
            limit: Maximum number of messages to return (optional)
            
        Returns:
            List of messages (limited if specified)
        """
        messages = self.get_all_messages()
        return messages[-limit:] if limit else messages
    
    def get_status(self) -> Dict[str, Any]:
        """Get session status"""
        return self.client.get_session_status(self.session_id)
    
    def close(self) -> Dict[str, Any]:
        """Close the session"""
        return self.client.delete_session(self.session_id)
    
    def wait_for_response(self, timeout: int = 30, poll_interval: float = 0.5) -> Optional[Message]:
        """
        Wait for a response from the agent
        
        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check for new messages
            
        Returns:
            The first new assistant message, or None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            new_messages = self.get_new_messages()
            
            # Look for assistant messages
            for message in new_messages:
                if message.sender == "assistant":
                    return message
            
            time.sleep(poll_interval)
        
        return None

# Pre-configured service configurations
class ServicePresets:
    """Pre-configured service settings for common business needs"""
    
    @staticmethod
    def cost_optimized() -> ServiceConfiguration:
        """Minimum cost configuration"""
        return ServiceConfiguration(
            primary_ai_model="gpt-4o-mini",
            tts_provider="cartesia",
            stt_provider="deepgram",
            vision_model="gpt-4o-vision",
            phone_provider="twilio",
            cost_optimization=True,
            max_credits_per_request=50,
            service_priorities={"cost": "high", "accuracy": "medium", "speed": "medium"}
        )
    
    @staticmethod
    def premium_quality() -> ServiceConfiguration:
        """High quality, higher cost configuration"""
        return ServiceConfiguration(
            primary_ai_model="gpt-4",
            fallback_ai_model="gpt-4o",
            tts_provider="cartesia",
            stt_provider="openai-whisper",
            vision_model="gpt-4-vision",
            phone_provider="twilio",
            cost_optimization=False,
            service_priorities={"cost": "low", "accuracy": "high", "speed": "medium"}
        )
    
    @staticmethod
    def balanced() -> ServiceConfiguration:
        """Balanced cost and quality"""
        return ServiceConfiguration(
            primary_ai_model="gpt-4o",
            fallback_ai_model="gpt-4o-mini",
            tts_provider="cartesia",
            stt_provider="deepgram",
            vision_model="gpt-4o-vision",
            phone_provider="twilio",
            cost_optimization=True,
            max_credits_per_request=200,
            service_priorities={"cost": "medium", "accuracy": "high", "speed": "high"}
        )
    
    @staticmethod
    def emergency_services() -> ServiceConfiguration:
        """Configuration for emergency/critical services - prioritizes accuracy and speed"""
        return ServiceConfiguration(
            primary_ai_model="gpt-4o",
            fallback_ai_model="gpt-4",
            tts_provider="cartesia",
            stt_provider="openai-whisper",
            vision_model="gpt-4-vision",
            phone_provider="twilio",
            voice_enabled=True,
            vision_enabled=True,
            phone_enabled=True,
            realtime_enabled=True,
            cost_optimization=False,
            service_priorities={"cost": "low", "accuracy": "high", "speed": "high"}
        )

# Convenience function for simple use cases
def create_simple_agent(api_url: str = "https://nexus.bits-innovate.com", 
                       api_key: Optional[str] = None,
                       instructions: str = "", 
                       capabilities: List[str] = None,
                       service_preset: str = "cost_optimized") -> tuple:
    """
    Create a simple agent session with minimal configuration
    
    Args:
        api_url: API URL
        api_key: API key for authentication
        instructions: Instructions for the agent
        capabilities: List of capabilities (defaults to ["text"])
        service_preset: Service configuration preset ("cost_optimized", "premium_quality", "balanced", "emergency_services")
        
    Returns:
        Tuple of (client, agent_info, session)
    """
    if capabilities is None:
        capabilities = ["text"]
    
    # Get service configuration preset
    service_config = None
    if service_preset == "premium_quality":
        service_config = ServicePresets.premium_quality()
    elif service_preset == "balanced":
        service_config = ServicePresets.balanced()
    elif service_preset == "emergency_services":
        service_config = ServicePresets.emergency_services()
    else:
        service_config = ServicePresets.cost_optimized()
    
    client = NexusAIClient(api_url, api_key)
    config = AgentConfig(
        instructions=instructions,
        capabilities=capabilities,
        service_configuration=service_config
    )
    
    result = client.create_agent(config)
    session_id = result["session_id"]
    session = AgentSession(client, session_id)
    
    return client, {"id": result["agent_id"]}, session

# Convenience functions for specific use cases
def create_emergency_agent(api_url: str = "https://nexus.bits-innovate.com", 
                          api_key: Optional[str] = None,
                          emergency_type: str = "medical") -> tuple:
    """Create an emergency services agent with optimal configuration"""
    return create_simple_agent(
        api_url=api_url,
        api_key=api_key,
        instructions=f"You are an emergency {emergency_type} assistant. Prioritize accuracy and clear communication.",
        capabilities=["text", "voice", "phone"],
        service_preset="emergency_services"
    )

def create_learning_agent(api_url: str = "https://nexus.bits-innovate.com", 
                         api_key: Optional[str] = None,
                         subject: str = "general") -> tuple:
    """Create a language learning agent with cost-optimized configuration"""
    return create_simple_agent(
        api_url=api_url,
        api_key=api_key,
        instructions=f"You are a {subject} tutor. Provide clear, educational responses with examples.",
        capabilities=["text", "voice"],
        service_preset="cost_optimized"
    )