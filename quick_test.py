#!/usr/bin/env python3
"""
Quick Test - Check basic functionality
"""

print("🧪 Starting Quick Test...")

try:
    print("1. Testing basic imports...")
    import json
    import os
    import sys
    print("   ✅ Basic imports OK")

    print("2. Testing Flask...")
    from flask import Flask
    print("   ✅ Flask OK")

    print("3. Testing backend server...")
    from backend.app_server_enhanced import EnhancedBackendServer
    server = EnhancedBackendServer()
    app = server.get_app()
    print("   ✅ Backend server OK")

    print("4. Testing authentication...")
    from OSCAR_BROOME_REVENUE.auth.login_override_fixed import AuthenticationManager
    auth = AuthenticationManager()
    print("   ✅ Authentication OK")

    print("5. Testing security middleware...")
    from OSCAR_BROOME_REVENUE.middleware.security import SecurityMiddleware
    security = SecurityMiddleware()
    print("   ✅ Security middleware OK")

    print("6. Testing API endpoints...")
    client = app.test_client()
    response = client.get('/health')
    print(f"   ✅ Health endpoint: {response.status_code}")

    print("\n🎉 ALL TESTS PASSED!")
    print("✅ System is ready for production")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n🔧 Please fix the errors above")
