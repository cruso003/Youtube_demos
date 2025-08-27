"""
API Gateway for Universal AI Agent Platform
Provides REST API endpoints for client integration
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import queue

from agent_platform.agent_service import AgentConfig, get_platform_service
from billing.usage_tracker import UsageTracker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global state management
active_sessions: Dict[str, Dict] = {}
message_queues: Dict[str, queue.Queue] = {}
usage_tracker = UsageTracker()

class APIGateway:
    """Main API Gateway class"""
    
    def __init__(self):
        self.platform_service = get_platform_service()
    
    async def create_agent_session(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent session"""
        try:
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Create agent configuration
            agent_config = AgentConfig(
                agent_id=config_data.get("agent_id", session_id),
                instructions=config_data.get("instructions", "You are a helpful AI assistant."),
                capabilities=config_data.get("capabilities", ["text"]),
                business_logic_adapter=config_data.get("business_logic_adapter"),
                custom_settings=config_data.get("custom_settings", {})
            )
            
            # Store session info
            active_sessions[session_id] = {
                "agent_config": agent_config,
                "status": "created",
                "created_at": datetime.now(),
                "client_id": config_data.get("client_id", "default")
            }
            
            # Create message queue for this session
            message_queues[session_id] = queue.Queue()
            
            return {
                "session_id": session_id,
                "agent_id": agent_config.agent_id,
                "status": "success",
                "capabilities": agent_config.capabilities,
                "message": "Agent session created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create agent session: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

# Initialize API Gateway
api_gateway = APIGateway()

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(active_sessions)
    })

@app.route("/api/v1/agent/create", methods=["POST"])
def create_agent():
    """Create a new AI agent session"""
    try:
        config_data = request.get_json()
        
        # Validate required fields
        if not config_data:
            return jsonify({
                "status": "error",
                "message": "Request body is required"
            }), 400
        
        # Run async function in thread
        result = asyncio.run(api_gateway.create_agent_session(config_data))
        
        if result.get("status") == "error":
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error in create_agent: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route("/api/v1/agent/<session_id>/message", methods=["POST"])
def send_message(session_id: str):
    """Send a message to an agent session"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        data = request.get_json()
        message = data.get("message", "")
        message_type = data.get("type", "text")  # text, image, audio
        
        if not message:
            return jsonify({
                "status": "error",
                "message": "Message content is required"
            }), 400
        
        # Add message to session queue
        message_queues[session_id].put({
            "id": str(uuid.uuid4()),
            "type": message_type,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "sender": "user"
        })
        
        # Track message processing
        agent_config = active_sessions[session_id]["agent_config"]
        asyncio.run(usage_tracker.track_message_processed(agent_config.agent_id, session_id))
        
        return jsonify({
            "status": "success",
            "message": "Message sent successfully"
        })
        
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route("/api/v1/agent/<session_id>/messages", methods=["GET"])
def get_messages(session_id: str):
    """Get messages from an agent session"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        messages = []
        message_queue = message_queues.get(session_id)
        
        if message_queue:
            # Get all available messages without blocking
            while not message_queue.empty():
                try:
                    messages.append(message_queue.get_nowait())
                except queue.Empty:
                    break
        
        return jsonify({
            "status": "success",
            "messages": messages,
            "session_status": active_sessions[session_id]["status"]
        })
        
    except Exception as e:
        logger.error(f"Error in get_messages: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route("/api/v1/agent/<session_id>/status", methods=["GET"])
def get_session_status(session_id: str):
    """Get status of an agent session"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        session_info = active_sessions[session_id]
        
        return jsonify({
            "session_id": session_id,
            "agent_id": session_info["agent_config"].agent_id,
            "status": session_info["status"],
            "capabilities": session_info["agent_config"].capabilities,
            "created_at": session_info["created_at"].isoformat(),
            "business_logic_adapter": session_info["agent_config"].business_logic_adapter
        })
        
    except Exception as e:
        logger.error(f"Error in get_session_status: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route("/api/v1/agent/<session_id>", methods=["DELETE"])
def delete_session(session_id: str):
    """Delete an agent session"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Track session end
        agent_config = active_sessions[session_id]["agent_config"]
        asyncio.run(usage_tracker.track_session_end(agent_config.agent_id, session_id))
        
        # Clean up session
        del active_sessions[session_id]
        if session_id in message_queues:
            del message_queues[session_id]
        
        return jsonify({
            "status": "success",
            "message": "Session deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error in delete_session: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route("/api/v1/usage/<client_id>", methods=["GET"])
def get_usage_summary(client_id: str):
    """Get usage summary for billing"""
    try:
        # Parse date parameters
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.now()
        
        # Get usage summary
        usage_summary = asyncio.run(usage_tracker.get_usage_summary(
            agent_id=client_id,
            start_date=start_date,
            end_date=end_date
        ))
        
        return jsonify({
            "status": "success",
            "client_id": client_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "usage": usage_summary
        })
        
    except Exception as e:
        logger.error(f"Error in get_usage_summary: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route("/api/v1/billing/<client_id>", methods=["GET"])
def get_billing_info(client_id: str):
    """Get billing information for a client"""
    try:
        # Parse parameters
        plan_id = request.args.get("plan_id", "starter")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.now()
        
        # Calculate bill
        bill = asyncio.run(usage_tracker.calculate_bill(
            client_id=client_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date
        ))
        
        return jsonify({
            "status": "success",
            "billing_info": bill
        })
        
    except Exception as e:
        logger.error(f"Error in get_billing_info: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route("/api/v1/agents", methods=["GET"])
def list_active_sessions():
    """List all active agent sessions"""
    try:
        sessions = []
        for session_id, session_info in active_sessions.items():
            sessions.append({
                "session_id": session_id,
                "agent_id": session_info["agent_config"].agent_id,
                "status": session_info["status"],
                "capabilities": session_info["agent_config"].capabilities,
                "created_at": session_info["created_at"].isoformat(),
                "client_id": session_info["client_id"]
            })
        
        return jsonify({
            "status": "success",
            "sessions": sessions,
            "total_sessions": len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error in list_active_sessions: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500

if __name__ == "__main__":
    logger.info("Starting Universal AI Agent Platform API Gateway")
    app.run(host="0.0.0.0", port=8000, debug=False)