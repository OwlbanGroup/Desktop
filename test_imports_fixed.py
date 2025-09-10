#!/usr/bin/env python3
"""
Test imports for the fixed authentication and security modules
"""

print("🧪 Testing Python module imports...")

try:
    # Test basic imports
    import sys
    import os
    print("✅ Basic Python imports OK")

    # Test Flask
    from flask import Flask
    print("✅ Flask import OK")

    # Test authentication module
    sys.path.append('.')
    from OSCAR_BROOME_REVENUE.auth.login_override_fixed import AuthenticationManager
    auth = AuthenticationManager()
    print("✅ Authentication module import OK")

    # Test security middleware
    from OSCAR_BROOME_REVENUE.middleware.security import SecurityMiddleware
    security = SecurityMiddleware()
    print("✅ Security middleware import OK")

    # Test backend server
    from backend.app_server_enhanced import EnhancedBackendServer
    server = EnhancedBackendServer()
    app = server.get_app()
    print("✅ Backend server import OK")

    print("\n🎉 ALL IMPORTS SUCCESSFUL!")
    print("✅ The compatibility issue has been resolved")
    print("✅ Python modules are now properly integrated")

except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    print("🔧 Please check if all dependencies are installed")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n🔧 Please fix the errors above")
