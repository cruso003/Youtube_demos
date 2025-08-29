"""
API Gateway for Universal AI Agent Platform
Provides REST API endpoints with freemium rate limiting
"""

import asyncio
import json
import logging
import os
import uuid
import sys
sys.path.append('..')
from freemium_limits import check_freemium_limits, validate_free_tier_request, record_message_usage, record_session_creation, get_usage_info
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import queue

# Add payment processing
try:
    from payment.mtn_payment import MTNMobileMoneyPayment, CreditManager
except ImportError:
    print("Warning: Payment module not found. Payment features will be disabled.")
    MTNMobileMoneyPayment = None
    CreditManager = None
from openai import OpenAI

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys
from pathlib import Path

# Add the current directory to Python path for relative imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from agent_platform.agent_service import AgentConfig, get_platform_service
except ImportError:
    # Fallback to mock service if LiveKit dependencies are not available
    from agent_platform.mock_service import AgentConfig, get_platform_service

from billing.usage_tracker import UsageTracker
from rate_limiter import rate_limiter

# Import multimodal endpoints
try:
    from api_gateway.voice_endpoints import voice_bp
    from api_gateway.vision_endpoints import vision_bp
    from api_gateway.realtime_endpoints import realtime_bp
    from api_gateway.payment_endpoints import payment_bp
except ImportError as e:
    # Create placeholder blueprints if import fails
    from flask import Blueprint
    voice_bp = Blueprint('voice', __name__)
    vision_bp = Blueprint('vision', __name__)
    realtime_bp = Blueprint('realtime', __name__)
    payment_bp = Blueprint('payment', __name__)
    logger.warning(f"Failed to import multimodal endpoints: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Register multimodal endpoint blueprints
app.register_blueprint(voice_bp)
app.register_blueprint(vision_bp)
app.register_blueprint(realtime_bp)
app.register_blueprint(payment_bp)

# Import shared state
from api_gateway.shared_state import active_sessions, message_queues

# Global state management uses shared module
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

@app.route("/api/v1/usage/check", methods=["GET"])
def check_usage_limits():
    """Check current freemium usage limits and plan information"""
    try:
        usage_info = get_usage_info()
        return jsonify({
            "status": "success",
            **usage_info
        })
    except Exception as e:
        logger.error(f"Error checking usage: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to check usage limits"
        }), 500

@app.route("/api/v1/agent/create", methods=["POST"])
@check_freemium_limits()
def create_agent():
    """Create a new AI agent session with freemium rate limiting"""
    try:
        # Get client IP and API key
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '') or None
        
        # Check freemium limits
        allowed, limit_info = rate_limiter.is_allowed(client_ip, api_key)
        
        if not allowed:
            return jsonify({
                "status": "error",
                "message": limit_info.get("error", "Rate limit exceeded"),
                "limit_info": limit_info,
                "upgrade_info": {
                    "message": "Upgrade to Business tier for unlimited access",
                    "pricing": "$29/month - Perfect for African businesses",
                    "features": ["Unlimited messages", "Priority support", "Custom adapters"]
                } if limit_info.get("tier") == "free" else None
            }), 429
        
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
@check_freemium_limits()
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
        
        # Process message and generate AI response
        async def process_and_respond():
            try:
                # Load business logic adapter and generate response
                response_content = "I understand your message. How can I help you today?"
                
                logger.info(f"Processing message for adapter: {agent_config.business_logic_adapter}")
                logger.info(f"Custom settings: {agent_config.custom_settings}")
                
                if agent_config.business_logic_adapter:
                    try:
                        # Load the appropriate adapter
                        if agent_config.business_logic_adapter == "languagelearning":
                            from adapters.languagelearning import LanguagelearningAdapter
                            adapter = LanguagelearningAdapter(agent_config.custom_settings)
                            logger.info(f"Language learning adapter loaded for: {adapter.target_language}")
                        elif agent_config.business_logic_adapter == "emergencyservices":
                            from adapters.emergencyservices import EmergencyservicesAdapter
                            adapter = EmergencyservicesAdapter(agent_config.custom_settings)
                        else:
                            adapter = None
                        
                        if adapter:
                            # Get system instructions from adapter
                            system_instructions = adapter.get_system_instructions()
                            logger.info(f"System instructions: {system_instructions[:100]}...")
                            
                            # Generate AI response using OpenAI
                            openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                            completion = openai_client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": system_instructions},
                                    {"role": "user", "content": message}
                                ]
                            )
                            response_content = completion.choices[0].message.content
                            logger.info(f"OpenAI response generated: {len(response_content)} characters")
                            
                    except Exception as adapter_error:
                        logger.error(f"Adapter processing error: {adapter_error}")
                        # Fallback to default response
                
                # Add AI response to queue
                message_queues[session_id].put({
                    "id": str(uuid.uuid4()),
                    "type": "text",
                    "content": response_content,
                    "timestamp": datetime.now().isoformat(),
                    "sender": "assistant"
                })
                
                # Track AI response
                await usage_tracker.track_message_processed(agent_config.agent_id, session_id)
                
            except Exception as e:
                logger.error(f"Error processing AI response: {e}")
                # Add error response
                message_queues[session_id].put({
                    "id": str(uuid.uuid4()),
                    "type": "text",
                    "content": "I apologize, but I encountered an error processing your message. Please try again.",
                    "timestamp": datetime.now().isoformat(),
                    "sender": "assistant"
                })
        
        # Run async processing in background thread
        def run_async():
            asyncio.run(process_and_respond())
        
        thread = threading.Thread(target=run_async)
        thread.start()
        
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

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check for Kubernetes"""
    try:
        # More thorough checks for readiness
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            return jsonify({"status": "not_ready", "reason": "OpenAI API key not configured"}), 503
            
        return jsonify({
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "not_ready", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

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

# Payment Endpoints
@app.route("/api/v1/payment/packages", methods=["GET"])
def get_credit_packages():
    """Get available credit packages"""
    try:
        if MTNMobileMoneyPayment is None:
            return jsonify({
                "status": "error",
                "message": "Payment system not available"
            }), 503
        
        mtn_payment = MTNMobileMoneyPayment()
        packages = mtn_payment.get_credit_packages()
        
        return jsonify({
            "status": "success",
            "packages": packages,
            "payment_methods": ["mtn_mobile_money", "bank_card"],
            "supported_countries": ["Liberia"]
        })
        
    except Exception as e:
        logger.error(f"Error getting credit packages: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get credit packages"
        }), 500

@app.route("/api/v1/payment/mtn/request", methods=["POST"])
def request_mtn_payment():
    """Request MTN Mobile Money payment for credits"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["phone_number", "package_type", "user_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        if MTNMobileMoneyPayment is None:
            return jsonify({
                "status": "error",
                "message": "MTN Mobile Money not available"
            }), 503
        
        # Initialize MTN payment processor
        mtn_payment = MTNMobileMoneyPayment(
            environment=os.getenv("MTN_ENVIRONMENT", "sandbox"),
            target_environment="mtnliberia"
        )
        
        # Request payment
        payment_result = mtn_payment.request_payment(
            phone_number=data["phone_number"],
            package_type=data["package_type"],
            user_id=data["user_id"]
        )
        
        if payment_result.success:
            return jsonify({
                "status": "success",
                "transaction_id": payment_result.transaction_id,
                "reference_id": payment_result.reference_id,
                "message": payment_result.message,
                "payment_status": payment_result.status
            })
        else:
            return jsonify({
                "status": "error",
                "message": payment_result.message
            }), 400
            
    except Exception as e:
        logger.error(f"Error requesting MTN payment: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to process payment request"
        }), 500

@app.route("/api/v1/payment/status/<reference_id>", methods=["GET"])
def check_payment_status(reference_id: str):
    """Check payment status and add credits if successful"""
    try:
        if MTNMobileMoneyPayment is None:
            return jsonify({
                "status": "error",
                "message": "Payment system not available"
            }), 503
        
        # Initialize payment processor
        mtn_payment = MTNMobileMoneyPayment(
            environment=os.getenv("MTN_ENVIRONMENT", "sandbox"),
            target_environment="mtnliberia"
        )
        
        # Check payment status
        status_result = mtn_payment.check_payment_status(reference_id)
        
        response_data = {
            "status": "success",
            "transaction_id": status_result.transaction_id,
            "payment_status": status_result.status,
            "message": status_result.message
        }
        
        # If payment is successful, add credits to user account
        if status_result.success and status_result.status == "successful":
            # Extract user_id from reference_id (format: nexusai_userid_randomhex)
            try:
                user_id = reference_id.split("_")[1]
                
                # Get package info from reference
                # TODO: Store package info with transaction for proper credit calculation
                # For now, assume starter package (1000 credits)
                credits_to_add = 1000
                
                if CreditManager:
                    credit_manager = CreditManager()
                    if credit_manager.add_credits(user_id, credits_to_add, reference_id):
                        response_data["credits_added"] = credits_to_add
                        response_data["message"] = f"Payment successful! {credits_to_add} credits added to your account."
                    else:
                        response_data["warning"] = "Payment successful but failed to add credits. Please contact support."
                        
            except Exception as e:
                logger.error(f"Error adding credits after successful payment: {e}")
                response_data["warning"] = "Payment successful but failed to add credits. Please contact support."
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to check payment status"
        }), 500

@app.route("/api/v1/user/<user_id>/credits", methods=["GET"])
def get_user_credits(user_id: str):
    """Get user's current credit balance"""
    try:
        if CreditManager is None:
            return jsonify({
                "status": "error",
                "message": "Credit system not available"
            }), 503
        
        credit_manager = CreditManager()
        credits = credit_manager.get_user_credits(user_id)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "credits": credits,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting user credits: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get user credits"
        }), 500

if __name__ == "__main__":
    logger.info("Starting NexusAI API Gateway")
    app.run(host="0.0.0.0", port=8000, debug=False)