#!/usr/bin/env python3
"""
Security configuration and utilities for OWLban application
"""

import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
import jwt
import bcrypt
from werkzeug.exceptions import BadRequest


class SecurityConfig:
    """Security configuration for the application"""

    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET', secrets.token_hex(32))
        self.jwt_algorithm = 'HS256'
        self.token_expiry_hours = int(os.getenv('JWT_EXPIRY_HOURS', '24'))

        # CORS settings
        self.cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')

        # Rate limiting
        self.rate_limit_requests = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', '60'))  # seconds

        # Security headers
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }

        # Password requirements
        self.password_min_length = 12
        self.password_require_uppercase = True
        self.password_require_lowercase = True
        self.password_require_digits = True
        self.password_require_special = True


class UserManager:
    """User authentication and authorization manager"""

    def __init__(self, security_config):
        self.config = security_config
        self.users = {}  # In production, use a database

        # Create default admin user
        self._create_default_users()

    def _create_default_users(self):
        """Create default users for development"""
        default_users = [
            {
                'username': 'admin',
                'password': 'AdminPass123!',
                'role': 'admin',
                'email': 'admin@owlban.com'
            },
            {
                'username': 'manager',
                'password': 'ManagerPass123!',
                'role': 'manager',
                'email': 'manager@owlban.com'
            },
            {
                'username': 'user',
                'password': 'UserPass123!',
                'role': 'user',
                'email': 'user@owlban.com'
            }
        ]

        for user_data in default_users:
            self.users[user_data['username']] = {
                'password_hash': self._hash_password(user_data['password']),
                'role': user_data['role'],
                'email': user_data['email'],
                'created_at': datetime.utcnow(),
                'active': True
            }

    def _hash_password(self, password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_password(self, password, password_hash):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def authenticate_user(self, username, password):
        """Authenticate a user"""
        user = self.users.get(username)
        if not user or not user['active']:
            return None

        if self._verify_password(password, user['password_hash']):
            return {
                'username': username,
                'role': user['role'],
                'email': user['email']
            }

        return None

    def create_user(self, username, password, role, email):
        """Create a new user"""
        if username in self.users:
            raise ValueError("User already exists")

        if not self._validate_password(password):
            raise ValueError("Password does not meet requirements")

        self.users[username] = {
            'password_hash': self._hash_password(password),
            'role': role,
            'email': email,
            'created_at': datetime.utcnow(),
            'active': True
        }

        return True

    def _validate_password(self, password):
        """Validate password against requirements"""
        if len(password) < self.config.password_min_length:
            return False

        if self.config.password_require_uppercase and not any(c.isupper() for c in password):
            return False

        if self.config.password_require_lowercase and not any(c.islower() for c in password):
            return False

        if self.config.password_require_digits and not any(c.isdigit() for c in password):
            return False

        if self.config.password_require_special and not any(not c.isalnum() for c in password):
            return False

        return True

    def get_user_role(self, username):
        """Get user role"""
        user = self.users.get(username)
        return user['role'] if user else None


class JWTManager:
    """JWT token management"""

    def __init__(self, security_config):
        self.config = security_config

    def generate_token(self, user_data):
        """Generate a JWT token for user"""
        payload = {
            'username': user_data['username'],
            'role': user_data['role'],
            'email': user_data['email'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.config.token_expiry_hours)
        }

        token = jwt.encode(payload, self.config.jwt_secret, algorithm=self.config.jwt_algorithm)
        return token

    def verify_token(self, token):
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=[self.config.jwt_algorithm])

            # Check if token is expired
            if datetime.utcnow().timestamp() > payload['exp']:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, security_config):
        self.config = security_config
        self.requests = {}  # In production, use Redis

    def is_allowed(self, client_id):
        """Check if request is allowed"""
        now = datetime.utcnow().timestamp()
        window_start = now - self.config.rate_limit_window

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > window_start
            ]

        # Check request count
        if client_id not in self.requests:
            self.requests[client_id] = []

        if len(self.requests[client_id]) >= self.config.rate_limit_requests:
            return False

        # Add current request
        self.requests[client_id].append(now)
        return True


# Global instances
security_config = SecurityConfig()
user_manager = UserManager(security_config)
jwt_manager = JWTManager(security_config)
rate_limiter = RateLimiter(security_config)


def require_auth(roles=None):
    """Decorator to require authentication and optional role authorization"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid authorization header'}), 401

            token = auth_header.split(' ')[1]

            # Verify token
            user_data = jwt_manager.verify_token(token)
            if not user_data:
                return jsonify({'error': 'Invalid or expired token'}), 401

            # Check role if required
            if roles and user_data['role'] not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403

            # Store user in request context
            g.user = user_data

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_rate_limit(f):
    """Decorator to apply rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_id = request.remote_addr  # In production, use user ID or API key

        if not rate_limiter.is_allowed(client_id):
            return jsonify({'error': 'Rate limit exceeded'}), 429

        return f(*args, **kwargs)
    return decorated_function


def add_security_headers(response):
    """Add security headers to response"""
    for header, value in security_config.security_headers.items():
        response.headers[header] = value
    return response


def validate_input_data(required_fields=None, field_validators=None):
    """Validate input data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()

                if required_fields:
                    for field in required_fields:
                        if field not in data:
                            raise BadRequest(f"Missing required field: {field}")

                if field_validators:
                    for field, validator in field_validators.items():
                        if field in data and not validator(data[field]):
                            raise BadRequest(f"Invalid value for field: {field}")

                return f(*args, **kwargs)

            except BadRequest as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                return jsonify({'error': 'Invalid JSON data'}), 400

        return decorated_function
    return decorator


# Input validators
def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Validate username format"""
    if not username or len(username) < 3 or len(username) > 50:
        return False
    return username.replace('_', '').replace('-', '').isalnum()


def validate_amount(amount):
    """Validate monetary amount"""
    try:
        amount = float(amount)
        return amount > 0 and amount < 1000000  # Reasonable limits
    except (ValueError, TypeError):
        return False
