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
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append('..')
from api_gateway.freemium_limits import check_freemium_limits, validate_free_tier_request, record_message_usage, record_session_creation, get_usage_info
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys
from pathlib import Path
# Ensure project root is in sys.path for Docker and local
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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

def check_api_key_and_credits(estimated_tokens=100):
    """Decorator to check API key and credits - ONLY for service endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Only accept API keys for service endpoints
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return jsonify({
                        "status": "error",
                        "message": "Missing API key"
                    }), 401
                
                api_key = auth_header.replace('Bearer ', '')
                
                # Ensure it's actually an API key, not a JWT token
                if not api_key.startswith('nexus_'):
                    return jsonify({
                        "status": "error",
                        "message": "Invalid API key format. Use API key, not JWT token."
                    }), 401
                
                # Check credits via local credit manager (more reliable)
                try:
                    from billing.credit_manager import LocalCreditManager
                    credit_manager = LocalCreditManager()
                    credit_check = credit_manager.verify_api_key_credits(api_key, estimated_tokens)
                    
                    if not credit_check.get('valid', False):
                        if credit_check.get('error') == 'Invalid API key':
                            return jsonify({
                                "status": "error",
                                "message": "Invalid or inactive API key",
                                "error_code": "invalid_api_key"
                            }), 401
                        else:
                            return jsonify({
                                "status": "error",
                                "message": "Insufficient credits",
                                "error_code": "insufficient_credits",
                                "current_credits": credit_check.get('current_credits', 0),
                                "credits_needed": credit_check.get('credits_needed', 1)
                            }), 402
                    
                    request.api_key = api_key
                    request.credit_info = credit_check
                    
                except ImportError as e:
                    logger.error(f"Credit manager import error: {e}")
                    return jsonify({
                        "status": "error",
                        "message": "Credit verification system unavailable"
                    }), 503
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"API key verification error: {e}")
                return jsonify({
                    "status": "error",
                    "message": "Authentication failed"
                }), 401
                
        return decorated_function
    return decorator

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

# Import and register auth endpoints
from api_gateway.auth_endpoints import auth_bp

# Register multimodal and auth endpoint blueprints
app.register_blueprint(voice_bp)
app.register_blueprint(vision_bp)
app.register_blueprint(realtime_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(auth_bp)

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

# SERVICE ENDPOINTS (Require API Key)
@app.route("/api/v1/agent/create", methods=["POST"])
@check_api_key_and_credits(estimated_tokens=50)
def create_agent():
    """Create a new AI agent session - SERVICE ENDPOINT"""
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
@check_api_key_and_credits(estimated_tokens=150)
def send_message(session_id: str):
    """Send a message to an agent session - SERVICE ENDPOINT"""
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
                            
                            # Record detailed multi-service usage and deduct credits
                            if hasattr(request, 'api_key') and hasattr(request, 'credit_info'):
                                # Get token usage from OpenAI completion
                                input_tokens = completion.usage.prompt_tokens if completion.usage else 75
                                output_tokens = completion.usage.completion_tokens if completion.usage else 75
                                total_tokens = completion.usage.total_tokens if completion.usage else 150
                                
                                # Determine model from adapter settings or default
                                model_name = "gpt-4o-mini"  # Default
                                if agent_config.custom_settings:
                                    service_config = agent_config.custom_settings.get('service_configuration', {})
                                    if 'primary_ai_model' in service_config:
                                        model_name = service_config['primary_ai_model']
                                
                                try:
                                    # Start multi-service workflow tracking
                                    from billing.multi_service_tracker import MultiServiceTracker, ServiceType, WorkflowTemplates
                                    multi_tracker = MultiServiceTracker()
                                    
                                    # Determine workflow type based on adapter
                                    workflow_name = "text_chat"
                                    if agent_config.business_logic_adapter == "emergencyservices":
                                        workflow_name = "emergency_text_chat"
                                    elif agent_config.business_logic_adapter == "languagelearning":
                                        workflow_name = "language_learning_chat"
                                    
                                    workflow_id = multi_tracker.start_workflow_tracking(
                                        api_key=request.api_key,
                                        user_id=request.credit_info['user_id'],
                                        workflow_name=workflow_name,
                                        endpoint="/api/v1/agent/message",
                                        session_id=session_id,
                                        business_adapter=agent_config.business_logic_adapter
                                    )
                                    
                                    # Add AI model usage
                                    multi_tracker.add_service_usage(
                                        workflow_id=workflow_id,
                                        service_type=ServiceType.GPT,
                                        provider=model_name,
                                        units_consumed=total_tokens,
                                        unit_type="tokens",
                                        metadata={
                                            "input_tokens": input_tokens,
                                            "output_tokens": output_tokens,
                                            "business_adapter": agent_config.business_logic_adapter
                                        }
                                    )
                                    
                                    # Complete workflow and get total credits
                                    workflow_result = multi_tracker.complete_workflow(workflow_id, status_code=200)
                                    
                                    if workflow_result.get('success'):
                                        credits_to_deduct = workflow_result['total_credits_used']
                                        
                                        # Deduct credits from user balance
                                        from billing.credit_manager import LocalCreditManager
                                        credit_manager = LocalCreditManager()
                                        deduction_result = credit_manager.deduct_credits(
                                            user_id=request.credit_info['user_id'],
                                            credits=credits_to_deduct,
                                            description=f"Multi-service workflow '{workflow_name}': {total_tokens} tokens for {model_name}"
                                        )
                                        
                                        if not deduction_result.get('success', False):
                                            logger.warning(f"Failed to deduct credits: {deduction_result}")
                                        else:
                                            logger.info(f"Workflow '{workflow_name}': Deducted {credits_to_deduct} credits. New balance: {deduction_result['new_balance']}")
                                    
                                except ImportError as e:
                                    logger.warning(f"Multi-service tracking not available: {e}")
                                    # Fallback to basic tracking
                                    from billing.api_usage_tracker import APIUsageTracker, ModelPricing
                                    usage_tracker = APIUsageTracker()
                                    cost_breakdown = ModelPricing.calculate_cost_and_credits(model_name, input_tokens, output_tokens)
                                    credits_to_deduct = cost_breakdown["credits_used"]
                                    
                                    from billing.credit_manager import LocalCreditManager
                                    credit_manager = LocalCreditManager()
                                    credit_manager.deduct_credits(
                                        user_id=request.credit_info['user_id'],
                                        credits=credits_to_deduct,
                                        description=f"Basic AI usage: {total_tokens} tokens for {model_name}"
                                    )
                                except Exception as e:
                                    logger.error(f"Error in multi-service tracking: {e}")
                            
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
@check_api_key_and_credits(estimated_tokens=10)
def get_messages(session_id: str):
    """Get messages from an agent session - SERVICE ENDPOINT"""
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
@check_api_key_and_credits(estimated_tokens=5)
def get_session_status(session_id: str):
    """Get status of an agent session - SERVICE ENDPOINT"""
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
@check_api_key_and_credits(estimated_tokens=5)
def delete_session(session_id: str):
    """Delete an agent session - SERVICE ENDPOINT"""
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

# PUBLIC ENDPOINTS (No authentication required)
@app.route("/api/v1/usage/<client_id>", methods=["GET"])
def get_usage_summary(client_id: str):
    """Get usage summary for billing - PUBLIC ENDPOINT"""
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
    """Get billing information for a client - PUBLIC ENDPOINT"""
    try:
        # Parse parameters
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.now()

        # Get usage summary (credit-based)
        usage_summary = asyncio.run(usage_tracker.get_usage_summary(
            agent_id=client_id,
            start_date=start_date,
            end_date=end_date
        ))

        # Calculate credit usage (assume 1 message = 1 credit, 1 image = 5 credits, 1 minute voice = 2 credits)
        credits_used = usage_summary.get("messages", 0) * 1 \
            + usage_summary.get("images", 0) * 5 \
            + usage_summary.get("total_duration_minutes", 0) * 2

        bill = {
            "client_id": client_id,
            "billing_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "usage": usage_summary,
            "credits_used": credits_used,
            "credit_rate": {
                "message": 1,
                "image": 5,
                "minute": 2
            }
        }

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
    """List all active agent sessions - PUBLIC ENDPOINT"""
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
    """Readiness check for Kubernetes - PUBLIC ENDPOINT"""
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

# CREDIT MANAGEMENT ENDPOINTS (Public for now, could be restricted later)
@app.route("/api/v1/user/<user_id>/credits", methods=["GET"])
def get_user_credits(user_id: str):
    """Get user's current credit balance - PUBLIC ENDPOINT"""
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
