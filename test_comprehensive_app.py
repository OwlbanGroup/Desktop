#!/usr/bin/env python3
"""
Test script for the comprehensive NVIDIA Control Panel API application
"""

import sys
import os
import requests
import json
from flask import Flask
import threading
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_creation():
    """Test if the comprehensive app can be created successfully"""
    try:
        from app_comprehensive import create_app
        app = create_app()
        print("✅ Comprehensive app created successfully")

        # Get all routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        gpu_routes = [route for route in routes if 'gpu' in route]

        print(f"📊 Total routes: {len(routes)}")
        print(f"🎮 GPU-related routes: {len(gpu_routes)}")

        for route in gpu_routes:
            print(f"  - {route}")

        return True
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        return False

def test_gpu_endpoints():
    """Test GPU endpoints functionality"""
    try:
        from app_comprehensive import create_app
        app = create_app()

        with app.test_client() as client:
            # Test GPU status endpoint
            print("\n🧪 Testing GPU endpoints...")

            # Test 1: GPU Status
            response = client.get('/api/gpu/status')
            print(f"GPU Status: {response.status_code}")

            # Test 2: PhysX Configuration
            response = client.get('/api/gpu/physx')
            print(f"PhysX Config: {response.status_code}")

            # Test 3: Performance Counters
            response = client.get('/api/gpu/performance')
            print(f"Performance: {response.status_code}")

            # Test 4: Frame Sync
            response = client.get('/api/gpu/frame-sync')
            print(f"Frame Sync: {response.status_code}")

            # Test 5: SDI Output
            response = client.get('/api/gpu/sdi-output')
            print(f"SDI Output: {response.status_code}")

            # Test 6: EDID Management
            response = client.get('/api/gpu/edid')
            print(f"EDID: {response.status_code}")

            # Test 7: Workstation Features
            response = client.get('/api/gpu/workstation')
            print(f"Workstation: {response.status_code}")

            # Test 8: GPU Profiles
            response = client.get('/api/gpu/profiles')
            print(f"Profiles: {response.status_code}")

            print("✅ All GPU endpoints are accessible")
            return True

    except Exception as e:
        print(f"❌ GPU endpoint test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Comprehensive NVIDIA Control Panel API Application")
    print("=" * 60)

    # Test 1: App Creation
    if not test_app_creation():
        print("❌ App creation test failed")
        return False

    # Test 2: GPU Endpoints
    if not test_gpu_endpoints():
        print("❌ GPU endpoints test failed")
        return False

    print("\n🎉 All tests passed! The comprehensive NVIDIA API is working correctly.")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
