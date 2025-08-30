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
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for creating an AI agent"""
    instructions: str
    capabilities: List[str]  # ["voice", "vision", "text"]
    business_logic_adapter: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None
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
            payload = {
                "instructions": config.instructions,
                "capabilities": config.capabilities,
                "business_logic_adapter": config.business_logic_adapter,
                "custom_settings": config.custom_settings or {},
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

# Convenience function for simple use cases
def create_simple_agent(api_url: str = "https://nexus.bits-innovate.com", 
                       instructions: str = "", capabilities: List[str] = None) -> tuple:
    """
    Create a simple agent session with minimal configuration
    
    Args:
        api_url: API URL
        instructions: Instructions for the agent
        capabilities: List of capabilities (defaults to ["text"])
        
    Returns:
        Tuple of (client, agent_info, session)
    """
    if capabilities is None:
        capabilities = ["text"]
    
    client = NexusAIClient(api_url)
    config = AgentConfig(
        instructions=instructions,
        capabilities=capabilities
    )
    
    result = client.create_agent(config)
    session_id = result["session_id"]
    session = AgentSession(client, session_id)
    
    return client, {"id": result["agent_id"]}, session