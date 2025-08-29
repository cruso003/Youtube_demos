"""
Emergency Services Business Logic Adapter
Customizes agent behavior for emergency response applications
"""

import logging
from typing import Any, Dict, List, Optional
from livekit.agents import ChatContext
from livekit.agents.llm import ImageContent
from livekit import rtc
import base64
import json

from .business_logic_adapter import BusinessLogicAdapter

logger = logging.getLogger(__name__)

class EmergencyservicesAdapter(BusinessLogicAdapter):
    """Adapter for emergency services applications"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.emergency_types = config.get("emergency_types", [
            "medical", "fire", "police", "natural_disaster"
        ]) if config else ["medical", "fire", "police", "natural_disaster"]
        self.location_required = config.get("location_required", True) if config else True
        self.escalation_keywords = config.get("escalation_keywords", [
            "unconscious", "bleeding", "fire", "break-in", "assault", "chest pain", "breathing"
        ]) if config else ["unconscious", "bleeding", "fire", "break-in", "assault", "chest pain", "breathing"]
    
    def get_system_instructions(self) -> str:
        """Get system instructions for emergency services"""
        return f"""You are a professional emergency services dispatcher. Your role is to:

        COLLECT CRITICAL INFORMATION:
        - What is the emergency?
        - Where is the emergency? (exact address)
        - Who is involved and are they injured?
        - Is anyone in immediate danger?
        - What services are needed (police, fire, medical)?

        MAINTAIN CALM PROFESSIONALISM:
        - Speak clearly and calmly
        - Ask one question at a time
        - Confirm critical information by repeating it back
        - Keep caller on the line until help arrives
        - Never hang up first

        ESCALATION KEYWORDS: {', '.join(self.escalation_keywords)}
        
        Always begin by asking: "What is your emergency?" and gather information systematically.
        If caller mentions any escalation keywords, immediately prioritize and dispatch services.
        """
    
    async def on_agent_enter(self, agent, room: rtc.Room):
        """Initialize emergency services session"""
        logger.info(f"Emergency services session started in room {room.name}")
        
        # Update agent instructions for emergency response
        agent.instructions = f"""You are an emergency services AI assistant. Your role is to:

        CRITICAL PRIORITIES:
        1. Stay CALM and reassuring
        2. Quickly assess the emergency type and severity
        3. Collect essential information: WHAT, WHERE, WHO, WHEN
        4. Provide immediate safety instructions if needed
        5. Guide the caller through necessary steps while help is on the way

        INFORMATION TO COLLECT:
        - Type of emergency: {', '.join(self.emergency_types)}
        - Exact location (address, landmarks, GPS coordinates if available)
        - Number of people involved
        - Current condition of anyone injured
        - Immediate dangers present

        ESCALATION TRIGGERS:
        - Keywords: {', '.join(self.escalation_keywords)}
        - Life-threatening situations
        - Active ongoing danger

        RESPONSE GUIDELINES:
        - Ask ONE clear question at a time
        - Speak clearly and slowly
        - Confirm critical information by repeating it back
        - Never hang up first
        - Keep the caller on the line until help arrives
        
        Begin by asking: "What is your emergency?" and listen carefully.
        """
        
        # Set emergency context
        agent.emergency_context = {
            "emergency_type": None,
            "location": None,
            "severity": "unknown",
            "people_involved": 0,
            "critical_info_collected": False,
            "escalated": False
        }
    
    async def process_image(self, image_bytes: bytes, chat_ctx: ChatContext) -> Optional[List[Any]]:
        """Process images for emergency assessment"""
        return [
            "I can see the image you've shared. This may help me better understand your emergency situation. Please continue to describe what's happening while I analyze this image.",
            ImageContent(
                image=f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
            ),
            "\n[EMERGENCY CONTEXT: Image received - analyze for emergency indicators, injuries, hazards, or location clues. Prioritize immediate safety assessment.]"
        ]
    
    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: dict):
        """Handle completed user turn in emergency context"""
        content = new_message.get('content', '')
        
        if isinstance(content, str):
            # Check for escalation keywords
            escalation_detected = any(keyword.lower() in content.lower() for keyword in self.escalation_keywords)
            
            # Extract potential location information
            location_indicators = self._extract_location_info(content)
            
            # Check for emergency type
            emergency_type = self._identify_emergency_type(content)
            
            # Add emergency analysis context
            emergency_analysis = {
                "escalation_detected": escalation_detected,
                "location_indicators": location_indicators,
                "emergency_type": emergency_type,
                "timestamp": "current"
            }
            
            analysis_prompt = f"\n\n[EMERGENCY ANALYSIS: {json.dumps(emergency_analysis)}]"
            
            if escalation_detected:
                analysis_prompt += "\n[PRIORITY: HIGH - Escalation keywords detected. Immediate action may be required.]"
            
            new_message['content'] = content + analysis_prompt
    
    async def process_text_input(self, text: str, chat_ctx: ChatContext) -> Optional[str]:
        """Process text input for emergency context"""
        # Add emergency service context and urgency
        processed_text = f"[EMERGENCY CALL] {text}"
        return processed_text
    
    def _extract_location_info(self, text: str) -> List[str]:
        """Extract potential location information from text"""
        location_indicators = []
        text_lower = text.lower()
        
        # Address patterns
        if any(word in text_lower for word in ['street', 'avenue', 'road', 'drive', 'boulevard']):
            location_indicators.append("street_address_mentioned")
        
        # Landmark patterns
        if any(word in text_lower for word in ['hospital', 'school', 'park', 'mall', 'store', 'restaurant']):
            location_indicators.append("landmark_mentioned")
        
        # Indoor location patterns
        if any(word in text_lower for word in ['apartment', 'room', 'floor', 'basement', 'kitchen', 'bathroom']):
            location_indicators.append("indoor_location_mentioned")
        
        # Transportation
        if any(word in text_lower for word in ['highway', 'freeway', 'bridge', 'tunnel', 'intersection']):
            location_indicators.append("transportation_location_mentioned")
        
        return location_indicators
    
    def _identify_emergency_type(self, text: str) -> Optional[str]:
        """Identify the type of emergency from text"""
        text_lower = text.lower()
        
        # Medical emergency indicators
        medical_keywords = ['hurt', 'pain', 'bleeding', 'unconscious', 'breathing', 'heart', 'medical', 'ambulance', 'sick', 'injured']
        if any(keyword in text_lower for keyword in medical_keywords):
            return "medical"
        
        # Fire emergency indicators
        fire_keywords = ['fire', 'smoke', 'burning', 'flames', 'explosion']
        if any(keyword in text_lower for keyword in fire_keywords):
            return "fire"
        
        # Police emergency indicators
        police_keywords = ['robbery', 'theft', 'break', 'assault', 'fight', 'threat', 'suspicious', 'crime']
        if any(keyword in text_lower for keyword in police_keywords):
            return "police"
        
        # Natural disaster indicators
        disaster_keywords = ['flood', 'earthquake', 'tornado', 'hurricane', 'landslide', 'disaster']
        if any(keyword in text_lower for keyword in disaster_keywords):
            return "natural_disaster"
        
        return None
    
    # Multimodal method implementations
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice settings optimized for emergency services"""
        return {
            "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",  # Clear, authoritative voice
            "model": "sonic-english",
            "output_format": "pcm_16000", 
            "speed": 0.95,  # Slightly slower for clarity in emergencies
            "emotion": "calm_authoritative"
        }
    
    def get_vision_instructions(self) -> str:
        """Get vision analysis instructions for emergency assessment"""
        return """Analyze this image for emergency response purposes. Focus on:

        IMMEDIATE SAFETY ASSESSMENT:
        - Visible injuries or medical conditions
        - Fire, smoke, or hazardous materials
        - Structural damage or unsafe conditions
        - Number of people involved and their apparent condition
        - Environmental hazards (water, electrical, chemical)

        LOCATION ANALYSIS:
        - Type of location (residential, commercial, vehicle, outdoor)
        - Access points for emergency responders
        - Obstacles that might impede emergency response
        - Landmarks or identifying features

        EMERGENCY TYPE CLASSIFICATION:
        - Medical emergency indicators
        - Fire/explosion evidence
        - Crime scene indicators
        - Natural disaster effects
        - Traffic/vehicle incidents

        RESPONSE PRIORITIES:
        - Immediate life threats
        - Rescue accessibility
        - Resource requirements (ambulance, fire, police)
        - Special equipment needs

        Provide a structured analysis with clear priorities for emergency response."""
    
    async def process_realtime_event(self, event: Dict[str, Any]) -> Optional[str]:
        """Process real-time events for emergency context"""
        event_type = event.get("type", "")
        
        if event_type == "caller_distress":
            return "I understand this is a stressful situation. Take a deep breath. Help is on the way, and I'm here to guide you through this."
        
        elif event_type == "emergency_escalation":
            return "This situation requires immediate escalation. I'm alerting emergency responders now with high priority."
        
        elif event_type == "location_confirmed":
            return "Thank you for confirming your location. Emergency responders are being dispatched to your exact location."
        
        elif event_type == "injury_reported":
            return "I've noted the injury details. Keep the person still and conscious if possible. Don't move them unless there's immediate danger."
        
        elif event_type == "fire_smoke_detected":
            return "If there's fire or smoke, get to safety immediately. Don't go back for belongings. Fire department is being dispatched."
        
        return None
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get conversation context for emergency services"""
        return {
            "domain": "emergency_services",
            "emergency_types": self.emergency_types,
            "interaction_style": "calm_authoritative",
            "response_length": "short_clear",
            "priority": "life_safety",
            "information_gathering": "systematic",
            "escalation_triggers": self.escalation_keywords,
            "location_priority": True,
            "time_sensitivity": "high",
            "reassurance_level": "high",
            "instruction_clarity": "maximum"
        }