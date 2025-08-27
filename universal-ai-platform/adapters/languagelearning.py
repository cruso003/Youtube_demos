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
    
    # Multimodal method implementations
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice settings optimized for language learning"""
        # Use a voice that's clear and good for pronunciation practice
        voice_settings = {
            "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",  # Clear, educational voice
            "model": "sonic-english", 
            "output_format": "pcm_16000",
            "speed": 0.9,  # Slightly slower for better comprehension
            "emotion": "encouraging"
        }
        
        # Adjust voice based on target language
        if self.target_language.lower() == "spanish":
            voice_settings["model"] = "sonic-multilingual"
            voice_settings["voice_id"] = "87748186-23bb-4158-a1eb-332911b0b708"  # Spanish voice
        elif self.target_language.lower() == "french":
            voice_settings["model"] = "sonic-multilingual"
            voice_settings["voice_id"] = "95856005-0332-41b0-935f-352e296aa0df"  # French voice
        
        return voice_settings
    
    def get_vision_instructions(self) -> str:
        """Get vision analysis instructions for language learning"""
        return f"""Analyze this image from a language learning perspective for {self.target_language}.

        Please:
        1. Identify any text visible in the image and read it in {self.target_language}
        2. Describe objects, people, and scenes using {self.target_language} vocabulary at a {self.proficiency_level} level
        3. Provide cultural context if the image shows culturally relevant content
        4. Suggest conversation topics or vocabulary practice based on what you see
        5. If there's text in {self.target_language}, explain difficult words and grammar
        6. Offer pronunciation tips for any {self.target_language} words you mention

        Adapt your language complexity to the {self.proficiency_level} proficiency level.
        Be encouraging and focus on learning opportunities."""
    
    async def process_realtime_event(self, event: Dict[str, Any]) -> Optional[str]:
        """Process real-time events for language learning context"""
        event_type = event.get("type", "")
        
        if event_type == "pronunciation_attempt":
            # User is trying to pronounce something
            return f"Great pronunciation practice! Remember to focus on the {self.target_language} sounds we've been working on."
        
        elif event_type == "vocabulary_question":
            # User asking about vocabulary
            return f"That's an excellent {self.target_language} vocabulary question! Let me help you with that."
        
        elif event_type == "grammar_correction":
            # Grammar correction needed
            return "Let me help you with that grammar structure. Don't worry, making mistakes is part of learning!"
        
        return None
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get conversation context for language learning sessions"""
        return {
            "domain": "language_learning",
            "target_language": self.target_language,
            "proficiency_level": self.proficiency_level,
            "conversation_topics": self.conversation_topics,
            "interaction_style": "encouraging_teacher",
            "response_length": "medium",
            "correction_style": "gentle",
            "encouragement_frequency": "high",
            "cultural_context": True,
            "pronunciation_focus": True
        }