"""
Project Perfection Integration Test
Tests all critical components working together
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import Config
from database import get_db, init_db
from caching.redis_cache import get_cache, RedisCache
from api_docs.swagger import setup_swagger
from realtime.websocket_manager import WebSocketManager
from ssl_config.ssl_manager import SSLManager
from organizational_leadership.leadership import LeadershipManager
from revenue_tracking import RevenueTracker
from interface import NVIDIAInterface

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-secret-key'
    REDIS_URL = None  # Disable Redis for tests

class PerfectionIntegrationTest(unittest.TestCase):
    """Integration test for all critical components"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Initialize database
        init_db()

        # Mock external dependencies
        self.mock_cache = Mock()
        self.mock_ws_manager = Mock()
        self.mock_ssl_manager = Mock()

    def tearDown(self):
        """Clean up test environment"""
        self.app_context.pop()

    def test_app_creation(self):
        """Test that the Flask app is created successfully"""
        self.assertIsNotNone(self.app)
        self.assertEqual(self.app.config['TESTING'], True)

    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)
        self.assertIn('services', data)

    @patch('app.get_cache')
    def test_cache_integration(self, mock_get_cache):
        """Test Redis cache integration"""
        mock_get_cache.return_value = self.mock_cache
        self.mock_cache.is_connected.return_value = True

        cache = get_cache()
        self.assertIsNotNone(cache)

        # Test cache operations
        cache.set('test_key', 'test_value')
        self.mock_cache.set.assert_called_with('test_key', 'test_value', ttl=None)

        cache.get('test_key')
        self.mock_cache.get.assert_called_with('test_key')

    @patch('app.WebSocketManager')
    def test_websocket_integration(self, mock_ws_manager_class):
        """Test WebSocket manager integration"""
        mock_ws_manager_class.return_value = self.mock_ws_manager

        ws_manager = WebSocketManager()
        self.assertIsNotNone(ws_manager)

        # Test WebSocket operations
        ws_manager.broadcast('test_event', {'data': 'test'})
        self.mock_ws_manager.broadcast.assert_called_with('test_event', {'data': 'test'})

    def test_ssl_manager_integration(self):
        """Test SSL manager integration"""
        ssl_manager = SSLManager()

        # Test certificate info retrieval
        info = ssl_manager.get_cert_info()
        self.assertIsInstance(info, dict)

        # Test SSL context setup
        context = ssl_manager.setup_ssl_context()
        self.assertIsInstance(context, dict)

    def test_leadership_manager_integration(self):
        """Test leadership manager integration"""
        leadership_manager = LeadershipManager()

        # Test leadership simulation
        result = leadership_manager.simulate_leadership(
            'Test Leader',
            'DEMOCRATIC',
            ['Alice', 'Bob', 'Charlie']
        )

        self.assertIsInstance(result, dict)
        self.assertIn('lead_result', result)
        self.assertIn('team_status', result)

    def test_revenue_tracker_integration(self):
        """Test revenue tracker integration"""
        revenue_tracker = RevenueTracker()

        # Test revenue tracking
        revenue_data = {
            'amount': 1000.00,
            'source': 'sales',
            'category': 'product',
            'date': '2024-01-01'
        }

        result = revenue_tracker.track_revenue(revenue_data)
        self.assertIsInstance(result, dict)

    def test_nvidia_interface_integration(self):
        """Test NVIDIA interface integration"""
        nvidia_interface = NVIDIAInterface()

        # Test GPU status retrieval
        status = nvidia_interface.get_gpu_status()
        self.assertIsInstance(status, dict)

    @patch('app.create_access_token')
    def test_authentication_flow(self, mock_create_token):
        """Test authentication flow"""
        mock_create_token.return_value = 'test_token'

        # Test login endpoint
        response = self.client.post('/api/auth/login',
            json={'username': 'admin', 'password': 'password'}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Make multiple requests to test rate limiting
        for i in range(5):
            response = self.client.post('/api/auth/login',
                json={'username': 'admin', 'password': 'wrong'}
            )

        # Should eventually get rate limited
        self.assertIn(response.status_code, [401, 429])

    @patch('app.get_cache')
    @patch('app.WebSocketManager')
    def test_leadership_endpoint_integration(self, mock_ws_manager_class, mock_get_cache):
        """Test leadership endpoint with all integrations"""
        mock_get_cache.return_value = self.mock_cache
        mock_ws_manager_class.return_value = self.mock_ws_manager

        self.mock_cache.is_connected.return_value = True
        self.mock_cache.set.return_value = True

        # Get auth token first
        with patch('app.create_access_token', return_value='test_token'):
            auth_response = self.client.post('/api/auth/login',
                json={'username': 'admin', 'password': 'password'}
            )
            token = json.loads(auth_response.data)['access_token']

        # Test leadership endpoint
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/leadership/lead_team',
            json={
                'leader_name': 'Test Leader',
                'leadership_style': 'DEMOCRATIC',
                'team_members': ['Alice', 'Bob']
            },
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('lead_result', data)

        # Verify cache was called
        self.mock_cache.set.assert_called()

        # Verify WebSocket broadcast was called
        self.mock_ws_manager.broadcast.assert_called_with(
            'leadership_update',
            unittest.mock.ANY  # Match any data
        )

    def test_error_handling(self):
        """Test error handling across components"""
        # Test 404 error
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

        # Test invalid JSON
        response = self.client.post('/api/auth/login',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = self.client.get('/health')
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)

    def test_security_headers(self):
        """Test security headers are properly set"""
        response = self.client.get('/')
        self.assertIn('X-Frame-Options', response.headers)
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertIn('X-XSS-Protection', response.headers)

    def test_database_integration(self):
        """Test database integration"""
        db = get_db()
        self.assertIsNotNone(db)

        # Test database operations
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT 1"))
            self.assertEqual(result.fetchone()[0], 1)

    def test_api_documentation_integration(self):
        """Test API documentation integration"""
        swagger = setup_swagger(self.app)
        self.assertIsNotNone(swagger)

        # Test Swagger endpoint
        response = self.client.get('/apispec.json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('openapi', data)
        self.assertIn('info', data)
        self.assertIn('paths', data)

    def test_performance_monitoring(self):
        """Test performance monitoring capabilities"""
        start_time = time.time()

        # Make multiple requests
        for _ in range(10):
            self.client.get('/health')

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete within reasonable time
        self.assertLess(total_time, 5.0)  # Less than 5 seconds for 10 requests

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import queue

        results = queue.Queue()

        def make_request():
            response = self.client.get('/health')
            results.put(response.status_code)

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check all requests succeeded
        for _ in range(5):
            status_code = results.get()
            self.assertEqual(status_code, 200)

    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Make many requests
        for _ in range(100):
            self.client.get('/health')

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        self.assertLess(memory_increase, 50 * 1024 * 1024)

    def test_component_isolation(self):
        """Test that components are properly isolated"""
        # Test that cache failure doesn't break the app
        with patch('app.get_cache') as mock_get_cache:
            mock_cache = Mock()
            mock_cache.is_connected.return_value = False
            mock_get_cache.return_value = mock_cache

            response = self.client.get('/health')
            self.assertEqual(response.status_code, 200)

        # Test that WebSocket failure doesn't break the app
        with patch('app.WebSocketManager') as mock_ws_class:
            mock_ws = Mock()
            mock_ws.init_app.side_effect = Exception("WebSocket error")
            mock_ws_class.return_value = mock_ws

            # App should still start (WebSocket failure shouldn't be fatal)
            app = create_app(TestConfig)
            self.assertIsNotNone(app)

if __name__ == '__main__':
    # Run comprehensive integration tests
    unittest.main(verbosity=2)
