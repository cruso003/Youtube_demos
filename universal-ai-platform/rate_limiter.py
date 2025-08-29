"""
Rate Limiting for NexusAI - Freemium Model
Implements IP-based rate limiting for free tier users
"""

import time
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

class FreemiumRateLimiter:
    """
    Rate limiter for freemium model:
    - Free tier: 50 messages/day, 1000/month per IP
    - No authentication required for free tier
    - Encourages adoption while preventing abuse
    """
    
    def __init__(self):
        # IP-based tracking for free tier
        self.daily_usage = defaultdict(int)  # ip -> daily_count
        self.monthly_usage = defaultdict(int)  # ip -> monthly_count
        self.last_reset = defaultdict(lambda: datetime.now())  # ip -> last_reset_time
        
        # Free tier limits
        self.DAILY_FREE_LIMIT = 50
        self.MONTHLY_FREE_LIMIT = 1000
        
        # Rate limiting windows
        self.request_times = defaultdict(deque)  # ip -> deque of request timestamps
        self.RATE_WINDOW = 60  # 1 minute window
        self.RATE_LIMIT = 30   # 30 requests per minute
    
    def is_allowed(self, ip_address: str, api_key: Optional[str] = None) -> Tuple[bool, Dict]:
        """
        Check if request is allowed under freemium model
        
        Args:
            ip_address: Client IP address
            api_key: Optional API key for paid users
            
        Returns:
            (allowed, info_dict)
        """
        
        # Paid users (with API key) have no limits
        if api_key:
            return True, {
                "tier": "paid",
                "limit_type": "unlimited",
                "remaining": "unlimited"
            }
        
        # Free tier users - check limits
        now = datetime.now()
        
        # Reset daily counter if needed
        if (now - self.last_reset[ip_address]).days >= 1:
            self.daily_usage[ip_address] = 0
            self.last_reset[ip_address] = now
        
        # Reset monthly counter if needed
        if (now - self.last_reset[ip_address]).days >= 30:
            self.monthly_usage[ip_address] = 0
        
        # Check rate limiting (requests per minute)
        current_time = time.time()
        request_times = self.request_times[ip_address]
        
        # Remove old requests outside the window
        while request_times and current_time - request_times[0] > self.RATE_WINDOW:
            request_times.popleft()
        
        # Check rate limit
        if len(request_times) >= self.RATE_LIMIT:
            return False, {
                "tier": "free",
                "limit_type": "rate_limit",
                "error": f"Rate limit exceeded: {self.RATE_LIMIT} requests per minute",
                "retry_after": self.RATE_WINDOW
            }
        
        # Check daily limit
        if self.daily_usage[ip_address] >= self.DAILY_FREE_LIMIT:
            return False, {
                "tier": "free",
                "limit_type": "daily_limit",
                "error": f"Daily limit exceeded: {self.DAILY_FREE_LIMIT} messages per day",
                "daily_remaining": 0,
                "monthly_remaining": max(0, self.MONTHLY_FREE_LIMIT - self.monthly_usage[ip_address])
            }
        
        # Check monthly limit
        if self.monthly_usage[ip_address] >= self.MONTHLY_FREE_LIMIT:
            return False, {
                "tier": "free", 
                "limit_type": "monthly_limit",
                "error": f"Monthly limit exceeded: {self.MONTHLY_FREE_LIMIT} messages per month",
                "upgrade_message": "Upgrade to Business tier for unlimited access"
            }
        
        # Request allowed - update counters
        request_times.append(current_time)
        self.daily_usage[ip_address] += 1
        self.monthly_usage[ip_address] += 1
        
        return True, {
            "tier": "free",
            "limit_type": "within_limits",
            "daily_remaining": self.DAILY_FREE_LIMIT - self.daily_usage[ip_address],
            "monthly_remaining": self.MONTHLY_FREE_LIMIT - self.monthly_usage[ip_address],
            "rate_remaining": self.RATE_LIMIT - len(request_times)
        }
    
    def get_usage_stats(self, ip_address: str) -> Dict:
        """Get current usage statistics for an IP"""
        return {
            "daily_used": self.daily_usage[ip_address],
            "daily_limit": self.DAILY_FREE_LIMIT,
            "monthly_used": self.monthly_usage[ip_address],
            "monthly_limit": self.MONTHLY_FREE_LIMIT,
            "last_reset": self.last_reset[ip_address].isoformat() if ip_address in self.last_reset else None
        }

# Global rate limiter instance
rate_limiter = FreemiumRateLimiter()
