"""
Service Configuration Framework
Allows developers to control which AI services to use through business adapters
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
import json

class AIModel(Enum):
    """Available AI models with cost tiers"""
    # GPT Models (OpenAI)
    GPT_4O_MINI = "gpt-4o-mini"      # 1 credit per 1K tokens
    GPT_4O = "gpt-4o"                # 8 credits per 1K tokens
    GPT_4 = "gpt-4"                  # 25 credits per 1K tokens
    
    # Claude Models (Anthropic)
    CLAUDE_3_HAIKU = "claude-3-haiku"     # 1 credit per 1K tokens
    CLAUDE_3_SONNET = "claude-3-sonnet"   # 12 credits per 1K tokens
    
    # Vision Models
    GPT_4_VISION = "gpt-4-vision"         # 50 credits per image
    CLAUDE_3_VISION = "claude-3-vision"   # 40 credits per image

class VoiceProvider(Enum):
    """Voice service providers"""
    CARTESIA = "cartesia"            # 0.0008 credits per char (Primary TTS)
    OPENAI_TTS = "openai-tts"        # 0.001 credits per char (Backup TTS)
    DEEPGRAM = "deepgram"            # 8 credits per minute (Primary STT)
    OPENAI_WHISPER = "openai-whisper"    # 10 credits per minute (Backup STT)

class PhoneProvider(Enum):
    """Phone service providers"""
    TWILIO = "twilio"                # 20 credits per minute
    TWILIO_INTERNATIONAL = "twilio-intl"  # 35 credits per minute

@dataclass
class ServiceConfiguration:
    """Configuration for AI services in a business adapter"""
    
    # Text AI Model Selection
    primary_ai_model: AIModel = AIModel.GPT_4O_MINI
    fallback_ai_model: Optional[AIModel] = None
    
    # Voice Services
    tts_provider: VoiceProvider = VoiceProvider.CARTESIA
    stt_provider: VoiceProvider = VoiceProvider.DEEPGRAM
    voice_enabled: bool = False
    
    # Vision Services
    vision_model: AIModel = AIModel.GPT_4_VISION
    vision_enabled: bool = False
    
    # Phone Services
    phone_provider: PhoneProvider = PhoneProvider.TWILIO
    phone_enabled: bool = False
    
    # Real-time Services
    realtime_enabled: bool = False
    
    # Cost Control
    max_credits_per_request: Optional[int] = None
    max_credits_per_minute: Optional[int] = None
    cost_optimization: bool = True  # Auto-select cheaper models when possible
    
    # Service Priorities (when multiple options available)
    service_priorities: Dict[str, str] = None  # e.g., {"accuracy": "high", "cost": "low"}
    
    def __post_init__(self):
        if self.service_priorities is None:
            self.service_priorities = {"cost": "medium", "accuracy": "medium", "speed": "high"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Convert enums to string values
        for key, value in result.items():
            if isinstance(value, Enum):
                result[key] = value.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceConfiguration':
        """Create from dictionary"""
        # Convert string values back to enums
        if 'primary_ai_model' in data:
            data['primary_ai_model'] = AIModel(data['primary_ai_model'])
        if 'fallback_ai_model' in data and data['fallback_ai_model']:
            data['fallback_ai_model'] = AIModel(data['fallback_ai_model'])
        if 'tts_provider' in data:
            data['tts_provider'] = VoiceProvider(data['tts_provider'])
        if 'stt_provider' in data:
            data['stt_provider'] = VoiceProvider(data['stt_provider'])
        if 'vision_model' in data:
            data['vision_model'] = AIModel(data['vision_model'])
        if 'phone_provider' in data:
            data['phone_provider'] = PhoneProvider(data['phone_provider'])
            
        return cls(**data)

class ServiceSelector:
    """Intelligent service selection based on configuration and context"""
    
    @staticmethod
    def select_ai_model(config: ServiceConfiguration, context: Dict[str, Any]) -> AIModel:
        """Select the best AI model based on configuration and context"""
        
        # Check cost optimization
        if config.cost_optimization:
            request_complexity = context.get('complexity', 'medium')
            
            # For simple requests, use cheaper models
            if request_complexity == 'low':
                if config.primary_ai_model in [AIModel.GPT_4, AIModel.CLAUDE_3_SONNET]:
                    return AIModel.GPT_4O_MINI  # Auto-downgrade for cost
        
        # Check credit limits
        if config.max_credits_per_request:
            estimated_tokens = context.get('estimated_tokens', 1000)
            model_costs = {
                AIModel.GPT_4O_MINI: 1,
                AIModel.GPT_4O: 8,
                AIModel.GPT_4: 25,
                AIModel.CLAUDE_3_HAIKU: 1,
                AIModel.CLAUDE_3_SONNET: 12
            }
            
            estimated_credits = (estimated_tokens / 1000) * model_costs.get(config.primary_ai_model, 1)
            
            if estimated_credits > config.max_credits_per_request:
                # Find cheaper alternative
                for model, cost in sorted(model_costs.items(), key=lambda x: x[1]):
                    if (estimated_tokens / 1000) * cost <= config.max_credits_per_request:
                        return model
        
        return config.primary_ai_model
    
    @staticmethod
    def select_voice_provider(config: ServiceConfiguration, service_type: str, context: Dict[str, Any]) -> VoiceProvider:
        """Select voice provider based on configuration and context"""
        
        if service_type == "tts":
            # Consider voice quality requirements
            quality_requirement = context.get('voice_quality', 'standard')
            if quality_requirement == 'premium' and not config.cost_optimization:
                return VoiceProvider.CARTESIA  # Premium TTS with high quality
            return config.tts_provider
        
        elif service_type == "stt":
            # Consider accuracy requirements
            accuracy_requirement = context.get('accuracy_requirement', 'standard')
            if accuracy_requirement == 'high' and not config.cost_optimization:
                return VoiceProvider.OPENAI_WHISPER
            return config.stt_provider
        
        return config.stt_provider
    
    @staticmethod
    def estimate_workflow_cost(config: ServiceConfiguration, workflow_description: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate cost for a multi-service workflow"""
        
        estimated_cost = {
            "total_credits": 0,
            "total_cost_usd": 0.0,
            "service_breakdown": [],
            "warnings": []
        }
        
        # AI model costs
        if workflow_description.get('ai_tokens'):
            model = ServiceSelector.select_ai_model(config, workflow_description)
            model_costs = {
                AIModel.GPT_4O_MINI: (1, 0.00015),
                AIModel.GPT_4O: (8, 0.0025),
                AIModel.GPT_4: (25, 0.03),
                AIModel.CLAUDE_3_HAIKU: (1, 0.00025),
                AIModel.CLAUDE_3_SONNET: (12, 0.003)
            }
            
            credits_per_1k, cost_per_1k = model_costs.get(model, (1, 0.001))
            tokens = workflow_description['ai_tokens']
            
            ai_credits = max(1, int((tokens / 1000) * credits_per_1k))
            ai_cost = (tokens / 1000) * cost_per_1k
            
            estimated_cost["total_credits"] += ai_credits
            estimated_cost["total_cost_usd"] += ai_cost
            estimated_cost["service_breakdown"].append({
                "service": "AI Model",
                "provider": model.value,
                "credits": ai_credits,
                "cost_usd": ai_cost
            })
        
        # Voice services
        if workflow_description.get('voice_minutes') and config.voice_enabled:
            minutes = workflow_description['voice_minutes']
            
            # STT cost
            stt_credits = max(1, int(minutes * 10))  # 10 credits per minute average
            stt_cost = minutes * 0.006
            
            # TTS cost (estimated 150 chars per minute of speech)
            chars = int(minutes * 150)
            tts_credits = max(1, int(chars * 0.001))
            tts_cost = chars * 0.000015
            
            voice_credits = stt_credits + tts_credits
            voice_cost = stt_cost + tts_cost
            
            estimated_cost["total_credits"] += voice_credits
            estimated_cost["total_cost_usd"] += voice_cost
            estimated_cost["service_breakdown"].append({
                "service": "Voice Processing",
                "provider": f"{config.stt_provider.value} + {config.tts_provider.value}",
                "credits": voice_credits,
                "cost_usd": voice_cost
            })
        
        # Phone services
        if workflow_description.get('phone_minutes') and config.phone_enabled:
            minutes = workflow_description['phone_minutes']
            phone_credits = max(1, int(minutes * 20))  # 20 credits per minute
            phone_cost = minutes * 0.0085
            
            estimated_cost["total_credits"] += phone_credits
            estimated_cost["total_cost_usd"] += phone_cost
            estimated_cost["service_breakdown"].append({
                "service": "Phone Service",
                "provider": config.phone_provider.value,
                "credits": phone_credits,
                "cost_usd": phone_cost
            })
        
        # Vision services
        if workflow_description.get('image_count') and config.vision_enabled:
            images = workflow_description['image_count']
            vision_credits = images * 50  # 50 credits per image
            vision_cost = images * 0.01
            
            estimated_cost["total_credits"] += vision_credits
            estimated_cost["total_cost_usd"] += vision_cost
            estimated_cost["service_breakdown"].append({
                "service": "Vision Analysis",
                "provider": config.vision_model.value,
                "credits": vision_credits,
                "cost_usd": vision_cost
            })
        
        # Add warnings for high costs
        if estimated_cost["total_credits"] > 100:
            estimated_cost["warnings"].append("High credit usage expected (>100 credits)")
        
        if config.max_credits_per_request and estimated_cost["total_credits"] > config.max_credits_per_request:
            estimated_cost["warnings"].append(f"Exceeds max credits per request ({config.max_credits_per_request})")
        
        return estimated_cost

# Pre-defined service configurations for common use cases
class ServicePresets:
    """Pre-configured service settings for common business needs"""
    
    @staticmethod
    def cost_optimized() -> ServiceConfiguration:
        """Minimum cost configuration"""
        return ServiceConfiguration(
            primary_ai_model=AIModel.GPT_4O_MINI,
            tts_provider=VoiceProvider.CARTESIA,
            stt_provider=VoiceProvider.DEEPGRAM,
            vision_model=AIModel.GPT_4O_VISION,
            phone_provider=PhoneProvider.TWILIO,
            cost_optimization=True,
            max_credits_per_request=50,
            service_priorities={"cost": "high", "accuracy": "medium", "speed": "medium"}
        )
    
    @staticmethod
    def premium_quality() -> ServiceConfiguration:
        """High quality, higher cost configuration"""
        return ServiceConfiguration(
            primary_ai_model=AIModel.GPT_4,
            fallback_ai_model=AIModel.GPT_4O,
            tts_provider=VoiceProvider.CARTESIA,
            stt_provider=VoiceProvider.OPENAI_WHISPER,
            vision_model=AIModel.GPT_4_VISION,
            phone_provider=PhoneProvider.TWILIO,
            cost_optimization=False,
            service_priorities={"cost": "low", "accuracy": "high", "speed": "medium"}
        )
    
    @staticmethod
    def balanced() -> ServiceConfiguration:
        """Balanced cost and quality"""
        return ServiceConfiguration(
            primary_ai_model=AIModel.GPT_4O,
            fallback_ai_model=AIModel.GPT_4O_MINI,
            tts_provider=VoiceProvider.CARTESIA,
            stt_provider=VoiceProvider.DEEPGRAM,
            vision_model=AIModel.GPT_4O_VISION,
            phone_provider=PhoneProvider.TWILIO,
            cost_optimization=True,
            max_credits_per_request=200,
            service_priorities={"cost": "medium", "accuracy": "high", "speed": "high"}
        )
    
    @staticmethod
    def emergency_services() -> ServiceConfiguration:
        """Configuration for emergency/critical services - prioritizes accuracy and speed"""
        return ServiceConfiguration(
            primary_ai_model=AIModel.GPT_4O,
            fallback_ai_model=AIModel.GPT_4,
            tts_provider=VoiceProvider.CARTESIA,  # Fast and reliable
            stt_provider=VoiceProvider.OPENAI_WHISPER,  # High accuracy
            vision_model=AIModel.GPT_4_VISION,
            phone_provider=PhoneProvider.TWILIO,
            voice_enabled=True,
            vision_enabled=True,
            phone_enabled=True,
            realtime_enabled=True,
            cost_optimization=False,  # Don't optimize cost for emergencies
            service_priorities={"cost": "low", "accuracy": "high", "speed": "high"}
        )
    
    @staticmethod
    def language_learning() -> ServiceConfiguration:
        """Configuration for language learning - needs good voice and reasonable cost"""
        return ServiceConfiguration(
            primary_ai_model=AIModel.GPT_4O_MINI,
            fallback_ai_model=AIModel.GPT_4O,
            tts_provider=VoiceProvider.CARTESIA,  # High-quality voice for pronunciation
            stt_provider=VoiceProvider.OPENAI_WHISPER,  # Good accuracy for language detection
            vision_model=AIModel.CLAUDE_3_VISION,
            phone_provider=PhoneProvider.TWILIO,
            voice_enabled=True,
            vision_enabled=True,
            phone_enabled=False,
            realtime_enabled=True,
            cost_optimization=True,
            max_credits_per_request=75,
            service_priorities={"cost": "medium", "accuracy": "high", "speed": "medium"}
        )