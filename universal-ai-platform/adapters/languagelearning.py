"""
Language Learning Business Logic Adapter
Customizes agent behavior for language learning applications
"""

import logging
from typing import Any, Dict, List, Optional
from livekit.agents import ChatContext
from livekit.agents.llm import ImageContent
from livekit import rtc
import base64

from .business_logic_adapter import BusinessLogicAdapter

logger = logging.getLogger(__name__)

class LanguagelearningAdapter(BusinessLogicAdapter):
    """Adapter for language learning applications"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.target_language = config.get("target_language", "Spanish") if config else "Spanish"
        self.proficiency_level = config.get("proficiency_level", "beginner") if config else "beginner"
        self.conversation_topics = config.get("conversation_topics", [
            "daily activities", "food", "travel", "hobbies"
        ]) if config else ["daily activities", "food", "travel", "hobbies"]
    
    async def on_agent_enter(self, agent, room: rtc.Room):
        """Initialize language learning session"""
        logger.info(f"Language learning session started for {self.target_language} ({self.proficiency_level})")
        
        # Update agent instructions for language learning
        agent.instructions = f"""You are a friendly {self.target_language} language learning assistant. 
        
        Guidelines:
        - Help the user practice {self.target_language} at a {self.proficiency_level} level
        - Encourage conversation in {self.target_language} but be patient with mistakes
        - Provide gentle corrections and explanations
        - Ask engaging questions about: {', '.join(self.conversation_topics)}
        - Use simple vocabulary for beginners, more complex for advanced learners
        - Praise progress and provide encouragement
        - If the user speaks in English, gently encourage them to try in {self.target_language}
        """
    
    async def process_image(self, image_bytes: bytes, chat_ctx: ChatContext) -> Optional[List[Any]]:
        """Process images for language learning context"""
        # For language learning, we want to describe images in the target language
        return [
            f"I can see an image! Let's practice {self.target_language} by describing what we see. Can you tell me what you notice in this picture in {self.target_language}?",
            ImageContent(
                image=f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
            )
        ]
    
    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: dict):
        """Handle completed user turn in language learning context"""
        # Extract the user's message content
        content = new_message.get('content', '')
        
        # Add language learning specific context
        if isinstance(content, str):
            # Check if user is speaking in English when they should practice target language
            if self._is_primarily_english(content) and len(content.split()) > 3:
                # Add coaching prompt for the assistant
                coaching_prompt = f"\n\n[COACHING NOTE: The user spoke in English. Gently encourage them to try expressing this in {self.target_language}. Provide the {self.target_language} translation and ask them to repeat it.]"
                new_message['content'] = content + coaching_prompt
    
    async def process_text_input(self, text: str, chat_ctx: ChatContext) -> Optional[str]:
        """Process text input for language learning"""
        # Add metadata about the learning context
        processed_text = f"[Learning {self.target_language} - {self.proficiency_level} level] {text}"
        return processed_text
    
    def _is_primarily_english(self, text: str) -> bool:
        """Simple heuristic to detect if text is primarily in English"""
        english_words = [
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'from', 'up', 'about', 'into', 'over', 'after', 'this', 'that',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can'
        ]
        
        words = text.lower().split()
        english_count = sum(1 for word in words if word in english_words)
        
        # If more than 40% of words are common English words, assume it's English
        return len(words) > 0 and (english_count / len(words)) > 0.4