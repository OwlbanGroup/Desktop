"""
Owlban Group Integrated Platform - Main Application Server
Combines all critical components for project perfection
"""

import os
import sys
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime

# Import our custom modules
from config import Config
from database import get_db, init_db
from caching.redis_cache import get_cache
from api_docs.swagger import setup_swagger
from realtime.websocket_manager import WebSocketManager, socketio
from ssl_config.ssl_manager import SSLManager
from organizational_leadership.leadership import LeadershipManager
from revenue_tracking import RevenueTracker
from interface import NVIDIAInterface
from OSCAR_BROOME_REVENUE.earnings_dashboard.api import EarningsAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """
    Create and configure the Flask application

    Args:
        config_class: Configuration class to use

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)

    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    # Initialize our custom components
    cache = get_cache()
    ws_manager = WebSocketManager()

    # Initialize database
    init_db()

    # Setup WebSocket manager
    ws_manager.init_app(app)

    # Setup Swagger documentation
    setup_swagger(app)

    # Initialize business logic components
    leadership_manager = LeadershipManager()
    revenue_tracker = RevenueTracker()
    nvidia_interface = NVIDIAInterface()
    earnings_api = EarningsAPI()

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """System health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'services': {
                'database': 'connected' if get_db() else 'disconnected',
                'cache': 'connected' if cache.is_connected() else 'disconnected',
                'websockets': 'active' if ws_manager else 'inactive'
            }
        })

    # API Routes
    @app.route('/api/leadership/lead_team', methods=['POST'])
    @jwt_required()
    @limiter.limit("10 per minute")
    def lead_team():
        """Leadership simulation endpoint"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            leader_name = data.get('leader_name')
            leadership_style = data.get('leadership_style')
            team_members = data.get('team_members', [])

            if not all([leader_name, leadership_style, team_members]):
                return jsonify({'error': 'Missing required fields'}), 400

            # Simulate leadership
            result = leadership_manager.simulate_leadership(
                leader_name, leadership_style, team_members
            )

            # Cache result
            cache_key = f"leadership:{leader_name}:{leadership_style}"
            cache.set(cache_key, result, ttl=3600)  # Cache for 1 hour

            # Emit real-time update
            ws_manager.broadcast('leadership_update', {
                'leader': leader_name,
                'style': leadership_style,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })

            return jsonify(result)

        except Exception as e:
            logger.error(f"Leadership simulation error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/revenue/track', methods=['POST'])
    @jwt_required()
    @limiter.limit("20 per minute")
    def track_revenue():
        """Revenue tracking endpoint"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            revenue_data = {
                'amount': data.get('amount'),
                'source': data.get('source'),
                'category': data.get('category'),
                'date': data.get('date', datetime.now().isoformat())
            }

            if not all([revenue_data['amount'], revenue_data['source']]):
                return jsonify({'error': 'Missing required fields'}), 400

            # Track revenue
            result = revenue_tracker.track_revenue(revenue_data)

            # Emit real-time update
            ws_manager.broadcast('revenue_update', {
                'data': revenue_data,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })

            return jsonify(result)

        except Exception as e:
            logger.error(f"Revenue tracking error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/gpu/status', methods=['GET'])
    @jwt_required()
    @limiter.limit("30 per minute")
    def gpu_status():
        """NVIDIA GPU status endpoint"""
        try:
            # Get GPU status from cache first
            cache_key = "gpu_status"
            cached_status = cache.get(cache_key)

            if cached_status:
                return jsonify(cached_status)

            # Get fresh GPU status
            status = nvidia_interface.get_gpu_status()

            # Cache for 30 seconds
            cache.set(cache_key, status, ttl=30)

            # Emit real-time update
            ws_manager.broadcast('gpu_status', {
                'status': status,
                'timestamp': datetime.now().isoformat()
            })

            return jsonify(status)

        except Exception as e:
            logger.error(f"GPU status error: {e}")
            return jsonify({'error': 'Failed to get GPU status'}), 500

    @app.route('/api/earnings/dashboard', methods=['GET'])
    @jwt_required()
    @limiter.limit("10 per minute")
    def earnings_dashboard():
        """Earnings dashboard endpoint"""
        try:
            # Get earnings data
            earnings_data = earnings_api.get_dashboard_data()

            return jsonify(earnings_data)

        except Exception as e:
            logger.error(f"Earnings dashboard error: {e}")
            return jsonify({'error': 'Failed to get earnings data'}), 500

    @app.route('/api/auth/login', methods=['POST'])
    @limiter.limit("5 per minute")
    def login():
        """Authentication endpoint"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            username = data.get('username')
            password = data.get('password')

            if not all([username, password]):
                return jsonify({'error': 'Missing username or password'}), 400

            # Simple authentication (replace with proper auth system)
            if username == 'admin' and password == 'password':
                access_token = create_access_token(identity=username)
                return jsonify({'access_token': access_token})
            else:
                return jsonify({'error': 'Invalid credentials'}), 401

        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({'error': 'Authentication failed'}), 500

    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle WebSocket connection"""
        logger.info(f"Client connected: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnection"""
        logger.info(f"Client disconnected: {request.sid}")

    @socketio.on('subscribe_updates')
    def handle_subscribe_updates(data):
        """Handle subscription to real-time updates"""
        event_type = data.get('event_type')
        if event_type:
            ws_manager.register_event_handler(event_type, lambda d: None)
            socketio.emit('subscribed', {'event_type': event_type})

    # Frontend routes
    @app.route('/')
    def index():
        """Main dashboard page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Owlban Group Integrated Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }
                .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
                .status { display: inline-block; padding: 5px 10px; border-radius: 4px; }
                .healthy { background: #27ae60; color: white; }
                .error { background: #e74c3c; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🦉 Owlban Group Integrated Platform</h1>
                    <p>Leadership Simulation • Revenue Tracking • NVIDIA AI Integration</p>
                </div>

                <div class="section">
                    <h2>System Status</h2>
                    <p>Database: <span class="status healthy">Connected</span></p>
                    <p>Cache: <span class="status healthy">Active</span></p>
                    <p>WebSocket: <span class="status healthy">Running</span></p>
                </div>

                <div class="section">
                    <h2>API Documentation</h2>
                    <p><a href="/docs" target="_blank">📖 View Swagger Documentation</a></p>
                </div>

                <div class="section">
                    <h2>Real-time Features</h2>
                    <ul>
                        <li>✅ WebSocket connections for live updates</li>
                        <li>✅ Leadership simulation with real-time feedback</li>
                        <li>✅ Revenue tracking with instant notifications</li>
                        <li>✅ GPU monitoring and status updates</li>
                    </ul>
                </div>
            </div>

            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <script>
                const socket = io();

                socket.on('connect', function() {
                    console.log('Connected to WebSocket');
                });

                socket.on('leadership_update', function(data) {
                    console.log('Leadership update:', data);
                });

                socket.on('revenue_update', function(data) {
                    console.log('Revenue update:', data);
                });

                socket.on('gpu_status', function(data) {
                    console.log('GPU status:', data);
                });
            </script>
        </body>
        </html>
        """
        return render_template_string(html)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({'error': 'Rate limit exceeded'}), 429

    logger.info("✅ Owlban Group Integrated Platform initialized successfully")
    return app

def main():
    """Main application entry point"""
    app = create_app()

    # SSL configuration (if certificates exist)
    ssl_manager = SSLManager()
    ssl_context = None

    if os.path.exists(ssl_manager.cert_file) and os.path.exists(ssl_manager.key_file):
        ssl_context = (ssl_manager.cert_file, ssl_manager.key_file)
        logger.info("🔒 SSL/TLS enabled")

    # Start the application
    try:
        if ssl_context:
            socketio.run(app, host='0.0.0.0', port=5000, ssl_context=ssl_context, debug=True)
        else:
            socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("🛑 Application shutdown requested")
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
