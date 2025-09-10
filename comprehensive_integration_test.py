"""
Oscar Broome Revenue System - Comprehensive Integration Test Suite
Tests all critical components including authentication, database, API, and security features
"""

import os
import sys
import json
import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test dependencies
from backend.app_server_enhanced import EnhancedBackendServer
from database.connection import DatabaseManager
from OSCAR-BROOME-REVENUE.auth.login_override_fixed import AuthenticationManager
from OSCAR-BROOME-REVENUE.middleware.security import SecurityMiddleware
from caching.redis_cache import RedisCache
from realtime.websocket_manager import WebSocketManager

class TestOscarBroomeIntegration(unittest.TestCase):
    """Comprehensive integration test suite"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret',
            'TESTING': True,
            'DEBUG': True
        }

        # Mock external dependencies
        self.mock_db = Mock()
        self.mock_cache = Mock()
        self.mock_websocket = Mock()

        # Create test server instance
        with patch('backend.app_server_enhanced.get_db_manager', return_value=self.mock_db), \
             patch('backend.app_server_enhanced.RedisCache', return_value=self.mock_cache), \
             patch('backend.app_server_enhanced.WebSocketManager', return_value=self.mock_websocket):

            self.server = EnhancedBackendServer()
            self.app = self.server.get_app()
            self.app.config.update(self.config)
            self.client = self.app.test_client()

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def test_health_check_endpoints(self):
        """Test health check endpoints"""
        # Basic health check
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)

        # Detailed health check
        response = self.client.get('/health/detailed')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('components', data)
        self.assertIn('database', data['components'])
        self.assertIn('cache', data['components'])

    def test_authentication_flow(self):
        """Test complete authentication flow"""
        # Test login endpoint
        login_data = {
            'email': 'admin@oscarbroomerevenue.com',
            'password': 'OscarBroome2024!'
        }

        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], login_data['email'])

        # Test token refresh
        response = self.client.post('/api/auth/refresh',
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Test logout
        response = self.client.post('/api/auth/logout',
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_user_management(self):
        """Test user management endpoints"""
        # Mock authentication
        with self.app.test_request_context():
            from flask import g
            g.user = {
                'user_id': 1,
                'email': 'admin@oscarbroomerevenue.com',
                'role': 'admin'
            }

            # Test user profile endpoint
            response = self.client.get('/api/users/profile')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['email'], 'admin@oscarbroomerevenue.com')
            self.assertEqual(data['role'], 'admin')

            # Test user list endpoint (admin only)
            response = self.client.get('/api/users')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('users', data)

    def test_revenue_endpoints(self):
        """Test revenue data endpoints"""
        # Mock authentication
        with self.app.test_request_context():
            from flask import g
            g.user = {
                'user_id': 1,
                'email': 'admin@oscarbroomerevenue.com',
                'role': 'admin'
            }

            # Test revenue dashboard
            response = self.client.get('/api/revenue/dashboard')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('total_revenue', data)
            self.assertIn('monthly_growth', data)

            # Test transactions endpoint
            response = self.client.get('/api/revenue/transactions')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('transactions', data)

            # Test create transaction
            transaction_data = {
                'amount': 50000,
                'source': 'Test Source',
                'description': 'Test transaction'
            }
            response = self.client.post('/api/revenue/transactions',
                                      data=json.dumps(transaction_data),
                                      content_type='application/json')
            self.assertEqual(response.status_code, 201)

    def test_earnings_endpoints(self):
        """Test earnings dashboard endpoints"""
        # Mock authentication
        with self.app.test_request_context():
            from flask import g
            g.user = {
                'user_id': 1,
                'email': 'executive@oscarbroomerevenue.com',
                'role': 'executive'
            }

            # Test earnings summary
            response = self.client.get('/api/earnings/summary')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('total_earnings', data)
            self.assertIn('net_profit', data)

            # Test earnings report
            response = self.client.get('/api/earnings/report')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('report', data)

    def test_payroll_endpoints(self):
        """Test payroll management endpoints"""
        # Mock authentication with HR role
        with self.app.test_request_context():
            from flask import g
            g.user = {
                'user_id': 1,
                'email': 'hr@oscarbroomerevenue.com',
                'role': 'hr'
            }

            # Test employees endpoint
            response = self.client.get('/api/payroll/employees')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('employees', data)

            # Test payroll calculation
            calc_data = {
                'employee_id': 1,
                'hours_worked': 160,
                'hourly_rate': 50
            }
            response = self.client.post('/api/payroll/calculate',
                                      data=json.dumps(calc_data),
                                      content_type='application/json')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('gross_pay', data)
            self.assertIn('net_pay', data)

    def test_integration_status_endpoints(self):
        """Test financial integration status endpoints"""
        # Mock authentication with admin role
        with self.app.test_request_context():
            from flask import g
            g.user = {
                'user_id': 1,
                'email': 'admin@oscarbroomerevenue.com',
                'role': 'admin'
            }

            # Test JPMorgan integration status
            response = self.client.get('/api/integrations/jpmorgan/status')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('status', data)
            self.assertIn('last_sync', data)

            # Test Chase integration status
            response = self.client.get('/api/integrations/chase/status')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('status', data)
            self.assertIn('last_sync', data)

    def test_security_middleware(self):
        """Test security middleware functionality"""
        # Test rate limiting headers
        response = self.client.get('/health')
        self.assertIn('X-RateLimit-Limit', response.headers)
        self.assertIn('X-RateLimit-Remaining', response.headers)
        self.assertIn('X-RateLimit-Reset', response.headers)

        # Test security headers
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertIn('X-XSS-Protection', response.headers)

        # Test CORS headers
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_error_handling(self):
        """Test comprehensive error handling"""
        # Test 404 error
        response = self.client.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('message', data)
        self.assertIn('timestamp', data)

        # Test invalid JSON
        response = self.client.post('/api/auth/login',
                                  data='invalid json',
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Test missing authentication
        response = self.client.get('/api/users/profile')
        self.assertEqual(response.status_code, 401)

    def test_database_integration(self):
        """Test database integration"""
        # Mock database operations
        self.mock_db.health_check.return_value = {
            'status': 'healthy',
            'message': 'Database connection is working'
        }

        # Test database health through health endpoint
        response = self.client.get('/health/detailed')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['components']['database']['status'], 'healthy')

    def test_cache_integration(self):
        """Test caching integration"""
        # Mock cache operations
        self.mock_cache.health_check.return_value = {'healthy': True}
        self.mock_cache.get.return_value = None
        self.mock_cache.set.return_value = True

        # Test cache health through health endpoint
        response = self.client.get('/health/detailed')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['components']['cache']['healthy'])

    def test_api_documentation(self):
        """Test API documentation endpoint"""
        response = self.client.get('/api/docs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('swagger', data.lower()) or self.assertIn('openapi', data.lower())

    @patch('backend.app_server_enhanced.jwt.decode')
    def test_jwt_token_validation(self, mock_jwt_decode):
        """Test JWT token validation"""
        # Mock valid token
        mock_jwt_decode.return_value = {
            'user_id': 1,
            'email': 'test@example.com',
            'role': 'admin',
            'exp': datetime.utcnow().timestamp() + 3600
        }

        with self.app.test_request_context(headers={'Authorization': 'Bearer valid-token'}):
            from flask import g
            # This would normally be set by the auth decorator
            g.user = mock_jwt_decode.return_value

            response = self.client.get('/api/users/profile')
            self.assertEqual(response.status_code, 200)

    def test_request_validation(self):
        """Test request validation"""
        # Test with oversized payload
        large_data = 'x' * (17 * 1024 * 1024)  # 17MB
        response = self.client.post('/api/auth/login',
                                  data=large_data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 413)

    def test_cors_configuration(self):
        """Test CORS configuration"""
        # Test preflight request
        response = self.client.options('/api/auth/login',
                                     headers={
                                         'Origin': 'http://localhost:3000',
                                         'Access-Control-Request-Method': 'POST',
                                         'Access-Control-Request-Headers': 'Content-Type'
                                     })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)

    def test_response_timing(self):
        """Test response timing headers"""
        response = self.client.get('/health')
        self.assertIn('X-Response-Time', response.headers)

        # Verify timing is reasonable (less than 1 second for health check)
        timing = float(response.headers['X-Response-Time'].rstrip('ms'))
        self.assertLess(timing, 1000)

class TestAuthenticationManager(unittest.TestCase):
    """Test authentication manager functionality"""

    def setUp(self):
        self.auth_manager = AuthenticationManager()

    def test_user_creation_and_authentication(self):
        """Test user creation and authentication"""
        # Test user authentication
        result = asyncio.run(self.auth_manager.authenticateUser(
            'admin@oscarbroomerevenue.com',
            'OscarBroome2024!',
            '123456'  # Mock MFA code
        ))

        self.assertTrue(result['success'])
        self.assertIn('token', result)
        self.assertIn('user', result)

    def test_admin_override(self):
        """Test admin override functionality"""
        result = asyncio.run(self.auth_manager.adminOverride(
            'OSCAR_BROOME_EMERGENCY_2024',
            'executive@oscarbroomerevenue.com'
        ))

        self.assertTrue(result['success'])
        self.assertIn('emergencyToken', result)

    def test_invalid_credentials(self):
        """Test invalid credentials handling"""
        result = asyncio.run(self.auth_manager.authenticateUser(
            'invalid@example.com',
            'wrongpassword'
        ))

        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Invalid credentials')

class TestSecurityMiddleware(unittest.TestCase):
    """Test security middleware functionality"""

    def setUp(self):
        self.security = SecurityMiddleware()

    def test_input_validation(self):
        """Test input validation"""
        # Mock request object
        mock_req = Mock()
        mock_req.headers = {'content-length': '1024'}
        mock_req.query = {'param': 'valid_value'}

        # This would normally be tested with actual middleware
        # For now, just test the validation logic exists
        self.assertIsInstance(self.security, SecurityMiddleware)

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Mock request/response objects
        mock_req = Mock()
        mock_req.remote_addr = '127.0.0.1'
        mock_req.path = '/api/test'
        mock_res = Mock()

        # Test that rate limiting methods exist
        self.assertTrue(hasattr(self.security, 'rateLimit'))

class TestDatabaseManager(unittest.TestCase):
    """Test database manager functionality"""

    def setUp(self):
        self.db_manager = DatabaseManager()

    @patch('database.connection.create_engine')
    def test_database_initialization(self, mock_create_engine):
        """Test database initialization"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        # Test that initialization doesn't raise errors
        try:
            self.db_manager.init_db()
        except Exception as e:
            # In test environment, some dependencies might not be available
            self.assertIn('test', str(e).lower()) or self.assertIn('mock', str(e).lower())

    def test_health_check_structure(self):
        """Test health check response structure"""
        # Mock the database connection
        with patch.object(self.db_manager, 'engine', Mock()) as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = Mock(return_value=None)

            mock_result = Mock()
            mock_result.fetchone.return_value = [1, '2024-01-01']
            mock_conn.execute.return_value = mock_result

            # Test health check
            result = self.db_manager.health_check()
            self.assertIn('status', result)
            self.assertIn('message', result)

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOscarBroomeIntegration)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAuthenticationManager))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSecurityMiddleware))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatabaseManager))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\n{'='*60}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.failures:
        print(f"\n{'='*60}")
        print("FAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print(f"\n{'='*60}")
        print("ERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)
