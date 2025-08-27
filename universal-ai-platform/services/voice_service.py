"""
Voice Processing Service
Integrates Deepgram STT and Cartesia TTS for voice capabilities
"""

import os
import base64
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for voice processing with STT and TTS capabilities"""
    
    def __init__(self):
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.cartesia_api_key = os.getenv("CARTESIA_API_KEY")
        
        if not self.deepgram_api_key:
            logger.warning("DEEPGRAM_API_KEY not found. Voice input will be disabled.")
        if not self.cartesia_api_key:
            logger.warning("CARTESIA_API_KEY not found. Voice output will be disabled.")
    
    async def speech_to_text(self, audio_data: bytes, audio_format: str = "wav") -> Dict[str, Any]:
        """
        Convert audio data to text using Deepgram STT
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (wav, mp3, etc.)
            
        Returns:
            Dict with transcription results
        """
        try:
            if not self.deepgram_api_key:
                return {
                    "success": False,
                    "error": "Deepgram API key not configured",
                    "transcript": ""
                }
            
            # Import Deepgram SDK if available
            try:
                from deepgram import DeepgramClient, PrerecordedOptions
                
                # Initialize Deepgram client
                deepgram = DeepgramClient(self.deepgram_api_key)
                
                # Configure transcription options
                options = PrerecordedOptions(
                    model="nova-2",
                    language="en",
                    smart_format=True,
                    punctuate=True,
                    diarize=True,
                    detect_language=True
                )
                
                # Prepare audio data
                audio_source = {"buffer": audio_data}
                
                # Transcribe audio
                response = await deepgram.listen.prerecorded.v("1").transcribe_file(
                    audio_source, options
                )
                
                # Extract transcript
                if response.results and response.results.channels:
                    transcript = response.results.channels[0].alternatives[0].transcript
                    confidence = response.results.channels[0].alternatives[0].confidence
                    
                    return {
                        "success": True,
                        "transcript": transcript,
                        "confidence": confidence,
                        "language": response.results.language if hasattr(response.results, 'language') else "en",
                        "error": None
                    }
                else:
                    return {
                        "success": False,
                        "transcript": "",
                        "error": "No transcription result received"
                    }
                    
            except ImportError:
                logger.warning("Deepgram SDK not available. Using mock transcription.")
                # Mock transcription for testing
                return {
                    "success": True,
                    "transcript": "[Mock transcription - Deepgram SDK not installed]",
                    "confidence": 0.95,
                    "language": "en",
                    "error": None
                }
                
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return {
                "success": False,
                "transcript": "",
                "error": str(e)
            }
    
    async def text_to_speech(self, text: str, voice_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert text to speech using Cartesia TTS
        
        Args:
            text: Text to convert to speech
            voice_settings: Voice configuration (voice_id, speed, etc.)
            
        Returns:
            Dict with audio data and metadata
        """
        try:
            if not self.cartesia_api_key:
                return {
                    "success": False,
                    "error": "Cartesia API key not configured",
                    "audio_data": None
                }
            
            # Default voice settings
            settings = {
                "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",  # Default voice
                "model": "sonic-english",
                "output_format": "pcm_16000",
                "speed": 1.0,
                "emotion": "neutral"
            }
            
            if voice_settings:
                settings.update(voice_settings)
            
            try:
                import cartesia
                
                # Initialize Cartesia client
                client = cartesia.Cartesia(api_key=self.cartesia_api_key)
                
                # Generate speech
                voice = client.voices.get(id=settings["voice_id"])
                
                # Create TTS request
                response = client.tts.sse(
                    model_id=settings["model"],
                    transcript=text,
                    voice_id=settings["voice_id"],
                    output_format=settings["output_format"]
                )
                
                # Collect audio chunks
                audio_chunks = []
                for chunk in response:
                    if chunk.get("data"):
                        audio_chunks.append(base64.b64decode(chunk["data"]))
                
                # Combine audio data
                if audio_chunks:
                    audio_data = b"".join(audio_chunks)
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    return {
                        "success": True,
                        "audio_data": audio_base64,
                        "audio_format": settings["output_format"],
                        "voice_id": settings["voice_id"],
                        "text_length": len(text),
                        "error": None
                    }
                else:
                    return {
                        "success": False,
                        "audio_data": None,
                        "error": "No audio data generated"
                    }
                    
            except ImportError:
                logger.warning("Cartesia SDK not available. Using mock TTS.")
                # Mock TTS response for testing
                mock_audio = b"mock_audio_data_" + text.encode('utf-8')
                audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
                
                return {
                    "success": True,
                    "audio_data": audio_base64,
                    "audio_format": "pcm_16000",
                    "voice_id": settings["voice_id"],
                    "text_length": len(text),
                    "error": None,
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return {
                "success": False,
                "audio_data": None,
                "error": str(e)
            }
    
    async def process_voice_conversation(self, audio_data: bytes, adapter_voice_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete voice conversation processing: STT -> AI Processing -> TTS
        
        Args:
            audio_data: Input audio bytes
            adapter_voice_settings: Voice configuration from business adapter
            
        Returns:
            Dict with transcript, AI response, and audio response
        """
        try:
            # Step 1: Convert speech to text
            stt_result = await self.speech_to_text(audio_data)
            if not stt_result["success"]:
                return {
                    "success": False,
                    "error": f"Speech-to-text failed: {stt_result['error']}",
                    "transcript": "",
                    "response_text": "",
                    "response_audio": None
                }
            
            transcript = stt_result["transcript"]
            
            # Step 2: Process with AI (this would be handled by the main agent)
            # For now, return the structure that the API gateway expects
            return {
                "success": True,
                "transcript": transcript,
                "confidence": stt_result.get("confidence", 0.0),
                "language": stt_result.get("language", "en"),
                "voice_settings": adapter_voice_settings or {},
                "ready_for_ai_processing": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Voice conversation processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcript": "",
                "response_text": "",
                "response_audio": None
            }

# Global voice service instance
_voice_service = None

def get_voice_service() -> VoiceService:
    """Get the global voice service instance"""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service