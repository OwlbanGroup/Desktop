#!/usr/bin/env python3
"""
Debug script to test the simple app and write results to file
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def write_result(message):
    """Write result to debug file"""
    with open('debug_results.txt', 'a') as f:
        f.write(message + '\n')
    print(message)

def test_basic_imports():
    """Test basic imports without complex dependencies"""
    try:
        write_result("Testing basic imports...")

        # Test Flask import
        from flask import Flask
        write_result("✅ Flask imported successfully")

        # Test basic modules
        import json
        import datetime
        write_result("✅ Basic modules imported successfully")

        return True
    except Exception as e:
        write_result(f"❌ Basic import failed: {e}")
        return False

def test_simple_app_creation():
    """Test if the simple app can be created"""
    try:
        write_result("\nTesting simple app creation...")

        # Try to import the app
        from app_simple import app

        # Get routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        gpu_routes = [route for route in routes if 'gpu' in route.lower()]

        write_result(f"📊 Total routes: {len(routes)}")
        write_result(f"🎮 GPU-related routes: {len(gpu_routes)}")

        if gpu_routes:
            write_result("GPU routes found:")
            for route in gpu_routes[:5]:  # Show first 5
                write_result(f"  - {route}")

        return True
    except Exception as e:
        write_result(f"❌ Simple app creation failed: {e}")
        import traceback
        write_result(traceback.format_exc())
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        write_result("\nTesting health endpoint...")

        from app_simple import app

        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                data = response.get_json()
                write_result(f"✅ Health check passed: {data.get('status')}")
                return True
            else:
                write_result(f"❌ Health check failed with status: {response.status_code}")
                return False

    except Exception as e:
        write_result(f"❌ Health endpoint test failed: {e}")
        return False

def test_gpu_status_endpoint():
    """Test the GPU status endpoint with authentication"""
    try:
        write_result("\nTesting GPU status endpoint...")

        from app_simple import app

        with app.test_client() as client:
            # Test without auth (should fail)
            response = client.get('/api/gpu/status')
            if response.status_code == 401:
                write_result("✅ Authentication properly required")
            else:
                write_result(f"⚠️  Unexpected auth response: {response.status_code}")
                return False

            # Test with auth (should succeed)
            headers = {'Authorization': 'Bearer test-token-123'}
            response = client.get('/api/gpu/status', headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                write_result(f"✅ GPU status retrieved: {data.get('gpu_name')}")
                return True
            else:
                write_result(f"❌ GPU status failed with status: {response.status_code}")
                return False

    except Exception as e:
        write_result(f"❌ GPU status test failed: {e}")
        return False

def main():
    """Main test function"""
    # Clear previous results
    if os.path.exists('debug_results.txt'):
        os.remove('debug_results.txt')

    write_result("🚀 Debug Test for Simplified NVIDIA Control Panel API Application")
    write_result("=" * 70)

    # Test 1: Basic imports
    if not test_basic_imports():
        write_result("❌ Basic imports test failed")
        return False

    # Test 2: Simple app creation
    if not test_simple_app_creation():
        write_result("❌ Simple app creation test failed")
        return False

    # Test 3: Health endpoint
    if not test_health_endpoint():
        write_result("❌ Health endpoint test failed")
        return False

    # Test 4: GPU status endpoint
    if not test_gpu_status_endpoint():
        write_result("❌ GPU status test failed")
        return False

    write_result("\n🎉 All tests passed! The simplified NVIDIA API is working correctly.")
    write_result("\n📋 Test Token for API calls: test-token-123")
    write_result("🔗 API Documentation: http://localhost:5000/api/docs")
    write_result("💚 Health Check: http://localhost:5000/health")
    return True

if __name__ == '__main__':
    success = main()
    write_result(f"\nTest completed with success: {success}")
    sys.exit(0 if success else 1)
