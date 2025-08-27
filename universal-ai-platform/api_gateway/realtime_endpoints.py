"""
Real-time Endpoints for Universal AI Agent Platform
Handles LiveKit session management and real-time multimodal processing
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Blueprint, request, jsonify

from api_gateway.shared_state import active_sessions, message_queues
from services.realtime_service import get_realtime_service
from services.phone_service import get_phone_service
from billing.usage_tracker import UsageTracker

logger = logging.getLogger(__name__)

# Create realtime blueprint
realtime_bp = Blueprint('realtime', __name__)

# Initialize services
realtime_service = get_realtime_service()
phone_service = get_phone_service()
usage_tracker = UsageTracker()

@realtime_bp.route("/api/v1/agent/<session_id>/realtime/start", methods=["POST"])
def start_realtime_session(session_id: str):
    """
    Start a real-time multimodal session using LiveKit
    
    Creates LiveKit room and prepares AI agent for real-time interaction
    """
    try:
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Get request data
        data = request.get_json() or {}
        
        # Get session info
        session_info = active_sessions[session_id]
        agent_config = session_info["agent_config"]
        
        # Room configuration
        room_config = {
            "max_participants": data.get("max_participants", 10),
            "audio_enabled": data.get("audio_enabled", True),
            "video_enabled": data.get("video_enabled", True),
            "screen_share_enabled": data.get("screen_share_enabled", True),
            "recording_enabled": data.get("recording_enabled", False)
        }
        
        # Start real-time session
        async def start_session():
            # Create LiveKit room
            room_result = await realtime_service.create_room(session_id, room_config)
            
            if not room_result["success"]:
                return {
                    "status": "error",
                    "message": f"Failed to create room: {room_result['error']}",
                    "room_details": None
                }
            
            # Start AI agent in room
            agent_result = await realtime_service.start_ai_agent_in_room(
                room_result["room_name"],
                {
                    "capabilities": agent_config.capabilities,
                    "business_logic_adapter": agent_config.business_logic_adapter,
                    "custom_settings": agent_config.custom_settings
                }
            )
            
            if agent_result["success"]:
                # Track real-time session start
                await usage_tracker.track_realtime_session_start(
                    agent_config.agent_id,
                    session_id,
                    room_result["room_name"]
                )
                
                # Update session info
                active_sessions[session_id]["realtime_room"] = room_result["room_name"]
                active_sessions[session_id]["realtime_started"] = datetime.now()
                active_sessions[session_id]["status"] = "realtime_active"
                
                return {
                    "status": "success",
                    "room_details": {
                        "room_name": room_result["room_name"],
                        "room_sid": room_result["room_sid"],
                        "access_token": room_result["access_token"],
                        "livekit_url": room_result["livekit_url"]
                    },
                    "agent_details": {
                        "agent_id": agent_result["agent_id"],
                        "capabilities": agent_result["capabilities"],
                        "status": agent_result["status"]
                    },
                    "session_id": session_id,
                    "config": room_config
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to start agent: {agent_result['error']}",
                    "room_details": room_result
                }
        
        # Run async processing
        result = asyncio.run(start_session())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Real-time session start error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during real-time session start"
        }), 500

@realtime_bp.route("/api/v1/agent/<session_id>/realtime/status", methods=["GET"])
def get_realtime_status(session_id: str):
    """
    Get status of real-time session
    """
    try:
        # Import active sessions from main module
        
        
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        session_info = active_sessions[session_id]
        
        # Check if real-time session is active
        if "realtime_room" not in session_info:
            return jsonify({
                "status": "success",
                "realtime_active": False,
                "session_id": session_id,
                "message": "No real-time session active"
            })
        
        # Calculate session duration
        start_time = session_info.get("realtime_started")
        duration_seconds = 0
        if start_time:
            duration_seconds = (datetime.now() - start_time).total_seconds()
        
        return jsonify({
            "status": "success",
            "realtime_active": True,
            "session_id": session_id,
            "room_name": session_info["realtime_room"],
            "duration_seconds": duration_seconds,
            "session_status": session_info["status"],
            "capabilities": session_info["agent_config"].capabilities,
            "business_adapter": session_info["agent_config"].business_logic_adapter
        })
        
    except Exception as e:
        logger.error(f"Real-time status error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during status check"
        }), 500

@realtime_bp.route("/api/v1/agent/<session_id>/realtime/stop", methods=["POST"])
def stop_realtime_session(session_id: str):
    """
    Stop a real-time session and clean up resources
    """
    try:
        # Import active sessions from main module
        
        
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        session_info = active_sessions[session_id]
        
        # Check if real-time session is active
        if "realtime_room" not in session_info:
            return jsonify({
                "status": "success",
                "message": "No real-time session to stop"
            })
        
        room_name = session_info["realtime_room"]
        
        # Stop real-time session
        async def stop_session():
            # End session and clean up room
            cleanup_result = await realtime_service.end_session(room_name)
            
            # Calculate session duration for billing
            start_time = session_info.get("realtime_started")
            duration_seconds = 0
            if start_time:
                duration_seconds = (datetime.now() - start_time).total_seconds()
            
            # Track session end
            agent_config = session_info["agent_config"]
            await usage_tracker.track_realtime_session_end(
                agent_config.agent_id,
                session_id,
                duration_seconds
            )
            
            # Update session info
            del active_sessions[session_id]["realtime_room"]
            if "realtime_started" in active_sessions[session_id]:
                del active_sessions[session_id]["realtime_started"]
            active_sessions[session_id]["status"] = "active"
            
            return {
                "status": "success",
                "message": "Real-time session stopped successfully",
                "session_id": session_id,
                "room_name": room_name,
                "duration_seconds": duration_seconds,
                "cleanup_result": cleanup_result
            }
        
        # Run async processing
        result = asyncio.run(stop_session())
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Real-time session stop error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during real-time session stop"
        }), 500

@realtime_bp.route("/api/v1/agent/<session_id>/phone/call", methods=["POST"])
def initiate_phone_call(session_id: str):
    """
    Initiate a phone call via Twilio and connect to real-time session
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
        if not data or 'to_number' not in data:
            return jsonify({
                "status": "error",
                "message": "Phone number is required"
            }), 400
        
        to_number = data['to_number']
        
        # Get session info
        session_info = active_sessions[session_id]
        agent_config = session_info["agent_config"]
        
        # Adapter configuration for call handling
        adapter_config = {
            "business_logic_adapter": agent_config.business_logic_adapter,
            "custom_settings": agent_config.custom_settings
        }
        
        # Initiate phone call
        async def start_call():
            call_result = await phone_service.initiate_call(
                to_number,
                session_id,
                adapter_config
            )
            
            if call_result["success"]:
                # Track phone call initiation
                await usage_tracker.track_phone_call_start(
                    agent_config.agent_id,
                    session_id,
                    to_number,
                    call_result["call_sid"]
                )
                
                # Update session with call info
                active_sessions[session_id]["phone_call"] = {
                    "call_sid": call_result["call_sid"],
                    "to_number": to_number,
                    "started_at": datetime.now(),
                    "status": "initiated"
                }
                
                return {
                    "status": "success",
                    "call_details": {
                        "call_sid": call_result["call_sid"],
                        "to_number": to_number,
                        "from_number": call_result["from_number"],
                        "status": call_result["status"]
                    },
                    "session_id": session_id,
                    "message": "Phone call initiated successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to initiate call: {call_result['error']}",
                    "call_details": None
                }
        
        # Run async processing
        result = asyncio.run(start_call())
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Phone call initiation error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during phone call initiation"
        }), 500

@realtime_bp.route("/api/v1/phone/twiml/<session_id>", methods=["POST"])
def handle_twiml_webhook(session_id: str):
    """
    Handle TwiML webhook from Twilio for call events
    """
    try:
        # Get webhook data from Twilio
        webhook_data = request.form.to_dict()
        webhook_data["session_id"] = session_id
        
        # Process webhook
        async def process_webhook():
            webhook_result = await phone_service.handle_call_webhook(webhook_data)
            return webhook_result
        
        # Run async processing
        result = asyncio.run(process_webhook())
        
        # Return TwiML response
        if result["success"]:
            return result["twiml_response"], 200, {'Content-Type': 'application/xml'}
        else:
            # Return error TwiML
            error_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">We're sorry, there was an error processing your call.</Say>
    <Hangup/>
</Response>"""
            return error_twiml, 500, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        logger.error(f"TwiML webhook error: {e}")
        error_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">We're sorry, there was a system error.</Say>
    <Hangup/>
</Response>"""
        return error_twiml, 500, {'Content-Type': 'application/xml'}

@realtime_bp.route("/api/v1/phone/status/<session_id>", methods=["POST"])
def handle_call_status_webhook(session_id: str):
    """
    Handle call status webhook from Twilio
    """
    try:
        # Import active sessions from main module
        
        
        # Get webhook data
        webhook_data = request.form.to_dict()
        call_status = webhook_data.get("CallStatus")
        call_sid = webhook_data.get("CallSid")
        
        logger.info(f"Call status webhook: {session_id} - {call_status}")
        
        # Update session call status if session exists
        if session_id in active_sessions and "phone_call" in active_sessions[session_id]:
            active_sessions[session_id]["phone_call"]["status"] = call_status
            
            # If call completed, track usage
            if call_status == "completed":
                session_info = active_sessions[session_id]
                call_info = session_info["phone_call"]
                
                # Calculate call duration
                start_time = call_info.get("started_at")
                duration_seconds = 0
                if start_time:
                    duration_seconds = (datetime.now() - start_time).total_seconds()
                
                # Track call completion
                async def track_completion():
                    agent_config = session_info["agent_config"]
                    await usage_tracker.track_phone_call_end(
                        agent_config.agent_id,
                        session_id,
                        call_sid,
                        duration_seconds
                    )
                
                asyncio.run(track_completion())
                
                # Clean up call info
                del active_sessions[session_id]["phone_call"]
        
        return jsonify({
            "status": "success",
            "message": "Status webhook processed"
        }), 200
        
    except Exception as e:
        logger.error(f"Call status webhook error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@realtime_bp.route("/api/v1/agent/<session_id>/phone/end", methods=["POST"])
def end_phone_call(session_id: str):
    """
    End an active phone call
    """
    try:
        # Import active sessions from main module
        
        
        # Check if session exists
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        session_info = active_sessions[session_id]
        
        # Check if phone call is active
        if "phone_call" not in session_info:
            return jsonify({
                "status": "success",
                "message": "No active phone call to end"
            })
        
        call_sid = session_info["phone_call"]["call_sid"]
        
        # End phone call
        async def end_call():
            end_result = await phone_service.end_call(call_sid)
            
            if end_result["success"]:
                # Clean up call info
                del active_sessions[session_id]["phone_call"]
                
                return {
                    "status": "success",
                    "message": "Phone call ended successfully",
                    "call_sid": call_sid
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to end call: {end_result['error']}",
                    "call_sid": call_sid
                }
        
        # Run async processing
        result = asyncio.run(end_call())
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Phone call end error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during phone call end"
        }), 500