"""
Oscar Broome Revenue System - Enhanced Backend API Server
Provides secure, scalable, and monitored API endpoints with comprehensive error handling
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
import traceback

# Third-party imports
from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException
import jwt
from dotenv import load_dotenv

# Local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_db_manager
from caching.redis_cache import RedisCache
from api_docs.swagger import generate_swagger_spec
from realtime.websocket_manager import WebSocketManager
from ssl_config.ssl_manager import SSLManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedBackendServer:
    """Enhanced backend server with security, monitoring, and scalability features"""

    def __init__(self):
        self.app = Flask(__name__)
        self.db_manager = get_db_manager()
        self.cache = RedisCache()
        self.websocket_manager = WebSocketManager()
        self.ssl_manager = SSLManager()

        # Configuration
        self.config = {
            'SECRET_KEY': os.getenv('SECRET_KEY', 'oscar-broome-secret-key-2024'),
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'oscar-broome-jwt-secret-2024'),
            'JWT_ACCESS_TOKEN_EXPIRE_MINUTES': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '15')),
            'JWT_REFRESH_TOKEN_EXPIRE_DAYS': int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7')),
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
            'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
            'TESTING': os.getenv('TESTING', 'False').lower() == 'true'
        }

        self.app.config.update(self.config)

        # Initialize components
        self._setup_middleware()
        self._setup_routes()
        self._setup_error_handlers()
        self._setup_health_checks()

        logger.info("Enhanced Backend Server initialized")

    def _setup_middleware(self):
        """Setup middleware components"""
        # CORS
        CORS(self.app, resources={
            r"/api/*": {
                "origins": ["http://localhost:3000", "http://localhost:8080"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["X-Total-Count", "X-Rate-Limit"],
                "supports_credentials": True
            }
        })

        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )

        # Request logging
        @self.app.before_request
        def log_request_info():
            logger.info(f'{request.method} {request.url} - {request.remote_addr}')

        # Request timing
        @self.app.before_request
        def start_timer():
            g.start = datetime.utcnow()

        @self.app.after_request
        def log_response_info(response):
            if hasattr(g, 'start'):
                duration = datetime.utcnow() - g.start
                response.headers['X-Response-Time'] = str(duration.total_seconds() * 1000) + 'ms'
            return response

    def _setup_routes(self):
        """Setup API routes"""

        # Authentication routes
        @self.app.route('/api/auth/login', methods=['POST'])
        @self.limiter.limit("5 per minute")
        def login():
            return self._handle_auth_request('login')

        @self.app.route('/api/auth/refresh', methods=['POST'])
        def refresh_token():
            return self._handle_auth_request('refresh')

        @self.app.route('/api/auth/logout', methods=['POST'])
        @self._require_auth
        def logout():
            return self._handle_auth_request('logout')

        # User management routes
        @self.app.route('/api/users/profile', methods=['GET'])
        @self._require_auth
        def get_user_profile():
            return self._handle_user_request('profile')

        @self.app.route('/api/users', methods=['GET'])
        @self._require_auth
        @self._require_role(['admin'])
        def get_users():
            return self._handle_user_request('list')

        # Revenue data routes
        @self.app.route('/api/revenue/dashboard', methods=['GET'])
        @self._require_auth
        @self._cache_response(timeout=300)  # 5 minutes
        def get_revenue_dashboard():
            return self._handle_revenue_request('dashboard')

        @self.app.route('/api/revenue/transactions', methods=['GET'])
        @self._require_auth
        def get_transactions():
            return self._handle_revenue_request('transactions')

        @self.app.route('/api/revenue/transactions', methods=['POST'])
        @self._require_auth
        @self._require_role(['admin', 'executive'])
        def create_transaction():
            return self._handle_revenue_request('create_transaction')

        # Earnings dashboard routes
        @self.app.route('/api/earnings/summary', methods=['GET'])
        @self._require_auth
        @self._cache_response(timeout=600)  # 10 minutes
        def get_earnings_summary():
            return self._handle_earnings_request('summary')

        @self.app.route('/api/earnings/report', methods=['GET'])
        @self._require_auth
        def get_earnings_report():
            return self._handle_earnings_request('report')

        # Payroll routes
        @self.app.route('/api/payroll/employees', methods=['GET'])
        @self._require_auth
        @self._require_role(['admin', 'hr'])
        def get_payroll_employees():
            return self._handle_payroll_request('employees')

        @self.app.route('/api/payroll/calculate', methods=['POST'])
        @self._require_auth
        @self._require_role(['admin', 'hr'])
        def calculate_payroll():
            return self._handle_payroll_request('calculate')

        # Financial integrations
        @self.app.route('/api/integrations/jpmorgan/status', methods=['GET'])
        @self._require_auth
        @self._require_role(['admin'])
        def get_jpmorgan_status():
            return self._handle_integration_request('jpmorgan_status')

        @self.app.route('/api/integrations/chase/status', methods=['GET'])
        @self._require_auth
        @self._require_role(['admin'])
        def get_chase_status():
            return self._handle_integration_request('chase_status')

        # WebSocket endpoint for real-time updates
        @self.app.route('/api/ws')
        def websocket_endpoint():
            return self.websocket_manager.handle_websocket(request)

        # API documentation
        @self.app.route('/api/docs')
        def api_docs():
            return jsonify(generate_swagger_spec())

    def _setup_error_handlers(self):
        """Setup comprehensive error handlers"""

        @self.app.errorhandler(400)
        def bad_request(error):
            logger.warning(f'Bad Request: {error}')
            return self._json_error_response(400, 'Bad Request', str(error))

        @self.app.errorhandler(401)
        def unauthorized(error):
            logger.warning(f'Unauthorized: {error}')
            return self._json_error_response(401, 'Unauthorized', 'Authentication required')

        @self.app.errorhandler(403)
        def forbidden(error):
            logger.warning(f'Forbidden: {error}')
            return self._json_error_response(403, 'Forbidden', 'Insufficient permissions')

        @self.app.errorhandler(404)
        def not_found(error):
            logger.info(f'Not Found: {request.url}')
            return self._json_error_response(404, 'Not Found', 'Resource not found')

        @self.app.errorhandler(429)
        def rate_limit_exceeded(error):
            logger.warning(f'Rate limit exceeded: {request.remote_addr}')
            return self._json_error_response(429, 'Rate Limit Exceeded', 'Too many requests')

        @self.app.errorhandler(500)
        def internal_server_error(error):
            logger.error(f'Internal Server Error: {error}\n{traceback.format_exc()}')
            return self._json_error_response(500, 'Internal Server Error', 'An unexpected error occurred')

        @self.app.errorhandler(Exception)
        def handle_unexpected_error(error):
            logger.error(f'Unexpected error: {error}\n{traceback.format_exc()}')
            return self._json_error_response(500, 'Internal Server Error', 'An unexpected error occurred')

    def _setup_health_checks(self):
        """Setup health check endpoints"""

        @self.app.route('/health')
        def health_check():
            """Basic health check"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            })

        @self.app.route('/health/detailed')
        def detailed_health_check():
            """Detailed health check with component status"""
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'components': {}
            }

            # Database health
            try:
                db_health = self.db_manager.health_check()
                health_status['components']['database'] = db_health
                if db_health['status'] != 'healthy':
                    health_status['status'] = 'degraded'
            except Exception as e:
                health_status['components']['database'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['status'] = 'unhealthy'

            # Cache health
            try:
                cache_health = self.cache.health_check()
                health_status['components']['cache'] = cache_health
                if not cache_health.get('healthy', False):
                    health_status['status'] = 'degraded'
            except Exception as e:
                health_status['components']['cache'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['status'] = 'degraded'

            # WebSocket health
            try:
                ws_health = self.websocket_manager.health_check()
                health_status['components']['websocket'] = ws_health
            except Exception as e:
                health_status['components']['websocket'] = {'status': 'unhealthy', 'error': str(e)}

            return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503

    def _require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return self._json_error_response(401, 'Unauthorized', 'Missing or invalid token')

            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, self.config['JWT_SECRET_KEY'], algorithms=['HS256'])

                # Check if token is expired
                if datetime.utcnow().timestamp() > payload['exp']:
                    return self._json_error_response(401, 'Unauthorized', 'Token expired')

                g.user = payload
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return self._json_error_response(401, 'Unauthorized', 'Token expired')
            except jwt.InvalidTokenError:
                return self._json_error_response(401, 'Unauthorized', 'Invalid token')

        return decorated_function

    def _require_role(self, required_roles: List[str]):
        """Decorator to require specific roles"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(g, 'user') or 'role' not in g.user:
                    return self._json_error_response(401, 'Unauthorized', 'User not authenticated')

                user_role = g.user['role']
                if user_role not in required_roles:
                    return self._json_error_response(403, 'Forbidden', 'Insufficient permissions')

                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def _cache_response(self, timeout: int = 300):
        """Decorator to cache responses"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = f"{request.method}:{request.url}:{request.data.decode() if request.data else ''}"

                # Try to get from cache
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    logger.info(f"Cache hit for {cache_key}")
                    return Response(
                        cached_response['data'],
                        status=cached_response['status'],
                        headers=cached_response['headers']
                    )

                # Execute function
                response = f(*args, **kwargs)

                # Cache the response
                if response.status_code == 200:
                    cache_data = {
                        'data': response.get_data(),
                        'status': response.status_code,
                        'headers': dict(response.headers)
                    }
                    self.cache.set(cache_key, cache_data, timeout)
                    logger.info(f"Cached response for {cache_key}")

                return response
            return decorated_function
        return decorator

    def _json_error_response(self, status_code: int, error: str, message: str) -> Response:
        """Create standardized JSON error response"""
        response_data = {
            'error': error,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path,
            'method': request.method
        }

        if self.config['DEBUG']:
            response_data['traceback'] = traceback.format_exc()

        return jsonify(response_data), status_code

    def _handle_auth_request(self, action: str):
        """Handle authentication requests"""
        try:
            if action == 'login':
                data = request.get_json()
                if not data or not data.get('email') or not data.get('password'):
                    return self._json_error_response(400, 'Bad Request', 'Email and password required')

                # Here you would integrate with your authentication system
                # For now, return mock response
                return jsonify({
                    'message': 'Login successful',
                    'token': 'mock-jwt-token',
                    'user': {'id': 1, 'email': data['email']}
                })

            elif action == 'refresh':
                # Handle token refresh
                return jsonify({'message': 'Token refreshed', 'token': 'new-mock-token'})

            elif action == 'logout':
                return jsonify({'message': 'Logged out successfully'})

        except Exception as e:
            logger.error(f'Auth error ({action}): {e}')
            return self._json_error_response(500, 'Internal Server Error', 'Authentication failed')

    def _handle_user_request(self, action: str):
        """Handle user management requests"""
        try:
            if action == 'profile':
                return jsonify({
                    'id': g.user['user_id'],
                    'email': g.user['email'],
                    'role': g.user['role']
                })

            elif action == 'list':
                # Mock user list
                return jsonify({
                    'users': [
                        {'id': 1, 'email': 'admin@oscarbroomerevenue.com', 'role': 'admin'},
                        {'id': 2, 'email': 'executive@oscarbroomerevenue.com', 'role': 'executive'}
                    ]
                })

        except Exception as e:
            logger.error(f'User request error ({action}): {e}')
            return self._json_error_response(500, 'Internal Server Error', 'User operation failed')

    def _handle_revenue_request(self, action: str):
        """Handle revenue data requests"""
        try:
            if action == 'dashboard':
                return jsonify({
                    'total_revenue': 1250000.00,
                    'monthly_growth': 8.5,
                    'top_performers': ['JPMorgan', 'Chase', 'NVIDIA'],
                    'last_updated': datetime.utcnow().isoformat()
                })

            elif action == 'transactions':
                return jsonify({
                    'transactions': [
                        {'id': 1, 'amount': 50000, 'source': 'JPMorgan', 'date': '2024-01-15'},
                        {'id': 2, 'amount': 75000, 'source': 'Chase', 'date': '2024-01-16'}
                    ]
                })

            elif action == 'create_transaction':
                data = request.get_json()
                # Here you would validate and save the transaction
                return jsonify({'message': 'Transaction created', 'id': 123}), 201

        except Exception as e:
            logger.error(f'Revenue request error ({action}): {e}')
            return self._json_error_response(500, 'Internal Server Error', 'Revenue operation failed')

    def _handle_earnings_request(self, action: str):
        """Handle earnings dashboard requests"""
        try:
            if action == 'summary':
                return jsonify({
                    'total_earnings': 2500000.00,
                    'net_profit': 750000.00,
                    'profit_margin': 30.0,
                    'period': 'Q1 2024'
                })

            elif action == 'report':
                return jsonify({
                    'report': 'Comprehensive earnings report data',
                    'generated_at': datetime.utcnow().isoformat()
                })

        except Exception as e:
            logger.error(f'Earnings request error ({action}): {e}')
            return self._json_error_response(500, 'Internal Server Error', 'Earnings operation failed')

    def _handle_payroll_request(self, action: str):
        """Handle payroll requests"""
        try:
            if action == 'employees':
                return jsonify({
                    'employees': [
                        {'id': 1, 'name': 'John Doe', 'salary': 75000, 'department': 'Engineering'},
                        {'id': 2, 'name': 'Jane Smith', 'salary': 80000, 'department': 'Finance'}
                    ]
                })

            elif action == 'calculate':
                data = request.get_json()
                # Here you would perform payroll calculations
                return jsonify({
                    'employee_id': data.get('employee_id'),
                    'gross_pay': 6666.67,
                    'net_pay': 5333.33,
                    'deductions': 1333.34
                })

        except Exception as e:
            logger.error(f'Payroll request error ({action}): {e}')
            return self._json_error_response(500, 'Internal Server Error', 'Payroll operation failed')

    def _handle_integration_request(self, action: str):
        """Handle integration status requests"""
        try:
            if action == 'jpmorgan_status':
                return jsonify({
                    'status': 'connected',
                    'last_sync': datetime.utcnow().isoformat(),
                    'accounts': 5,
                    'balance': 1250000.00
                })

            elif action == 'chase_status':
                return jsonify({
                    'status': 'connected',
                    'last_sync': datetime.utcnow().isoformat(),
                    'accounts': 3,
                    'balance': 750000.00
                })

        except Exception as e:
            logger.error(f'Integration request error ({action}): {e}')
            return self._json_error_response(500, 'Internal Server Error', 'Integration check failed')

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = None):
        """Run the server"""
        debug = debug if debug is not None else self.config['DEBUG']

        logger.info(f"Starting Enhanced Backend Server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")

        # Use SSL if available
        ssl_context = self.ssl_manager.get_ssl_context() if not debug else None

        self.app.run(
            host=host,
            port=port,
            debug=debug,
            ssl_context=ssl_context,
            threaded=True,
            use_reloader=False
        )

    def get_app(self):
        """Get the Flask app instance for testing"""
        return self.app

# Create server instance
server = EnhancedBackendServer()

if __name__ == '__main__':
    server.run()
