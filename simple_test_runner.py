#!/usr/bin/env python3
"""
Simple Test Runner for Oscar Broome Revenue System
Runs basic tests and shows clear output for debugging
"""

import os
import sys
import traceback
import time
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_test_result(test_name, success, message="", duration=None):
    """Print test result with formatting"""
    status = "✅ PASS" if success else "❌ FAIL"
    duration_str = f" ({duration:.2f}s)" if duration else ""
    print(f"{status} {test_name}{duration_str}")
    if message:
        print(f"   {message}")

def test_import_safety():
    """Test that all imports work safely"""
    print_header("Testing Import Safety")

    test_results = []

    # Test basic Python imports
    try:
        import json
        import os
        import sys
        print_test_result("Basic Python imports", True)
        test_results.append(True)
    except Exception as e:
        print_test_result("Basic Python imports", False, str(e))
        test_results.append(False)

    # Test Flask import
    try:
        from flask import Flask
        print_test_result("Flask import", True)
        test_results.append(True)
    except Exception as e:
        print_test_result("Flask import", False, str(e))
        test_results.append(False)

    # Test our custom modules
    modules_to_test = [
        ('backend.app_server_enhanced', 'Enhanced Backend Server'),
        ('database.connection', 'Database Connection'),
        ('caching.redis_cache', 'Redis Cache'),
        ('OSCAR-BROOME-REVENUE.auth.login_override_fixed', 'Authentication System'),
        ('OSCAR-BROOME-REVENUE.middleware.security', 'Security Middleware')
    ]

    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print_test_result(f"{description} import", True)
            test_results.append(True)
        except Exception as e:
            print_test_result(f"{description} import", False, str(e))
            test_results.append(False)

    return all(test_results)

def test_basic_functionality():
    """Test basic functionality of core components"""
    print_header("Testing Basic Functionality")

    test_results = []

    # Test backend server instantiation
    try:
        start_time = time.time()
        from backend.app_server_enhanced import EnhancedBackendServer

        # Create server instance (without running it)
        server = EnhancedBackendServer()
        app = server.get_app()

        duration = time.time() - start_time
        print_test_result("Backend server instantiation", True, f"App created successfully", duration)
        test_results.append(True)

    except Exception as e:
        print_test_result("Backend server instantiation", False, str(e))
        test_results.append(False)

    # Test authentication manager
    try:
        start_time = time.time()
        from OSCAR-BROOME-REVENUE.auth.login_override_fixed import AuthenticationManager

        auth_manager = AuthenticationManager()
        duration = time.time() - start_time
        print_test_result("Authentication manager creation", True, f"Manager created successfully", duration)
        test_results.append(True)

    except Exception as e:
        print_test_result("Authentication manager creation", False, str(e))
        test_results.append(False)

    # Test security middleware
    try:
        start_time = time.time()
        from OSCAR-BROOME-REVENUE.middleware.security import SecurityMiddleware

        security = SecurityMiddleware()
        duration = time.time() - start_time
        print_test_result("Security middleware creation", True, f"Middleware created successfully", duration)
        test_results.append(True)

    except Exception as e:
        print_test_result("Security middleware creation", False, str(e))
        test_results.append(False)

    return all(test_results)

def test_api_endpoints():
    """Test basic API endpoint functionality"""
    print_header("Testing API Endpoints")

    test_results = []

    try:
        from backend.app_server_enhanced import EnhancedBackendServer

        # Create test client
        server = EnhancedBackendServer()
        app = server.get_app()
        client = app.test_client()

        # Test health endpoint
        start_time = time.time()
        response = client.get('/health')
        duration = time.time() - start_time

        if response.status_code == 200:
            print_test_result("Health endpoint", True, f"Status: {response.status_code}", duration)
            test_results.append(True)
        else:
            print_test_result("Health endpoint", False, f"Status: {response.status_code}")
            test_results.append(False)

        # Test API docs endpoint
        start_time = time.time()
        response = client.get('/api/docs')
        duration = time.time() - start_time

        if response.status_code == 200:
            print_test_result("API docs endpoint", True, f"Status: {response.status_code}", duration)
            test_results.append(True)
        else:
            print_test_result("API docs endpoint", False, f"Status: {response.status_code}")
            test_results.append(False)

    except Exception as e:
        print_test_result("API endpoints test", False, str(e))
        test_results.append(False)

    return all(test_results)

def test_database_connection():
    """Test database connection (mocked)"""
    print_header("Testing Database Connection")

    try:
        from database.connection import DatabaseManager

        # Test manager creation
        db_manager = DatabaseManager()
        print_test_result("Database manager creation", True, "Manager created successfully")
        return True

    except Exception as e:
        print_test_result("Database manager creation", False, str(e))
        return False

def main():
    """Main test runner"""
    print(f"🧪 Oscar Broome Revenue System - Test Runner")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python {sys.version}")

    overall_results = []

    # Run all test suites
    test_suites = [
        ("Import Safety", test_import_safety),
        ("Basic Functionality", test_basic_functionality),
        ("API Endpoints", test_api_endpoints),
        ("Database Connection", test_database_connection)
    ]

    for suite_name, test_function in test_suites:
        try:
            result = test_function()
            overall_results.append(result)
        except Exception as e:
            print(f"❌ {suite_name} - CRITICAL ERROR: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            overall_results.append(False)

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(overall_results)
    total = len(overall_results)

    print(f"📊 Tests Passed: {passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")

    if all(overall_results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ System is ready for production")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("🔧 Please review the errors above and fix issues")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
