"""
Mock Agent Platform for testing without LiveKit dependencies
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

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

class MockPlatformService:
    """Mock platform service for testing"""
    
    def __init__(self):
        self.active_agents = {}
    
    async def create_agent(self, config: AgentConfig):
        """Create a mock agent"""
        self.active_agents[config.agent_id] = config
        return {"status": "success", "agent_id": config.agent_id}
    
    async def get_agent(self, agent_id: str):
        """Get a mock agent"""
        return self.active_agents.get(agent_id)

def get_platform_service():
    """Get the mock platform service"""
    return MockPlatformService()