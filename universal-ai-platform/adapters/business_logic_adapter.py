"""
Business Logic Adapter Framework
Allows customization of agent behavior for different use cases
"""

import importlib
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from livekit.agents import ChatContext
from livekit import rtc

logger = logging.getLogger(__name__)

class BusinessLogicAdapter(ABC):
    """Abstract base class for business logic adapters"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @abstractmethod
    async def on_agent_enter(self, agent, room: rtc.Room):
        """Called when agent enters a room"""
        pass
    
    @abstractmethod
    async def process_image(self, image_bytes: bytes, chat_ctx: ChatContext) -> Optional[List[Any]]:
        """Process uploaded image - return content to add to chat or None for default processing"""
        pass
    
    @abstractmethod
    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: dict):
        """Called when user completes a turn"""
        pass
    
    @abstractmethod
    async def process_text_input(self, text: str, chat_ctx: ChatContext) -> Optional[str]:
        """Process text input - return modified text or None for default processing"""
        pass
    
    # New multimodal methods
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice settings for TTS output - override in subclasses"""
        return {
            "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",  # Default voice
            "model": "sonic-english",
            "output_format": "pcm_16000",
            "speed": 1.0,
            "emotion": "neutral"
        }
    
    def get_vision_instructions(self) -> str:
        """Get vision analysis instructions - override in subclasses"""
        return "Analyze this image and provide a detailed description of what you see."
    
    async def process_realtime_event(self, event: Dict[str, Any]) -> Optional[str]:
        """Process real-time events (voice, video, etc.) - override in subclasses"""
        return None
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get conversation context for real-time sessions - override in subclasses"""
        return {
            "domain": "general",
            "interaction_style": "helpful",
            "response_length": "medium"
        }
    
    @staticmethod
    def load(adapter_name: str) -> 'BusinessLogicAdapter':
        """Load adapter by name"""
        try:
            module_path = f"adapters.{adapter_name}"
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, f"{adapter_name.title()}Adapter")
            return adapter_class()
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load adapter {adapter_name}: {e}")
            return DefaultAdapter()

class DefaultAdapter(BusinessLogicAdapter):
    """Default adapter with no special processing"""
    
    async def on_agent_enter(self, agent, room: rtc.Room):
        logger.info(f"Agent {agent.config.agent_id} entered room {room.name}")
    
    async def process_image(self, image_bytes: bytes, chat_ctx: ChatContext) -> Optional[List[Any]]:
        return None  # Use default processing
    
    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: dict):
        pass  # No special processing
    
    async def process_text_input(self, text: str, chat_ctx: ChatContext) -> Optional[str]:
        return None  # Use original text
    
    # Default implementations for multimodal methods
    def get_voice_settings(self) -> Dict[str, Any]:
        return super().get_voice_settings()  # Use base defaults
    
    def get_vision_instructions(self) -> str:
        return super().get_vision_instructions()  # Use base defaults
    
    async def process_realtime_event(self, event: Dict[str, Any]) -> Optional[str]:
        return None  # No special real-time processing
    
    def get_conversation_context(self) -> Dict[str, Any]:
        return super().get_conversation_context()  # Use base defaults