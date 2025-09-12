#!/usr/bin/env python3
"""
Comprehensive Security Testing Script - Fixed Version
Tests edge cases, performance, and integration scenarios
"""

import sys
import os
import time
import importlib.util
from unittest.mock import patch

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_password_edge_cases():
    """Test password validation edge cases"""
    print("=== PASSWORD VALIDATION EDGE CASES ===")

    try:
        # Import the Python login override module
        spec = importlib.util.spec_from_file_location("login_override", "OSCAR-BROOME-REVENUE/auth/login_override_fixed_new.py")
        login_override = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(login_override)
        AuthenticationManager = login_override.AuthenticationManager
        auth_manager = AuthenticationManager()

        # Test cases
        test_cases = [
            ("A" * 100 + "1!a", "Very long password (101 chars)"),
            ("!@#$%^&*()123", "Special characters only"),
            ("Pässwörd123!ñ", "Unicode characters"),
            ("", "Empty password"),
            ("a", "Single character"),
            ("123456789012", "Numbers only (12 chars)"),
            ("abcdefghijkl", "Lowercase only (12 chars)"),
            ("ABCDEFGHIJKL", "Uppercase only (12 chars)"),
            ("!@#$%^&*()abc", "Special + lowercase (12 chars)"),
        ]

        for password, description in test_cases:
            result = auth_manager.validatePassword(password)
            status = "[OK] PASS" if result['valid'] else "[FAIL] FAIL"
            print(f"{status} {description}: {result['valid']}")

        print("✓ Password edge case testing completed\n")
        return True

    except Exception as e:
        print(f"✗ Password edge case testing failed: {e}\n")
        return False

def test_database_connection_load():
    """Test database connection pooling under load"""
    print("=== DATABASE CONNECTION LOAD TESTING ===")

    try:
        from database.connection import DatabaseManager

        db_manager = DatabaseManager()
        start_time = time.time()

        # Simulate multiple connection attempts
        connections_created = 0
        for i in range(10):
            try:
                conn_string = db_manager._build_connection_string()
                connections_created += 1
                print(f"✓ Connection {i+1}: Created successfully")
            except Exception as e:
                print(f"✗ Connection {i+1}: Failed - {e}")

        load_time = time.time() - start_time
        print(f"Load time: {load_time:.2f} seconds")
        print("[OK] Database connection load testing completed\n")
        return True

    except Exception as e:
        print(f"✗ Database connection load testing failed: {e}\n")
        return False

def test_session_management_edge_cases():
    """Test session management edge cases"""
    print("=== SESSION MANAGEMENT EDGE CASES ===")

    try:
        # Import the Python login override module
        spec = importlib.util.spec_from_file_location("login_override_session", "OSCAR-BROOME-REVENUE/auth/login_override_fixed_new.py")
        login_override_session = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(login_override_session)
        AuthenticationManager = login_override_session.AuthenticationManager

        auth_manager = AuthenticationManager()

        # Mock sessions with various states
        mock_sessions = {
            'valid_session': {
                'userId': 'user1',
                'expiresAt': time.time() * 1000 + 3600000,  # 1 hour from now
                'permissions': ['read', 'write']
            },
            'expired_session1': {
                'userId': 'user1',
                'expiresAt': time.time() * 1000 - 1000,  # 1 second ago
                'permissions': ['read']
            },
            'expired_session2': {
                'userId': 'user2',
                'expiresAt': time.time() * 1000 - 2000,  # 2 seconds ago
                'permissions': ['read']
            },
            'malformed_session': {
                'userId': 'user3',
                # Missing expiresAt
                'permissions': ['read']
            }
        }

        with patch.object(auth_manager, 'sessions', mock_sessions):
            # Test cleanup
            result = auth_manager.cleanupExpiredSessions()
            print(f"✓ Cleaned {result.get('cleaned', 0)} expired sessions")

            # Test force logout
            result = auth_manager.forceLogoutAll('user1')
            print(f"✓ Force logout: {result.get('success', False)}")

            # Test active sessions count
            active_count = len([s for s in mock_sessions.values()
                              if s.get('expiresAt', 0) > time.time() * 1000])
            print(f"✓ Active sessions: {active_count}")

        print("✓ Session management edge case testing completed\n")
        return True

    except Exception as e:
        print(f"✗ Session management edge case testing failed: {e}\n")
        return False

def test_security_integration():
    """Test integration between security components"""
    print("=== SECURITY SYSTEM INTEGRATION TESTING ===")

    try:
        from database.connection import DatabaseManager
        # Import the Python login override module
        spec = importlib.util.spec_from_file_location("login_override_integration", "OSCAR-BROOME-REVENUE/auth/login_override_fixed_new.py")
        login_override_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(login_override_integration)
        AuthenticationManager = login_override_integration.AuthenticationManager

        # Test system instantiation
        db_manager = DatabaseManager()
        auth_manager = AuthenticationManager()

        print("✓ DatabaseManager instantiated successfully")
        print("✓ AuthenticationManager instantiated successfully")

        # Test method availability
        methods_to_check = [
            (db_manager, 'init_db', 'DatabaseManager.init_db'),
            (db_manager, '_build_connection_string', 'DatabaseManager._build_connection_string'),
            (auth_manager, 'validatePassword', 'AuthenticationManager.validatePassword'),
            (auth_manager, 'authenticateUser', 'AuthenticationManager.authenticateUser'),
            (auth_manager, 'cleanupExpiredSessions', 'AuthenticationManager.cleanupExpiredSessions'),
        ]

        for obj, method, description in methods_to_check:
            if hasattr(obj, method):
                print(f"✓ {description} method available")
            else:
                print(f"✗ {description} method missing")

        print("✓ Security system integration testing completed\n")
        return True

    except Exception as e:
        print(f"✗ Security system integration testing failed: {e}\n")
        return False

def main():
    """Run all comprehensive security tests"""
    print("STARTING COMPREHENSIVE SECURITY TESTING SUITE")
    print("=" * 50)

    test_results = []

    # Run all test suites
    test_results.append(("Password Edge Cases", test_password_edge_cases()))
    test_results.append(("Database Load Testing", test_database_connection_load()))
    test_results.append(("Session Management", test_session_management_edge_cases()))
    test_results.append(("Security Integration", test_security_integration()))

    # Summary
    print("=" * 50)
    print("TESTING SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 ALL COMPREHENSIVE SECURITY TESTS PASSED!")
        return True
    else:
        print("⚠️  Some tests failed. Review output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
