"""
Freemium Rate Limiting for NexusAI
Very restrictive limits for testing purposes only
"""

import json
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
import os

# Store rate limit data (in production, use Redis)
RATE_LIMIT_STORE = {}

class FreemiumLimits:
    # Free tier - very restrictive for testing only
    FREE_DAILY_MESSAGES = 5
    FREE_MAX_SESSIONS = 1
    FREE_RATE_LIMIT = 60  # seconds between requests
    FREE_MAX_MESSAGE_LENGTH = 100
    FREE_ALLOWED_CAPABILITIES = ["text"]  # No voice, vision
    
    # Paid tiers
    STARTER_MONTHLY_MESSAGES = 1000
    STARTER_RATE_LIMIT = 1  # 1 second between requests
    
    BUSINESS_MONTHLY_MESSAGES = 10000
    BUSINESS_RATE_LIMIT = 0.5  # 2 requests per second

def get_client_id(request):
    """Get client identifier (IP + User-Agent for free tier)"""
    api_key = request.headers.get('Authorization')
    if api_key:
        return f"api_{api_key[-10:]}"  # Use last 10 chars of API key
    else:
        # Free tier - use IP + simplified user agent
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'unknown')[:20]
        return f"free_{ip}_{hash(user_agent) % 10000}"

def get_usage_data(client_id):
    """Get current usage data for client"""
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    
    if client_id not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[client_id] = {
            'daily_messages': {},
            'active_sessions': [],
            'last_request': 0,
            'plan': 'free'
        }
    
    data = RATE_LIMIT_STORE[client_id]
    
    # Clean old daily data (keep only today)
    data['daily_messages'] = {
        date: count for date, count in data['daily_messages'].items() 
        if date == today
    }
    
    # Clean old sessions (older than 1 hour)
    hour_ago = now - timedelta(hours=1)
    data['active_sessions'] = [
        session for session in data['active_sessions']
        if datetime.fromisoformat(session['created']) > hour_ago
    ]
    
    return data

def check_freemium_limits():
    """Decorator to check freemium limits"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = get_client_id(request)
            usage_data = get_usage_data(client_id)
            now = datetime.now()
            today = now.strftime('%Y-%m-%d')
            
            # Determine access tier
            api_key = request.headers.get('Authorization')
            access_tier = 'free' if not api_key else 'credit'  # Credit users have API keys
            
            # Check rate limiting
            time_since_last = time.time() - usage_data['last_request']
            if access_tier == 'free' and time_since_last < FreemiumLimits.FREE_RATE_LIMIT:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Free tier: Wait {FreemiumLimits.FREE_RATE_LIMIT} seconds between requests',
                    'retry_after': FreemiumLimits.FREE_RATE_LIMIT - time_since_last,
                    'upgrade_info': 'Purchase credits for faster access and more features'
                }), 429
            
            # Check daily message limits for free tier
            if access_tier == 'free':
                daily_count = usage_data['daily_messages'].get(today, 0)
                if daily_count >= FreemiumLimits.FREE_DAILY_MESSAGES:
                    return jsonify({
                        'error': 'Daily limit exceeded',
                        'message': f'Free tier: {FreemiumLimits.FREE_DAILY_MESSAGES} messages per day limit reached',
                        'usage': {
                            'messages_today': daily_count,
                            'limit': FreemiumLimits.FREE_DAILY_MESSAGES,
                            'resets_at': 'midnight UTC'
                        },
                        'upgrade_info': 'Purchase credits for unlimited messages'
                    }), 429
                
                # Check session limits for free tier
                if len(usage_data['active_sessions']) >= FreemiumLimits.FREE_MAX_SESSIONS:
                    return jsonify({
                        'error': 'Session limit exceeded',
                        'message': f'Free tier: Maximum {FreemiumLimits.FREE_MAX_SESSIONS} active session',
                        'upgrade_info': 'Purchase credits for unlimited sessions'
                    }), 429
            
            # Update usage
            usage_data['last_request'] = time.time()
            
            # Store access tier info for endpoint use
            g.client_id = client_id
            g.plan = access_tier
            g.usage_data = usage_data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_free_tier_request(data):
    """Validate request data for free tier restrictions"""
    if g.plan != 'free':
        return True, None
    
    # Check message length
    message = data.get('message', '')
    if len(message) > FreemiumLimits.FREE_MAX_MESSAGE_LENGTH:
        return False, {
            'error': 'Message too long',
            'message': f'Free tier: Maximum {FreemiumLimits.FREE_MAX_MESSAGE_LENGTH} characters per message',
            'current_length': len(message),
            'upgrade_info': 'Purchase credits for longer messages'
        }
    
    # Check capabilities
    capabilities = data.get('capabilities', ['text'])
    if not all(cap in FreemiumLimits.FREE_ALLOWED_CAPABILITIES for cap in capabilities):
        return False, {
            'error': 'Capabilities not allowed',
            'message': f'Free tier: Only {FreemiumLimits.FREE_ALLOWED_CAPABILITIES} capabilities allowed',
            'requested': capabilities,
            'upgrade_info': 'Purchase credits for voice and vision capabilities'
        }
    
    return True, None

def record_message_usage():
    """Record a message usage"""
    if hasattr(g, 'usage_data'):
        today = datetime.now().strftime('%Y-%m-%d')
        g.usage_data['daily_messages'][today] = g.usage_data['daily_messages'].get(today, 0) + 1

def record_session_creation(session_id):
    """Record a new session creation"""
    if hasattr(g, 'usage_data'):
        g.usage_data['active_sessions'].append({
            'session_id': session_id,
            'created': datetime.now().isoformat()
        })

def get_usage_info(client_id=None):
    """Get usage information for a client"""
    if not client_id:
        client_id = get_client_id(request)
    
    usage_data = get_usage_data(client_id)
    today = datetime.now().strftime('%Y-%m-%d')
    
    access_tier = 'free' if not request.headers.get('Authorization') else 'credit'
    
    if access_tier == 'free':
        return {
            'plan': 'free',
            'limits': {
                'messages_per_day': FreemiumLimits.FREE_DAILY_MESSAGES,
                'max_sessions': FreemiumLimits.FREE_MAX_SESSIONS,
                'rate_limit_seconds': FreemiumLimits.FREE_RATE_LIMIT,
                'max_message_length': FreemiumLimits.FREE_MAX_MESSAGE_LENGTH,
                'allowed_capabilities': FreemiumLimits.FREE_ALLOWED_CAPABILITIES
            },
            'usage': {
                'messages_today': usage_data['daily_messages'].get(today, 0),
                'active_sessions': len(usage_data['active_sessions'])
            },
            'upgrade_info': {
                'credit_system': 'Purchase credits starting at $5.00 for 5,000 credits',
                'benefits': 'No daily limits, all capabilities, faster response times'
            }
        }
    else:
        return {
            'plan': 'credit',
            'limits': {
                'credit_based': True,
                'unlimited_sessions': True,
                'all_capabilities': True
            },
            'usage': {
                'messages_today': usage_data['daily_messages'].get(today, 0)
            }
        }
