"""
Main entry point for the Universal AI Agent Platform
Starts the LiveKit agent service
"""

import os
import logging
import asyncio
from livekit import agents
from dotenv import load_dotenv

from agent_service import AgentConfig, get_platform_service

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint for LiveKit agents"""
    logger.info(f"Starting agent session for room: {ctx.room.name}")
    
    # Default configuration - can be customized via room metadata or other means
    config = AgentConfig(
        agent_id=f"agent_{ctx.room.name}",
        instructions="You are a helpful multimodal AI assistant with voice and vision capabilities.",
        capabilities=["voice", "vision", "text"],
        business_logic_adapter=None,  # Can be set based on room metadata
        custom_settings={}
    )
    
    # Check for room metadata to customize the agent
    room_metadata = ctx.room.metadata
    if room_metadata:
        try:
            import json
            metadata = json.loads(room_metadata)
            
            # Update config based on metadata
            if "instructions" in metadata:
                config.instructions = metadata["instructions"]
            if "capabilities" in metadata:
                config.capabilities = metadata["capabilities"]
            if "business_logic_adapter" in metadata:
                config.business_logic_adapter = metadata["business_logic_adapter"]
            if "custom_settings" in metadata:
                config.custom_settings = metadata["custom_settings"]
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse room metadata: {e}")
    
    # Get platform service and run agent
    platform_service = get_platform_service()
    await platform_service.entrypoint(ctx, config)

if __name__ == "__main__":
    logger.info("Starting Universal AI Agent Platform")
    
    # Verify required environment variables
    required_vars = ["OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these in your .env file")
        exit(1)
    
    # Start the LiveKit agent service
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))