"""
Phone Service
Integrates Twilio for phone call capabilities
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)

class PhoneService:
    """Service for phone integration using Twilio"""
    
    def __init__(self):
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.twilio_account_sid, self.twilio_auth_token]):
            logger.warning("Twilio configuration incomplete. Phone features will be disabled.")
    
    async def initiate_call(self, to_number: str, session_id: str, adapter_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initiate a phone call via Twilio
        
        Args:
            to_number: Phone number to call (E.164 format)
            session_id: Session identifier for call tracking
            adapter_config: Business adapter configuration for call handling
            
        Returns:
            Dict with call initiation results
        """
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
                return {
                    "success": False,
                    "error": "Twilio not configured",
                    "call_sid": None
                }
            
            try:
                from twilio.rest import Client
                
                # Initialize Twilio client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                
                # Prepare TwiML URL for call handling
                twiml_url = self._get_twiml_url(session_id, adapter_config)
                
                # Create call
                call = client.calls.create(
                    to=to_number,
                    from_=self.twilio_phone_number,
                    url=twiml_url,
                    method='POST',
                    record=True,  # Record for quality assurance
                    timeout=30,   # Ring for 30 seconds
                    status_callback=self._get_status_callback_url(session_id),
                    status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                    status_callback_method='POST'
                )
                
                return {
                    "success": True,
                    "call_sid": call.sid,
                    "to_number": to_number,
                    "from_number": self.twilio_phone_number,
                    "session_id": session_id,
                    "status": "initiated",
                    "twiml_url": twiml_url,
                    "error": None
                }
                
            except ImportError:
                logger.warning("Twilio SDK not available. Using mock call initiation.")
                # Mock call initiation for testing
                return {
                    "success": True,
                    "call_sid": f"CA_mock_{session_id}",
                    "to_number": to_number,
                    "from_number": self.twilio_phone_number or "+15551234567",
                    "session_id": session_id,
                    "status": "initiated",
                    "twiml_url": f"https://mock-server.com/twiml/{session_id}",
                    "error": None,
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"Call initiation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "call_sid": None
            }
    
    async def handle_call_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Twilio webhook for call events
        
        Args:
            webhook_data: Webhook payload from Twilio
            
        Returns:
            Dict with TwiML response
        """
        try:
            call_sid = webhook_data.get("CallSid")
            call_status = webhook_data.get("CallStatus")
            session_id = webhook_data.get("session_id")  # Custom parameter
            
            logger.info(f"Call webhook: {call_sid} - Status: {call_status}")
            
            if call_status == "in-progress":
                # Call answered, connect to LiveKit room
                twiml_response = self._generate_connect_twiml(session_id)
            elif call_status == "completed":
                # Call ended, clean up
                twiml_response = self._generate_hangup_twiml()
            else:
                # Default response
                twiml_response = self._generate_default_twiml()
            
            return {
                "success": True,
                "twiml_response": twiml_response,
                "call_sid": call_sid,
                "status": call_status
            }
            
        except Exception as e:
            logger.error(f"Webhook handling error: {e}")
            return {
                "success": False,
                "error": str(e),
                "twiml_response": self._generate_error_twiml()
            }
    
    async def end_call(self, call_sid: str) -> Dict[str, Any]:
        """
        End an active call
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Dict with call termination results
        """
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token]):
                return {
                    "success": False,
                    "error": "Twilio not configured"
                }
            
            try:
                from twilio.rest import Client
                
                # Initialize Twilio client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                
                # Update call to completed status
                call = client.calls(call_sid).update(status='completed')
                
                return {
                    "success": True,
                    "call_sid": call_sid,
                    "status": call.status,
                    "message": "Call ended successfully"
                }
                
            except ImportError:
                logger.warning("Twilio SDK not available. Using mock call termination.")
                return {
                    "success": True,
                    "call_sid": call_sid,
                    "status": "completed",
                    "message": "Mock call ended successfully",
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"Call termination error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_twiml_url(self, session_id: str, adapter_config: Dict[str, Any] = None) -> str:
        """Get TwiML URL for call handling"""
        base_url = os.getenv("PLATFORM_BASE_URL", "https://your-platform.com")
        return f"{base_url}/api/v1/phone/twiml/{session_id}"
    
    def _get_status_callback_url(self, session_id: str) -> str:
        """Get status callback URL for call events"""
        base_url = os.getenv("PLATFORM_BASE_URL", "https://your-platform.com")
        return f"{base_url}/api/v1/phone/status/{session_id}"
    
    def _generate_connect_twiml(self, session_id: str) -> str:
        """Generate TwiML to connect call to LiveKit room"""
        # This would generate TwiML to connect the call to a LiveKit room
        # For now, return a simple greeting
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello, you are connected to the AI assistant. Please wait while we connect you to your session.</Say>
    <Pause length="1"/>
    <Say voice="alice">Your session ID is {session_id}. How can I help you today?</Say>
</Response>"""
    
    def _generate_hangup_twiml(self) -> str:
        """Generate TwiML to end the call"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Thank you for using our service. Goodbye.</Say>
    <Hangup/>
</Response>"""
    
    def _generate_default_twiml(self) -> str:
        """Generate default TwiML response"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Welcome to the AI assistant service.</Say>
</Response>"""
    
    def _generate_error_twiml(self) -> str:
        """Generate error TwiML response"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">We're sorry, there was an error processing your call. Please try again later.</Say>
    <Hangup/>
</Response>"""

# Global phone service instance
_phone_service = None

def get_phone_service() -> PhoneService:
    """Get the global phone service instance"""
    global _phone_service
    if _phone_service is None:
        _phone_service = PhoneService()
    return _phone_service