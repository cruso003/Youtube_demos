from flask import Blueprint, request, jsonify
from billing.models import User, APIKey, CreditTransaction
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import bcrypt
import jwt
import uuid
import os
from datetime import datetime, timedelta
from functools import wraps

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

# Generate API key for service consumption (requires email/password)
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

        # Check if user already has an active API key
        existing_key = session.query(APIKey).filter_by(user_id=user.id, revoked=False).first()
        if existing_key:
            return jsonify({
                'message': 'API key already exists',
                'api_key': existing_key.api_key,
                'created_at': existing_key.created_at.isoformat() if existing_key.created_at else None
            }), 200

        # Generate new API key
        api_key_value = f"nexus_{uuid.uuid4().hex[:20]}"
        new_key = APIKey(user_id=user.id, api_key=api_key_value)
        session.add(new_key)
        session.commit()

        return jsonify({
            'message': 'API key generated successfully',
            'api_key': api_key_value,
            'user_id': str(user.id),
            'created_at': new_key.created_at.isoformat() if new_key.created_at else None
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
        
        api_key_value = f"nexus_{uuid.uuid4().hex[:20]}"
        key = APIKey(user_id=user_id, api_key=api_key_value)
        session.add(key)
        session.commit()
        
        return jsonify({
            'id': str(key.id), 
            'api_key': key.api_key, 
            'created_at': key.created_at.isoformat() if key.created_at else None, 
            'revoked': key.revoked
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
        txs = session.query(CreditTransaction).filter_by(user_id=user_id).all()
        return jsonify([
            {
                'id': str(t.id), 
                'credits': t.credits, 
                'amount_usd': t.amount_usd, 
                'transaction_id': t.transaction_id, 
                'description': t.description, 
                'created_at': t.created_at.isoformat() if t.created_at else None
            }
            for t in txs
        ])
    finally:
        session.close()
