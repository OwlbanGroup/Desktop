#!/usr/bin/env python3
"""
Simple test for the simplified NVIDIA Control Panel API application
Without JWT dependencies
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports without complex dependencies"""
    try:
        print("Testing basic imports...")

        # Test Flask import
        from flask import Flask
        print("✅ Flask imported successfully")

        # Test basic modules
        import json
        import datetime
        print("✅ Basic modules imported successfully")

        return True
    except Exception as e:
        print(f"❌ Basic import failed: {e}")
        return False

def test_simple_app_creation():
    """Test if the simple app can be created"""
    try:
        print("\nTesting simple app creation...")

        # Try to import the app
        from app_simple import app

        # Get routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        gpu_routes = [route for route in routes if 'gpu' in route.lower()]

        print(f"📊 Total routes: {len(routes)}")
        print(f"🎮 GPU-related routes: {len(gpu_routes)}")

        if gpu_routes:
            print("GPU routes found:")
            for route in gpu_routes[:5]:  # Show first 5
                print(f"  - {route}")

        return True
    except Exception as e:
        print(f"❌ Simple app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        print("\nTesting health endpoint...")

        from app_simple import app

        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Health check passed: {data.get('status')}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_api_docs_endpoint():
    """Test the API docs endpoint"""
    try:
        print("\nTesting API docs endpoint...")

        from app_simple import app

        with app.test_client() as client:
            response = client.get('/api/docs')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ API docs retrieved: {data.get('title')}")
                print(f"📚 Endpoints documented: {len(data.get('endpoints', {}))}")
                return True
            else:
                print(f"❌ API docs failed with status: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ API docs test failed: {e}")
        return False

def test_gpu_status_endpoint():
    """Test the GPU status endpoint with authentication"""
    try:
        print("\nTesting GPU status endpoint...")

        from app_simple import app

        with app.test_client() as client:
            # Test without auth (should fail)
            response = client.get('/api/gpu/status')
            if response.status_code == 401:
                print("✅ Authentication properly required")
            else:
                print(f"⚠️  Unexpected auth response: {response.status_code}")
                return False

            # Test with auth (should succeed)
            headers = {'Authorization': 'Bearer test-token-123'}
            response = client.get('/api/gpu/status', headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ GPU status retrieved: {data.get('gpu_name')}")
                return True
            else:
                print(f"❌ GPU status failed with status: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ GPU status test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Simple Test for Simplified NVIDIA Control Panel API Application")
    print("=" * 70)

    # Test 1: Basic imports
    if not test_basic_imports():
        print("❌ Basic imports test failed")
        return False

    # Test 2: Simple app creation
    if not test_simple_app_creation():
        print("❌ Simple app creation test failed")
        return False

    # Test 3: Health endpoint
    if not test_health_endpoint():
        print("❌ Health endpoint test failed")
        return False

    # Test 4: API docs endpoint
    if not test_api_docs_endpoint():
        print("❌ API docs test failed")
        return False

    # Test 5: GPU status endpoint
    if not test_gpu_status_endpoint():
        print("❌ GPU status test failed")
        return False

    print("\n🎉 All tests passed! The simplified NVIDIA API is working correctly.")
    print("\n📋 Test Token for API calls: test-token-123")
    print("🔗 API Documentation: http://localhost:5000/api/docs")
    print("💚 Health Check: http://localhost:5000/health")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
