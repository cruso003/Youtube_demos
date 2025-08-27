"""
Voice Endpoints for Universal AI Agent Platform
Handles voice upload, processing, and response generation
"""

import asyncio
import json
import logging
import base64
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Blueprint, request, jsonify
import io

from api_gateway.shared_state import active_sessions, message_queues
from services.voice_service import get_voice_service
from billing.usage_tracker import UsageTracker

logger = logging.getLogger(__name__)

# Create voice blueprint
voice_bp = Blueprint('voice', __name__)

# Initialize services
voice_service = get_voice_service()
usage_tracker = UsageTracker()

@voice_bp.route("/api/v1/agent/<session_id>/voice", methods=["POST"])
def process_voice_input(session_id: str):
    """
    Process voice input for an agent session
    
    Accepts audio file upload, converts to text, and prepares for AI processing
    """
    try:
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No audio file provided"
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No audio file selected"
            }), 400
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Get audio format from filename or content type
        audio_format = _get_audio_format(audio_file.filename, audio_file.content_type)
        
        # Get business adapter for voice settings
        session_info = active_sessions[session_id]
        agent_config = session_info["agent_config"]
        
        voice_settings = None
        if hasattr(agent_config, 'business_logic_adapter') and agent_config.business_logic_adapter:
            # Load adapter to get voice settings
            try:
                from adapters.business_logic_adapter import BusinessLogicAdapter
                adapter = BusinessLogicAdapter.load(agent_config.business_logic_adapter)
                if hasattr(adapter, 'get_voice_settings'):
                    voice_settings = adapter.get_voice_settings()
            except Exception as e:
                logger.warning(f"Could not load voice settings from adapter: {e}")
        
        # Process voice input
        async def process_voice():
            # Convert speech to text
            stt_result = await voice_service.speech_to_text(audio_data, audio_format)
            
            if stt_result["success"]:
                # Track voice processing usage
                await usage_tracker.track_voice_processed(
                    agent_config.agent_id, 
                    session_id, 
                    duration_seconds=_estimate_audio_duration(audio_data),
                    data_size_bytes=len(audio_data)
                )
                
                # Add transcribed message to session queue
                message_queues[session_id].put({
                    "id": f"voice_{datetime.now().timestamp()}",
                    "type": "voice_transcript",
                    "content": stt_result["transcript"],
                    "timestamp": datetime.now().isoformat(),
                    "sender": "user",
                    "voice_metadata": {
                        "confidence": stt_result.get("confidence", 0.0),
                        "language": stt_result.get("language", "en"),
                        "audio_format": audio_format,
                        "audio_size_bytes": len(audio_data)
                    }
                })
                
                return {
                    "status": "success",
                    "transcript": stt_result["transcript"],
                    "confidence": stt_result.get("confidence", 0.0),
                    "language": stt_result.get("language", "en"),
                    "voice_settings": voice_settings,
                    "ready_for_ai_processing": True
                }
            else:
                return {
                    "status": "error",
                    "message": f"Voice processing failed: {stt_result['error']}",
                    "transcript": ""
                }
        
        # Run async processing
        result = asyncio.run(process_voice())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during voice processing"
        }), 500

@voice_bp.route("/api/v1/agent/<session_id>/speak", methods=["POST"])
def generate_speech_response(session_id: str):
    """
    Generate speech response from text using TTS
    """
    try:
        # Import active sessions from main module
        
        
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Get request data
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                "status": "error",
                "message": "Text content is required"
            }), 400
        
        text = data.get('text', '')
        if not text.strip():
            return jsonify({
                "status": "error",
                "message": "Text content cannot be empty"
            }), 400
        
        # Get business adapter for voice settings
        session_info = active_sessions[session_id]
        agent_config = session_info["agent_config"]
        
        voice_settings = data.get('voice_settings', {})
        if hasattr(agent_config, 'business_logic_adapter') and agent_config.business_logic_adapter:
            # Load adapter to get voice settings
            try:
                from adapters.business_logic_adapter import BusinessLogicAdapter
                adapter = BusinessLogicAdapter.load(agent_config.business_logic_adapter)
                if hasattr(adapter, 'get_voice_settings'):
                    adapter_voice_settings = adapter.get_voice_settings()
                    # Merge adapter settings with request settings (request takes priority)
                    voice_settings = {**adapter_voice_settings, **voice_settings}
            except Exception as e:
                logger.warning(f"Could not load voice settings from adapter: {e}")
        
        # Generate speech
        async def generate_speech():
            tts_result = await voice_service.text_to_speech(text, voice_settings)
            
            if tts_result["success"]:
                # Track TTS usage
                await usage_tracker.track_voice_generated(
                    agent_config.agent_id,
                    session_id,
                    text_length=len(text),
                    audio_size_bytes=len(base64.b64decode(tts_result["audio_data"]))
                )
                
                return {
                    "status": "success",
                    "audio_data": tts_result["audio_data"],
                    "audio_format": tts_result["audio_format"],
                    "voice_id": tts_result["voice_id"],
                    "text_length": tts_result["text_length"],
                    "duration_estimate": _estimate_speech_duration(text)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Speech generation failed: {tts_result['error']}",
                    "audio_data": None
                }
        
        # Run async processing
        result = asyncio.run(generate_speech())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Speech generation error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during speech generation"
        }), 500

@voice_bp.route("/api/v1/agent/<session_id>/voice-conversation", methods=["POST"])
def process_voice_conversation(session_id: str):
    """
    Complete voice conversation: STT -> AI Processing -> TTS
    
    This endpoint processes voice input and returns both text and audio responses
    """
    try:
        # Import active sessions and message queues from main module
        
        
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No audio file provided"
            }), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        audio_format = _get_audio_format(audio_file.filename, audio_file.content_type)
        
        # Get session info and adapter
        session_info = active_sessions[session_id]
        agent_config = session_info["agent_config"]
        
        # Process complete voice conversation
        async def process_conversation():
            # Step 1: Speech to Text
            stt_result = await voice_service.speech_to_text(audio_data, audio_format)
            
            if not stt_result["success"]:
                return {
                    "status": "error",
                    "message": f"Speech recognition failed: {stt_result['error']}",
                    "transcript": "",
                    "response_text": "",
                    "response_audio": None
                }
            
            transcript = stt_result["transcript"]
            
            # Step 2: Add message to session for AI processing
            # This would normally trigger AI processing, but for now we'll simulate
            message_queues[session_id].put({
                "id": f"voice_conv_{datetime.now().timestamp()}",
                "type": "voice_conversation",
                "content": transcript,
                "timestamp": datetime.now().isoformat(),
                "sender": "user",
                "voice_metadata": {
                    "confidence": stt_result.get("confidence", 0.0),
                    "language": stt_result.get("language", "en"),
                    "processing_type": "full_conversation"
                }
            })
            
            # Step 3: Simulate AI response (in real implementation, this would come from the agent)
            ai_response = f"I heard you say: '{transcript}'. This is a simulated AI response for voice conversation testing."
            
            # Step 4: Convert AI response to speech
            voice_settings = {}
            if hasattr(agent_config, 'business_logic_adapter') and agent_config.business_logic_adapter:
                try:
                    from adapters.business_logic_adapter import BusinessLogicAdapter
                    adapter = BusinessLogicAdapter.load(agent_config.business_logic_adapter)
                    if hasattr(adapter, 'get_voice_settings'):
                        voice_settings = adapter.get_voice_settings()
                except Exception as e:
                    logger.warning(f"Could not load voice settings: {e}")
            
            tts_result = await voice_service.text_to_speech(ai_response, voice_settings)
            
            # Track usage
            await usage_tracker.track_voice_conversation(
                agent_config.agent_id,
                session_id,
                input_duration=_estimate_audio_duration(audio_data),
                output_text_length=len(ai_response),
                input_size_bytes=len(audio_data)
            )
            
            return {
                "status": "success",
                "transcript": transcript,
                "transcript_confidence": stt_result.get("confidence", 0.0),
                "response_text": ai_response,
                "response_audio": tts_result["audio_data"] if tts_result["success"] else None,
                "audio_format": tts_result.get("audio_format", "pcm_16000"),
                "voice_settings": voice_settings,
                "processing_time": datetime.now().isoformat()
            }
        
        # Run async processing
        result = asyncio.run(process_conversation())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Voice conversation error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during voice conversation"
        }), 500

def _get_audio_format(filename: str, content_type: str) -> str:
    """Extract audio format from filename or content type"""
    if filename:
        extension = filename.lower().split('.')[-1]
        format_map = {
            'wav': 'wav',
            'mp3': 'mp3',
            'ogg': 'ogg',
            'flac': 'flac',
            'm4a': 'm4a',
            'webm': 'webm'
        }
        return format_map.get(extension, 'wav')
    
    if content_type:
        if 'wav' in content_type:
            return 'wav'
        elif 'mp3' in content_type:
            return 'mp3'
        elif 'ogg' in content_type:
            return 'ogg'
    
    return 'wav'  # Default

def _estimate_audio_duration(audio_data: bytes) -> float:
    """Estimate audio duration in seconds (rough calculation)"""
    # This is a very rough estimate - would need proper audio analysis
    # Assuming 16kHz, 16-bit, mono PCM: 32000 bytes per second
    estimated_duration = len(audio_data) / 32000.0
    return max(0.1, min(estimated_duration, 300.0))  # Clamp between 0.1 and 300 seconds

def _estimate_speech_duration(text: str) -> float:
    """Estimate speech duration based on text length"""
    # Rough estimate: ~150 words per minute, ~5 characters per word
    words = len(text) / 5.0
    duration = (words / 150.0) * 60.0  # Convert to seconds
    return max(0.5, duration)  # Minimum 0.5 seconds