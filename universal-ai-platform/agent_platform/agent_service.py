"""
Universal AI Agent Platform - Core Service
Built on LiveKit foundation for multimodal AI agent capabilities
"""

import os
import asyncio
import base64
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext, JobContext, get_job_context
from livekit.agents.llm import ImageContent
from livekit.agents.utils.images import encode, EncodeOptions, ResizeOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import from relative paths
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from adapters.business_logic_adapter import BusinessLogicAdapter
from billing.usage_tracker import UsageTracker

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for agent instances"""
    agent_id: str
    instructions: str
    capabilities: list[str]  # ["voice", "vision", "text"]
    business_logic_adapter: Optional[str] = None
    custom_settings: Dict[str, Any] = None

    def to_dict(self):
        return asdict(self)

class UniversalAgent(Agent):
    """Universal multimodal AI agent with business logic injection"""
    
    def __init__(self, config: AgentConfig, usage_tracker: UsageTracker) -> None:
        self.config = config
        self.usage_tracker = usage_tracker
        self._latest_frame = None
        self._video_stream = None
        self._tasks = []
        self._business_adapter = None
        
        # Load business logic adapter if specified
        if config.business_logic_adapter:
            self._business_adapter = BusinessLogicAdapter.load(config.business_logic_adapter)
        
        super().__init__(instructions=config.instructions)
    
    async def on_enter(self):
        """Initialize agent when entering room"""
        room = get_job_context().room
        
        # Track session start
        await self.usage_tracker.track_session_start(self.config.agent_id, room.name)
        
        # Set up vision capabilities if enabled
        if "vision" in self.config.capabilities:
            await self._setup_vision_capabilities(room)
        
        # Apply business logic if adapter is loaded
        if self._business_adapter:
            await self._business_adapter.on_agent_enter(self, room)
    
    async def _setup_vision_capabilities(self, room):
        """Set up video stream handling for vision capabilities"""
        def _image_received_handler(reader, participant_identity):
            task = asyncio.create_task(
                self._image_received(reader, participant_identity)
            )
            self._tasks.append(task)
            task.add_done_callback(lambda t: self._tasks.remove(t))
        
        room.register_byte_stream_handler("images", _image_received_handler)
        
        # Look for existing video tracks
        for participant in room.remote_participants.values():
            video_tracks = [
                publication.track for publication in participant.track_publications.values() 
                if publication.track and publication.track.kind == rtc.TrackKind.KIND_VIDEO
            ]
            if video_tracks:
                self._create_video_stream(video_tracks[0])
                break
        
        # Watch for new video tracks
        @room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                self._create_video_stream(track)
    
    async def _image_received(self, reader, participant_identity):
        """Handle images uploaded from the frontend"""
        image_bytes = bytes()
        async for chunk in reader:
            image_bytes += chunk

        # Track image processing usage
        await self.usage_tracker.track_image_processed(self.config.agent_id)

        chat_ctx = self.chat_ctx.copy()
        
        # Apply business logic to image processing if available
        if self._business_adapter:
            processed_content = await self._business_adapter.process_image(image_bytes, chat_ctx)
            if processed_content:
                chat_ctx.add_message(role="user", content=processed_content)
                await self.update_chat_ctx(chat_ctx)
                return

        # Default image processing
        chat_ctx.add_message(
            role="user",
            content=[
                "Here's an image I want to share with you:",
                ImageContent(
                    image=f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                )
            ],
        )
        await self.update_chat_ctx(chat_ctx)
    
    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: dict) -> None:
        """Handle completion of user turn"""
        # Track message processing
        await self.usage_tracker.track_message_processed(self.config.agent_id)
        
        # Add latest video frame if available and vision is enabled
        if "vision" in self.config.capabilities and self._latest_frame:
            if isinstance(new_message.content, list):
                new_message.content.append(ImageContent(image=self._latest_frame))
            else:
                new_message.content = [new_message.content, ImageContent(image=self._latest_frame)]
            self._latest_frame = None
        
        # Apply business logic processing
        if self._business_adapter:
            await self._business_adapter.on_user_turn_completed(turn_ctx, new_message)
    
    def _create_video_stream(self, track: rtc.Track):
        """Create video stream for processing frames"""
        if self._video_stream is not None:
            self._video_stream.close()

        self._video_stream = rtc.VideoStream(track)
        
        async def read_stream():
            async for event in self._video_stream:
                image_bytes = encode(
                    event.frame,
                    EncodeOptions(
                        format="JPEG",
                        resize_options=ResizeOptions(
                            width=1024,
                            height=1024,
                            strategy="scale_aspect_fit"
                        )
                    )
                )
                self._latest_frame = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
        
        task = asyncio.create_task(read_stream())
        self._tasks.append(task)
        task.add_done_callback(lambda t: self._tasks.remove(t) if t in self._tasks else None)

class PlatformService:
    """Main platform service for managing agent instances"""
    
    def __init__(self):
        self.usage_tracker = UsageTracker()
        self.active_agents: Dict[str, UniversalAgent] = {}
        
    async def create_agent_session(self, config: AgentConfig) -> AgentSession:
        """Create a new agent session with specified configuration"""
        
        # Determine STT, LLM, TTS based on capabilities and settings
        stt = deepgram.STT(model="nova-3", language="multi") if "voice" in config.capabilities else None
        
        # Choose LLM model based on vision requirements
        llm_model = "gpt-4o" if "vision" in config.capabilities else "gpt-4o-mini"
        llm = openai.LLM(model=llm_model)
        
        tts = cartesia.TTS(
            model="sonic-2", 
            voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"
        ) if "voice" in config.capabilities else None
        
        vad = silero.VAD.load() if "voice" in config.capabilities else None
        turn_detection = MultilingualModel() if "voice" in config.capabilities else None
        
        # Create universal agent instance
        agent = UniversalAgent(config, self.usage_tracker)
        self.active_agents[config.agent_id] = agent
        
        # Create session
        session = AgentSession(
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad,
            turn_detection=turn_detection,
        )
        
        return session, agent
    
    async def entrypoint(self, ctx: agents.JobContext, config: AgentConfig):
        """Main entrypoint for agent sessions"""
        try:
            session, agent = await self.create_agent_session(config)
            
            # Determine room input options based on capabilities
            video_enabled = "vision" in config.capabilities
            noise_cancellation_enabled = "voice" in config.capabilities
            
            room_input_options = RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC() if noise_cancellation_enabled else None,
                video_enabled=video_enabled,
            )
            
            await session.start(
                room=ctx.room,
                agent=agent,
                room_input_options=room_input_options,
            )

            # Generate initial greeting based on capabilities
            greeting = self._generate_greeting(config.capabilities)
            await session.generate_reply(instructions=greeting)
            
        except Exception as e:
            logger.error(f"Error in agent session {config.agent_id}: {e}")
            raise
        finally:
            # Clean up
            if config.agent_id in self.active_agents:
                del self.active_agents[config.agent_id]
    
    def _generate_greeting(self, capabilities: list[str]) -> str:
        """Generate appropriate greeting based on agent capabilities"""
        if "vision" in capabilities and "voice" in capabilities:
            return "Hello! I'm your multimodal AI assistant. I can see, hear, and speak with you. How can I help you today?"
        elif "vision" in capabilities:
            return "Hello! I'm your vision-enabled AI assistant. I can analyze images and text. What would you like me to help you with?"
        elif "voice" in capabilities:
            return "Hello! I'm your voice AI assistant. I can hear and speak with you. How can I assist you today?"
        else:
            return "Hello! I'm your AI assistant. How can I help you today?"

# Global platform service instance
platform_service = PlatformService()

def get_platform_service() -> PlatformService:
    """Get the global platform service instance"""
    return platform_service