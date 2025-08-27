"""
Shared state for Universal AI Agent Platform
Manages global session and queue state
"""

import queue
from typing import Dict, Any

# Global state management
active_sessions: Dict[str, Dict] = {}
message_queues: Dict[str, queue.Queue] = {}