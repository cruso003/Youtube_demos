from flask import Blueprint, request, jsonify
from billing.models import User, APIKey, CreditTransaction
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import bcrypt
import jwt
import uuid
import os
import logging
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

# Setup DB connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nexusai")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

auth_bp = Blueprint('auth', __name__)

def require_jwt_auth(required_roles=None):
    """Decorator for dashboard/management endpoints requiring JWT authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Missing JWT token'}), 401
                
                token = auth_header.replace('Bearer ', '')
                
                # Reject API keys on dashboard endpoints
                if token.startswith('nexus_'):
                    return jsonify({'error': 'Use JWT token, not API key for this endpoint'}), 401
                
                try:
                    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                    request.current_user = payload
                    
                    # Check role permissions if specified
                    if required_roles and payload.get('role') not in required_roles:
                        return jsonify({'error': 'Insufficient permissions'}), 403
                        
                except jwt.ExpiredSignatureError:
                    return jsonify({'error': 'Token has expired'}), 401
                except jwt.InvalidTokenError:
                    return jsonify({'error': 'Invalid token'}), 401
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': 'Authentication failed'}), 401
                
        return decorated_function
    return decorator

# User registration
@auth_bp.route('/api/v1/auth/register', methods=['POST'])
def register():
    data = request.json
    required = ['email', 'name', 'password']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400
    
    session = Session()
    try:
        if session.query(User).filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        user = User(
            email=data['email'],
            name=data['name'],
            password=bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode(),
            role='USER',
            is_active=True
        )
        session.add(user)
        session.commit()
        return jsonify({'message': 'User registered', 'user_id': str(user.id)}), 201
    finally:
        session.close()

# User login - Returns JWT token for dashboard access
@auth_bp.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    session = Session()
    try:
        user = session.query(User).filter_by(email=data['email']).first()
        if not user or not bcrypt.checkpw(data['password'].encode(), user.password.encode()):
            return jsonify({'error': 'Invalid credentials'}), 401
        if not user.is_active:
            return jsonify({'error': 'User is inactive'}), 403
        
        # Generate JWT token for dashboard access
        token_payload = {
            'user_id': str(user.id),
            'email': user.email,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'user_id': str(user.id),
            'email': user.email,
            'role': user.role,
            'token': token,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRATION_HOURS * 3600
        }), 200
    finally:
        session.close()

# Generate API key for service consumption (requires email/password AND sufficient credits)
@auth_bp.route('/api/v1/auth/api-key', methods=['POST'])
def generate_api_key():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    session = Session()
    try:
        user = session.query(User).filter_by(email=data['email']).first()
        if not user or not bcrypt.checkpw(data['password'].encode(), user.password.encode()):
            return jsonify({'error': 'Invalid credentials'}), 401
        if not user.is_active:
            return jsonify({'error': 'User is inactive'}), 403

        # CRITICAL: Check if user has sufficient credits for API key generation
        from billing.credit_manager import LocalCreditManager
        credit_manager = LocalCreditManager()
        credit_check = credit_manager.can_generate_api_key(str(user.id))
        
        if not credit_check['can_generate']:
            if credit_check.get('is_first_key', True):
                message = f'First API key requires {credit_check["required_credits"]} credits (${credit_check["required_credits"]/1000}) to verify payment. You need {credit_check["deficit"]} more credits.'
            else:
                message = f'You need at least 1 credit to generate additional API keys. Current balance: {credit_check["current_credits"]} credits.'
            
            return jsonify({
                'error': 'Insufficient credits to generate API key',
                'current_credits': credit_check['current_credits'],
                'required_credits': credit_check['required_credits'],
                'deficit': credit_check['deficit'],
                'is_first_key': credit_check.get('is_first_key', True),
                'message': message
            }), 402  # Payment Required

        # Generate new API key (allow multiple keys per user)
        api_key_value = f"nexus_{uuid.uuid4().hex[:20]}"
        new_key = APIKey(user_id=user.id, api_key=api_key_value)
        session.add(new_key)
        session.commit()

        return jsonify({
            'message': 'API key generated successfully',
            'api_key': api_key_value,
            'user_id': str(user.id),
            'created_at': new_key.created_at.isoformat() if new_key.created_at else None,
            'current_credits': credit_check['current_credits']
        }), 201
    finally:
        session.close()

# Verify JWT token endpoint (for dashboard)
@auth_bp.route('/api/v1/auth/verify', methods=['GET'])
@require_jwt_auth()
def verify_token():
    return jsonify({
        'message': 'Token is valid',
        'user': request.current_user
    }), 200

# Refresh JWT token endpoint
@auth_bp.route('/api/v1/auth/refresh', methods=['POST'])
@require_jwt_auth()
def refresh_token():
    user_data = request.current_user
    
    # Generate new token
    token_payload = {
        'user_id': user_data['user_id'],
        'email': user_data['email'],
        'role': user_data['role'],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    new_token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'message': 'Token refreshed successfully',
        'token': new_token,
        'token_type': 'Bearer',
        'expires_in': JWT_EXPIRATION_HOURS * 3600
    }), 200

# List users (admin dashboard endpoint)
@auth_bp.route('/api/v1/users', methods=['GET'])
@require_jwt_auth(required_roles=['ADMIN', 'SUPER_ADMIN'])
def list_users():
    session = Session()
    try:
        users = session.query(User).all()
        return jsonify([
            {
                'id': str(u.id), 
                'email': u.email, 
                'name': u.name, 
                'role': u.role, 
                'is_active': u.is_active, 
                'created_at': u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ])
    finally:
        session.close()

# Get user by ID (dashboard endpoint)
@auth_bp.route('/api/v1/users/<user_id>', methods=['GET'])
@require_jwt_auth()
def get_user(user_id):
    # Users can only view their own profile unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'id': str(user.id), 
            'email': user.email, 
            'name': user.name, 
            'role': user.role, 
            'is_active': user.is_active, 
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    finally:
        session.close()

# Update user (dashboard endpoint)
@auth_bp.route('/api/v1/users/<user_id>', methods=['PUT'])
@require_jwt_auth()
def update_user(user_id):
    # Users can only update their own profile unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.json
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins can change role and is_active
        allowed_fields = ['name', 'email']
        if request.current_user.get('role') in ['ADMIN', 'SUPER_ADMIN']:
            allowed_fields.extend(['role', 'is_active'])
        
        for k in allowed_fields:
            if k in data:
                setattr(user, k, data[k])
        
        session.commit()
        return jsonify({'message': 'User updated'})
    finally:
        session.close()

# Change password (dashboard endpoint)
@auth_bp.route('/api/v1/users/<user_id>/password', methods=['POST'])
@require_jwt_auth()
def change_password(user_id):
    # Users can only change their own password unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.json
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Old password and new password required'}), 400
    
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Admins can change password without old password verification
        if request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']:
            if not bcrypt.checkpw(data['old_password'].encode(), user.password.encode()):
                return jsonify({'error': 'Old password incorrect'}), 401
        
        user.password = bcrypt.hashpw(data['new_password'].encode(), bcrypt.gensalt()).decode()
        session.commit()
        return jsonify({'message': 'Password changed'})
    finally:
        session.close()

# List API keys for user (dashboard endpoint)
@auth_bp.route('/api/v1/users/<user_id>/api-keys', methods=['GET'])
@require_jwt_auth()
def list_api_keys(user_id):
    # Users can only view their own API keys unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    session = Session()
    try:
        keys = session.query(APIKey).filter_by(user_id=user_id).all()
        return jsonify([
            {
                'id': str(k.id), 
                'api_key': k.api_key, 
                'created_at': k.created_at.isoformat() if k.created_at else None, 
                'revoked': k.revoked
            }
            for k in keys
        ])
    finally:
        session.close()

# Create API key for user (dashboard endpoint)
@auth_bp.route('/api/v1/users/<user_id>/api-keys', methods=['POST'])
@require_jwt_auth()
def create_api_key(user_id):
    # Users can only create API keys for themselves unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # CRITICAL: Check if user has sufficient credits for API key generation
        from billing.credit_manager import LocalCreditManager
        credit_manager = LocalCreditManager()
        credit_check = credit_manager.can_generate_api_key(user_id)
        
        if not credit_check['can_generate']:
            return jsonify({
                'error': 'Insufficient credits to generate API key',
                'current_credits': credit_check['current_credits'],
                'required_credits': credit_check['required_credits'],
                'deficit': credit_check['deficit'],
                'message': f'User needs {credit_check["deficit"]} more credits to generate an API key.'
            }), 402  # Payment Required
        
        api_key_value = f"nexus_{uuid.uuid4().hex[:20]}"
        key = APIKey(user_id=user_id, api_key=api_key_value)
        session.add(key)
        session.commit()
        
        return jsonify({
            'id': str(key.id), 
            'api_key': key.api_key, 
            'created_at': key.created_at.isoformat() if key.created_at else None, 
            'revoked': key.revoked,
            'current_credits': credit_check['current_credits']
        })
    finally:
        session.close()

# Revoke API key (dashboard endpoint)
@auth_bp.route('/api/v1/api-keys/<key_id>/revoke', methods=['POST'])
@require_jwt_auth()
def revoke_api_key(key_id):
    session = Session()
    try:
        key = session.query(APIKey).filter_by(id=key_id).first()
        if not key:
            return jsonify({'error': 'API key not found'}), 404
        
        # Users can only revoke their own API keys unless they're admin
        if (request.current_user.get('user_id') != str(key.user_id) and 
            request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        key.revoked = True
        session.commit()
        return jsonify({'message': 'API key revoked'})
    finally:
        session.close()

# List credit transactions for user (dashboard endpoint)
@auth_bp.route('/api/v1/users/<user_id>/credits', methods=['GET'])
@require_jwt_auth()
def list_credits(user_id):
    # Users can only view their own credits unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    session = Session()
    try:
        # Get current credit balance
        user = session.query(User).filter_by(id=user_id).first()
        current_balance = user.credit_balance if user else 0
        
        # Get credit transactions
        txs = session.query(CreditTransaction).filter_by(user_id=user_id).all()
        
        return jsonify({
            'current_balance': current_balance,
            'transactions': [
                {
                    'id': str(t.id), 
                    'credits': t.credits, 
                    'amount_usd': t.amount_usd, 
                    'transaction_id': t.transaction_id, 
                    'description': t.description, 
                    'created_at': t.created_at.isoformat() if t.created_at else None
                }
                for t in txs
            ]
        })
    finally:
        session.close()

# API Usage Analytics Endpoints
@auth_bp.route('/api/v1/users/<user_id>/usage/analytics', methods=['GET'])
@require_jwt_auth()
def get_usage_analytics(user_id):
    """Get detailed usage analytics for user across all API keys"""
    # Users can only view their own analytics unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    try:
        days = int(request.args.get('days', 30))  # Default to 30 days
        days = max(1, min(days, 365))  # Limit between 1-365 days
        
        from billing.api_usage_tracker import APIUsageTracker
        usage_tracker = APIUsageTracker()
        analytics = usage_tracker.get_usage_analytics_by_user(user_id, days)
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'analytics': analytics
        })
        
    except Exception as e:
        logger.error(f"Error getting usage analytics: {e}")
        return jsonify({
            'error': 'Failed to get usage analytics',
            'message': str(e)
        }), 500

@auth_bp.route('/api/v1/users/<user_id>/usage/models', methods=['GET'])
@require_jwt_auth()
def get_model_usage_breakdown(user_id):
    """Get cost breakdown by AI model for user"""
    # Users can only view their own analytics unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    try:
        days = int(request.args.get('days', 30))
        days = max(1, min(days, 365))
        
        from billing.api_usage_tracker import APIUsageTracker
        usage_tracker = APIUsageTracker()
        breakdown = usage_tracker.get_model_cost_breakdown(user_id, days)
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'model_breakdown': breakdown
        })
        
    except Exception as e:
        logger.error(f"Error getting model breakdown: {e}")
        return jsonify({
            'error': 'Failed to get model breakdown',
            'message': str(e)
        }), 500

@auth_bp.route('/api/v1/api-keys/<api_key>/usage', methods=['GET'])
@require_jwt_auth()
def get_api_key_usage(api_key):
    """Get usage records for specific API key"""
    session = Session()
    try:
        # Verify API key belongs to user (or user is admin)
        key_obj = session.query(APIKey).filter_by(api_key=api_key).first()
        if not key_obj:
            return jsonify({'error': 'API key not found'}), 404
        
        # Check permissions
        if (request.current_user.get('user_id') != str(key_obj.user_id) and 
            request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Get usage records
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 100))
        days = max(1, min(days, 365))
        limit = max(1, min(limit, 1000))
        
        from datetime import datetime, timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        from billing.api_usage_tracker import APIUsageTracker
        usage_tracker = APIUsageTracker()
        usage_records = usage_tracker.get_usage_by_api_key(api_key, start_date, limit=limit)
        
        return jsonify({
            'status': 'success',
            'api_key': f"{api_key[:8]}...{api_key[-4:]}",  # Masked for security
            'usage_records': usage_records,
            'period_days': days,
            'total_records': len(usage_records)
        })
        
    except Exception as e:
        logger.error(f"Error getting API key usage: {e}")
        return jsonify({
            'error': 'Failed to get API key usage',
            'message': str(e)
        }), 500
    finally:
        session.close()

@auth_bp.route('/api/v1/users/<user_id>/usage/summary', methods=['GET'])
@require_jwt_auth()
def get_usage_summary_endpoint(user_id):
    """Get simple usage summary with current credit balance"""
    # Users can only view their own summary unless they're admin
    if (request.current_user.get('user_id') != user_id and 
        request.current_user.get('role') not in ['ADMIN', 'SUPER_ADMIN']):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    session = Session()
    try:
        # Get current credit balance
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        current_balance = user.credit_balance or 0
        
        # Get usage analytics for last 7 days (quick summary)
        from billing.api_usage_tracker import APIUsageTracker
        usage_tracker = APIUsageTracker()
        analytics = usage_tracker.get_usage_analytics_by_user(user_id, days=7)
        
        # Get number of active API keys
        active_keys = session.query(APIKey).filter_by(user_id=user_id, revoked=False).count()
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'current_credit_balance': current_balance,
            'active_api_keys': active_keys,
            'last_7_days': {
                'total_requests': analytics.get('total_statistics', {}).get('total_requests', 0),
                'total_credits_used': analytics.get('total_statistics', {}).get('total_credits', 0),
                'total_cost': analytics.get('total_statistics', {}).get('total_cost', 0.0),
                'models_used': analytics.get('total_statistics', {}).get('models_used', [])
            },
            'top_consuming_keys': analytics.get('top_consuming_keys', [])[:3]  # Top 3
        })
        
    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        return jsonify({
            'error': 'Failed to get usage summary',
            'message': str(e)
        }), 500
    finally:
        session.close()
