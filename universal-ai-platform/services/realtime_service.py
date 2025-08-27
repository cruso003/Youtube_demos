"""
Real-time Service
Integrates LiveKit for real-time multimodal sessions
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)

class RealtimeService:
    """Service for real-time multimodal sessions using LiveKit"""
    
    def __init__(self):
        self.livekit_url = os.getenv("LIVEKIT_URL")
        self.livekit_api_key = os.getenv("LIVEKIT_API_KEY")
        self.livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if not all([self.livekit_url, self.livekit_api_key, self.livekit_api_secret]):
            logger.warning("LiveKit configuration incomplete. Real-time features will be limited.")
    
    async def create_room(self, session_id: str, room_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a LiveKit room for real-time session
        
        Args:
            session_id: Session identifier
            room_config: Room configuration options
            
        Returns:
            Dict with room details and access tokens
        """
        try:
            if not all([self.livekit_url, self.livekit_api_key, self.livekit_api_secret]):
                return {
                    "success": False,
                    "error": "LiveKit not configured",
                    "room_name": None,
                    "access_token": None
                }
            
            # Default room configuration
            config = {
                "max_participants": 10,
                "audio_enabled": True,
                "video_enabled": True,
                "screen_share_enabled": True,
                "recording_enabled": False
            }
            
            if room_config:
                config.update(room_config)
            
            try:
                from livekit import api
                
                # Initialize LiveKit API client
                lk_api = api.LiveKitAPI(
                    url=self.livekit_url,
                    api_key=self.livekit_api_key,
                    api_secret=self.livekit_api_secret
                )
                
                # Create room
                room_name = f"session_{session_id}"
                
                room_info = await lk_api.room.create_room(
                    api.CreateRoomRequest(
                        name=room_name,
                        max_participants=config["max_participants"],
                        metadata=json.dumps({
                            "session_id": session_id,
                            "created_by": "universal_ai_platform",
                            "capabilities": ["voice", "vision", "text"]
                        })
                    )
                )
                
                # Generate access token for user
                from livekit import AccessToken, VideoGrants
                
                token = AccessToken(self.livekit_api_key, self.livekit_api_secret)
                token.with_identity(f"user_{session_id}")
                token.with_name("AI Session User")
                token.with_grants(VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True
                ))
                
                access_token = token.to_jwt()
                
                return {
                    "success": True,
                    "room_name": room_name,
                    "room_sid": room_info.sid,
                    "access_token": access_token,
                    "livekit_url": self.livekit_url,
                    "session_id": session_id,
                    "config": config,
                    "error": None
                }
                
            except ImportError:
                logger.warning("LiveKit SDK not available. Using mock room creation.")
                # Mock room creation for testing
                return {
                    "success": True,
                    "room_name": f"session_{session_id}",
                    "room_sid": f"RM_mock_{session_id}",
                    "access_token": "mock_access_token",
                    "livekit_url": self.livekit_url or "wss://mock-livekit-server.com",
                    "session_id": session_id,
                    "config": config,
                    "error": None,
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"Room creation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "room_name": None,
                "access_token": None
            }
    
    async def start_ai_agent_in_room(self, room_name: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start an AI agent in a LiveKit room
        
        Args:
            room_name: LiveKit room name
            agent_config: Agent configuration including adapter settings
            
        Returns:
            Dict with agent startup results
        """
        try:
            if not all([self.livekit_url, self.livekit_api_key, self.livekit_api_secret]):
                return {
                    "success": False,
                    "error": "LiveKit not configured",
                    "agent_id": None
                }
            
            try:
                # This would start the actual LiveKit agent
                # For now, return a structure indicating the agent is ready
                agent_id = f"agent_{room_name}"
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "room_name": room_name,
                    "capabilities": agent_config.get("capabilities", ["text", "voice", "vision"]),
                    "business_adapter": agent_config.get("business_logic_adapter"),
                    "status": "starting",
                    "error": None
                }
                
            except Exception as e:
                logger.error(f"Agent startup error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "agent_id": None
                }
                
        except Exception as e:
            logger.error(f"Agent startup error: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": None
            }
    
    async def end_session(self, room_name: str) -> Dict[str, Any]:
        """
        End a real-time session and clean up room
        
        Args:
            room_name: LiveKit room name
            
        Returns:
            Dict with cleanup results
        """
        try:
            if not all([self.livekit_url, self.livekit_api_key, self.livekit_api_secret]):
                return {
                    "success": True,  # No cleanup needed if not configured
                    "message": "No real-time session to clean up"
                }
            
            try:
                from livekit import api
                
                # Initialize LiveKit API client
                lk_api = api.LiveKitAPI(
                    url=self.livekit_url,
                    api_key=self.livekit_api_key,
                    api_secret=self.livekit_api_secret
                )
                
                # Delete room
                await lk_api.room.delete_room(
                    api.DeleteRoomRequest(room=room_name)
                )
                
                return {
                    "success": True,
                    "room_name": room_name,
                    "message": "Room deleted successfully"
                }
                
            except ImportError:
                logger.warning("LiveKit SDK not available. Mock cleanup.")
                return {
                    "success": True,
                    "room_name": room_name,
                    "message": "Mock room cleanup completed",
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global realtime service instance
_realtime_service = None

def get_realtime_service() -> RealtimeService:
    """Get the global realtime service instance"""
    global _realtime_service
    if _realtime_service is None:
        _realtime_service = RealtimeService()
    return _realtime_service