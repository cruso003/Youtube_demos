"""
Vision Endpoints for Universal AI Agent Platform
Handles image upload, analysis, and vision-aware processing
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
from services.vision_service import get_vision_service
from billing.usage_tracker import UsageTracker

logger = logging.getLogger(__name__)

# Create vision blueprint
vision_bp = Blueprint('vision', __name__)

# Initialize services
vision_service = get_vision_service()
usage_tracker = UsageTracker()

@vision_bp.route("/api/v1/agent/<session_id>/image", methods=["POST"])
def process_image_upload(session_id: str):
    """
    Process image upload for an agent session
    
    Accepts image file upload, analyzes with AI vision, and prepares for conversation
    """
    try:
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Get image file from request
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No image file selected"
            }), 400
        
        # Read image data
        image_data = image_file.read()
        
        # Get business adapter for vision instructions
        session_info = active_sessions[session_id]
        agent_config = session_info["agent_config"]
        
        vision_instructions = None
        if hasattr(agent_config, 'business_logic_adapter') and agent_config.business_logic_adapter:
            # Load adapter to get vision instructions
            try:
                from adapters.business_logic_adapter import BusinessLogicAdapter
                adapter = BusinessLogicAdapter.load(agent_config.business_logic_adapter)
                if hasattr(adapter, 'get_vision_instructions'):
                    vision_instructions = adapter.get_vision_instructions()
            except Exception as e:
                logger.warning(f"Could not load vision instructions from adapter: {e}")
        
        # Process image
        async def process_image():
            # Analyze image with vision service
            analysis_result = await vision_service.process_image_upload(
                image_data, 
                session_id, 
                vision_instructions
            )
            
            if analysis_result["success"]:
                # Track image processing usage
                await usage_tracker.track_image_processed(
                    agent_config.agent_id,
                    session_id,
                    data_size_bytes=len(image_data),
                    image_format=analysis_result.get("image_format", "unknown")
                )
                
                # Add image analysis to session queue
                message_queues[session_id].put({
                    "id": f"image_{datetime.now().timestamp()}",
                    "type": "image_analysis",
                    "content": analysis_result["image_analysis"],
                    "timestamp": datetime.now().isoformat(),
                    "sender": "user",
                    "image_metadata": {
                        "format": analysis_result.get("image_format", "unknown"),
                        "size": analysis_result.get("image_size", [0, 0]),
                        "bytes": len(image_data),
                        "analysis_model": "gpt-4o"
                    }
                })
                
                return {
                    "status": "success",
                    "image_analysis": analysis_result["image_analysis"],
                    "image_format": analysis_result.get("image_format"),
                    "image_size": analysis_result.get("image_size"),
                    "processing_time": analysis_result.get("processing_time", 0),
                    "usage": analysis_result.get("usage", {}),
                    "ready_for_conversation": True
                }
            else:
                return {
                    "status": "error",
                    "message": f"Image analysis failed: {analysis_result['error']}",
                    "image_analysis": ""
                }
        
        # Run async processing
        result = asyncio.run(process_image())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during image processing"
        }), 500

@vision_bp.route("/api/v1/agent/<session_id>/image-text", methods=["POST"])
def extract_text_from_image(session_id: str):
    """
    Extract text from uploaded image using OCR capabilities
    """
    try:
        # Import active sessions from main module
        
        
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Get image file from request
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # Get language parameter
        language = request.form.get('language', 'en')
        
        # Extract text from image
        async def extract_text():
            text_result = await vision_service.extract_text_from_image(image_data, language)
            
            if text_result["success"]:
                # Track OCR usage
                session_info = active_sessions[session_id]
                agent_config = session_info["agent_config"]
                
                await usage_tracker.track_ocr_processed(
                    agent_config.agent_id,
                    session_id,
                    data_size_bytes=len(image_data),
                    language=language
                )
                
                return {
                    "status": "success",
                    "extracted_text": text_result["extracted_text"],
                    "language": text_result["language"],
                    "method": text_result["method"],
                    "confidence": text_result.get("confidence", 0.0)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Text extraction failed: {text_result['error']}",
                    "extracted_text": ""
                }
        
        # Run async processing
        result = asyncio.run(extract_text())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Text extraction error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during text extraction"
        }), 500

@vision_bp.route("/api/v1/agent/<session_id>/image-conversation", methods=["POST"])
def process_image_conversation(session_id: str):
    """
    Complete image conversation: Image Analysis -> AI Processing -> Response
    
    This endpoint processes image input and returns conversational response
    """
    try:
        # Import active sessions and message queues from main module
        
        
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Get image file and optional text prompt
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # Get optional text prompt to accompany the image
        text_prompt = request.form.get('prompt', '')
        
        # Get session info and adapter
        session_info = active_sessions[session_id]
        agent_config = session_info["agent_config"]
        
        # Process complete image conversation
        async def process_conversation():
            # Get vision instructions from adapter
            vision_instructions = None
            if hasattr(agent_config, 'business_logic_adapter') and agent_config.business_logic_adapter:
                try:
                    from adapters.business_logic_adapter import BusinessLogicAdapter
                    adapter = BusinessLogicAdapter.load(agent_config.business_logic_adapter)
                    if hasattr(adapter, 'get_vision_instructions'):
                        vision_instructions = adapter.get_vision_instructions()
                        
                        # If user provided a prompt, combine it with adapter instructions
                        if text_prompt:
                            vision_instructions = f"{vision_instructions}\n\nUser prompt: {text_prompt}"
                        
                except Exception as e:
                    logger.warning(f"Could not load vision instructions: {e}")
            
            # If no adapter instructions but user provided prompt, use that
            if not vision_instructions and text_prompt:
                vision_instructions = text_prompt
            
            # Analyze image
            analysis_result = await vision_service.analyze_image(image_data, vision_instructions)
            
            if not analysis_result["success"]:
                return {
                    "status": "error",
                    "message": f"Image analysis failed: {analysis_result['error']}",
                    "image_analysis": "",
                    "response_text": ""
                }
            
            image_analysis = analysis_result["analysis"]
            
            # Add message to session for AI processing
            combined_content = image_analysis
            if text_prompt:
                combined_content = f"User prompt: {text_prompt}\n\nImage analysis: {image_analysis}"
            
            message_queues[session_id].put({
                "id": f"image_conv_{datetime.now().timestamp()}",
                "type": "image_conversation",
                "content": combined_content,
                "timestamp": datetime.now().isoformat(),
                "sender": "user",
                "image_metadata": {
                    "has_image": True,
                    "user_prompt": text_prompt,
                    "analysis_model": "gpt-4o",
                    "processing_type": "full_conversation"
                }
            })
            
            # Simulate AI response (in real implementation, this would come from the agent)
            if text_prompt:
                ai_response = f"I can see the image you shared. {image_analysis}\n\nRegarding your question: '{text_prompt}' - This is a simulated AI response for image conversation testing."
            else:
                ai_response = f"I can see the image you shared. {image_analysis}\n\nThis is a simulated AI response for image conversation testing. Feel free to ask me questions about what you see!"
            
            # Track usage
            await usage_tracker.track_image_conversation(
                agent_config.agent_id,
                session_id,
                image_size_bytes=len(image_data),
                response_text_length=len(ai_response),
                has_text_prompt=bool(text_prompt)
            )
            
            return {
                "status": "success",
                "image_analysis": image_analysis,
                "user_prompt": text_prompt,
                "response_text": ai_response,
                "usage": analysis_result.get("usage", {}),
                "processing_time": datetime.now().isoformat()
            }
        
        # Run async processing
        result = asyncio.run(process_conversation())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Image conversation error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during image conversation"
        }), 500

@vision_bp.route("/api/v1/agent/<session_id>/analyze-scene", methods=["POST"])
def analyze_scene(session_id: str):
    """
    Specialized endpoint for scene analysis with domain-specific focus
    """
    try:
        # Import active sessions from main module
        
        
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Get image file from request
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # Get analysis type parameter
        analysis_type = request.form.get('analysis_type', 'general')
        
        # Get session info and adapter
        session_info = active_sessions[session_id]
        agent_config = session_info["agent_config"]
        
        # Prepare specialized instructions based on analysis type and adapter
        specialized_instructions = _get_specialized_instructions(analysis_type, agent_config)
        
        # Analyze scene
        async def analyze():
            analysis_result = await vision_service.analyze_image(image_data, specialized_instructions)
            
            if analysis_result["success"]:
                # Track specialized analysis usage
                await usage_tracker.track_scene_analysis(
                    agent_config.agent_id,
                    session_id,
                    analysis_type=analysis_type,
                    data_size_bytes=len(image_data)
                )
                
                return {
                    "status": "success",
                    "scene_analysis": analysis_result["analysis"],
                    "analysis_type": analysis_type,
                    "adapter": agent_config.business_logic_adapter,
                    "usage": analysis_result.get("usage", {}),
                    "confidence_indicators": _extract_confidence_indicators(analysis_result["analysis"])
                }
            else:
                return {
                    "status": "error",
                    "message": f"Scene analysis failed: {analysis_result['error']}",
                    "scene_analysis": ""
                }
        
        # Run async processing
        result = asyncio.run(analyze())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Scene analysis error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during scene analysis"
        }), 500

def _get_specialized_instructions(analysis_type: str, agent_config) -> str:
    """Get specialized analysis instructions based on type and business adapter"""
    
    # Base instructions for different analysis types
    type_instructions = {
        "general": "Provide a comprehensive analysis of this scene, including objects, people, activities, and context.",
        "safety": "Analyze this scene for safety hazards, risks, and emergency situations. Focus on identifying potential dangers.",
        "educational": "Analyze this scene from an educational perspective. Identify learning opportunities and teaching points.",
        "medical": "Analyze this scene for medical concerns, visible injuries, or health-related indicators.",
        "security": "Analyze this scene for security concerns, suspicious activities, or safety threats."
    }
    
    base_instruction = type_instructions.get(analysis_type, type_instructions["general"])
    
    # Add adapter-specific context
    if hasattr(agent_config, 'business_logic_adapter') and agent_config.business_logic_adapter:
        try:
            from adapters.business_logic_adapter import BusinessLogicAdapter
            adapter = BusinessLogicAdapter.load(agent_config.business_logic_adapter)
            if hasattr(adapter, 'get_vision_instructions'):
                adapter_instructions = adapter.get_vision_instructions()
                return f"{base_instruction}\n\nDomain-specific context: {adapter_instructions}"
        except Exception as e:
            logger.warning(f"Could not load adapter instructions: {e}")
    
    return base_instruction

def _extract_confidence_indicators(analysis_text: str) -> Dict[str, Any]:
    """Extract confidence indicators from analysis text"""
    indicators = {
        "has_uncertainty_words": any(word in analysis_text.lower() for word in ["maybe", "possibly", "appears", "seems", "might", "could be"]),
        "has_definitive_words": any(word in analysis_text.lower() for word in ["clearly", "definitely", "obviously", "certain", "confirmed"]),
        "word_count": len(analysis_text.split()),
        "detail_level": "high" if len(analysis_text) > 500 else "medium" if len(analysis_text) > 200 else "low"
    }
    
    return indicators