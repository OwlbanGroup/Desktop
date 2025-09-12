#!/usr/bin/env python3
"""
Enhanced Security Testing for Oscar Broome Revenue System
Tests database connection enhancements and authentication improvements
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseManager
from OSCAR_BROOME_REVENUE.auth.login_override_fixed import AuthenticationManager

class TestDatabaseConnection:
    """Test enhanced database connection features"""

    def test_ssl_configuration(self):
        """Test SSL configuration for database connections"""
        # Test production SSL mode
        with patch.dict(os.environ, {'NODE_ENV': 'production', 'DB_SSL_MODE': 'require'}):
            db_manager = DatabaseManager()
            connection_string = db_manager._build_connection_string()
            assert 'ssl_mode=require' in connection_string

        # Test development SSL mode
        with patch.dict(os.environ, {'NODE_ENV': 'development', 'DB_SSL_MODE': 'prefer'}):
            db_manager = DatabaseManager()
            connection_string = db_manager._build_connection_string()
            assert 'ssl_mode=prefer' in connection_string

    def test_security_warnings(self):
        """Test security warnings for database configuration"""
        with patch('database.connection.logger') as mock_logger:
            # Test localhost warning
            with patch.dict(os.environ, {'DB_HOST': 'localhost'}):
                db_manager = DatabaseManager()
                db_manager._build_connection_string()
                mock_logger.warning.assert_called_with(
                    "Using localhost database connection - ensure proper security measures are in place"
                )

            # Test no password warning
            with patch.dict(os.environ, {'DB_PASSWORD': ''}):
                db_manager = DatabaseManager()
                db_manager._build_connection_string()
                mock_logger.warning.assert_called_with(
                    "No database password provided - this is a security risk in production"
                )

    def test_connection_pooling(self):
        """Test database connection pooling configuration"""
        with patch('database.connection.create_engine') as mock_engine:
            db_manager = DatabaseManager()
            db_manager.init_db()

            # Verify engine is created with correct pooling parameters
            mock_engine.assert_called_once()
            call_args = mock_engine.call_args
            assert call_args[1]['poolclass'].__name__ == 'QueuePool'
            assert call_args[1]['pool_size'] == 10
            assert call_args[1]['max_overflow'] == 20
            assert call_args[1]['pool_timeout'] == 30

class TestAuthenticationEnhancements:
    """Test enhanced authentication features"""

    def setup_method(self):
        """Setup test environment"""
        self.auth_manager = AuthenticationManager()

    def test_password_validation(self):
        """Test enhanced password validation"""
        # Test valid password
        result = self.auth_manager.validatePassword('ValidPass123!')
        assert result['valid'] is True

        # Test short password
        result = self.auth_manager.validatePassword('Short1!')
        assert result['valid'] is False
        assert '12 characters' in result['message']

        # Test password without uppercase
        result = self.auth_manager.validatePassword('validpass123!')
        assert result['valid'] is False
        assert 'uppercase' in result['message']

        # Test password without lowercase
        result = self.auth_manager.validatePassword('VALIDPASS123!')
        assert result['valid'] is False
        assert 'lowercase' in result['message']

        # Test password without numbers
        result = self.auth_manager.validatePassword('ValidPass!')
        assert result['valid'] is False
        assert 'number' in result['message']

        # Test password without special characters
        result = self.auth_manager.validatePassword('ValidPass123')
        assert result['valid'] is False
        assert 'special character' in result['message']

    def test_session_management(self):
        """Test session management features"""
        # Mock a user and session
        user_id = 'test-user-001'
        mock_session = {
            'userId': user_id,
            'email': 'test@example.com',
            'role': 'user',
            'permissions': ['read'],
            'expiresAt': datetime.now().timestamp() * 1000 + 3600000  # 1 hour from now
        }

        # Mock sessions map
        with patch.object(self.auth_manager, 'sessions', { 'token123': mock_session }):
            sessions = self.auth_manager.getActiveSessions(user_id)
            assert len(sessions) == 1
            assert sessions[0]['token'].startswith('token123')

    def test_force_logout_all(self):
        """Test force logout all sessions feature"""
        user_id = 'test-user-001'
        mock_sessions = {
            'token1': { 'userId': user_id, 'expiresAt': datetime.now().timestamp() * 1000 + 3600000 },
            'token2': { 'userId': user_id, 'expiresAt': datetime.now().timestamp() * 1000 + 3600000 },
            'token3': { 'userId': 'other-user', 'expiresAt': datetime.now().timestamp() * 1000 + 3600000 }
        }

        with patch.object(self.auth_manager, 'sessions', mock_sessions):
            result = self.auth_manager.forceLogoutAll(user_id)
            assert result['success'] is True
            assert '2 sessions terminated' in result['message']

    def test_enhanced_token_verification(self):
        """Test enhanced token verification with session cleanup"""
        # Test expired session cleanup
        expired_token = 'expired_token'
        expired_session = {
            'userId': 'test-user',
            'email': 'test@example.com',
            'role': 'user',
            'permissions': ['read'],
            'expiresAt': datetime.now().timestamp() * 1000 - 1000  # Expired 1 second ago
        }

        with patch.object(self.auth_manager, 'sessions', { expired_token: expired_session }):
            result = self.auth_manager.verifyTokenEnhanced(expired_token)
            assert result['valid'] is False
            assert result['message'] == 'Session expired'

    def test_security_stats(self):
        """Test security statistics generation"""
        # Mock users and sessions
        mock_users = new Map([
            ['user1@example.com', { 'locked': False }],
            ['user2@example.com', { 'locked': True }],
            ['user3@example.com', { 'locked': False }]
        ])

        mock_sessions = new Map([
            ['token1', { 'expiresAt': datetime.now().timestamp() * 1000 + 3600000 }],
            ['token2', { 'expiresAt': datetime.now().timestamp() * 1000 - 1000 }]  # Expired
        ])

        with patch.object(self.auth_manager, 'users', mock_users), \
             patch.object(self.auth_manager, 'sessions', mock_sessions):

            stats = self.auth_manager.getSecurityStats()
            assert stats['totalUsers'] == 3
            assert stats['lockedUsers'] == 1
            assert stats['activeSessions'] == 1
            assert 'timestamp' in stats

    def test_session_cleanup(self):
        """Test expired session cleanup"""
        mock_sessions = {
            'valid_token': { 'expiresAt': datetime.now().timestamp() * 1000 + 3600000 },
            'expired_token1': { 'expiresAt': datetime.now().timestamp() * 1000 - 1000 },
            'expired_token2': { 'expiresAt': datetime.now().timestamp() * 1000 - 2000 }
        }

        with patch.object(self.auth_manager, 'sessions', mock_sessions):
            result = self.auth_manager.cleanupExpiredSessions()
            assert result['cleaned'] == 2

class TestIntegration:
    """Test integration between database and authentication systems"""

    def test_database_auth_integration(self):
        """Test that database and auth systems work together"""
        # This would test the integration in a real environment
        # For now, we'll just verify the systems can be instantiated
        db_manager = DatabaseManager()
        auth_manager = AuthenticationManager()

        assert db_manager is not None
        assert auth_manager is not None

        # Test that both systems have proper configuration
        assert hasattr(db_manager, 'init_db')
        assert hasattr(auth_manager, 'authenticateUser')

if __name__ == '__main__':
    # Run basic tests
    print("Running enhanced security tests...")

    # Test database connection
    db_test = TestDatabaseConnection()
    try:
        db_test.test_ssl_configuration()
        print("✓ Database SSL configuration test passed")
    except Exception as e:
        print(f"✗ Database SSL configuration test failed: {e}")

    try:
        db_test.test_security_warnings()
        print("✓ Database security warnings test passed")
    except Exception as e:
        print(f"✗ Database security warnings test failed: {e}")

    # Test authentication enhancements
    auth_test = TestAuthenticationEnhancements()
    try:
        auth_test.setup_method()
        auth_test.test_password_validation()
        print("✓ Password validation test passed")
    except Exception as e:
        print(f"✗ Password validation test failed: {e}")

    print("Enhanced security testing completed!")
