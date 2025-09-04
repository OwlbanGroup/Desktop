#!/usr/bin/env python3

import sys
import os
import json
import subprocess
import time
import requests
from datetime import datetime

def log_message(message, status="INFO"):
    """Log messages with timestamps"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{status}] {message}")

def test_basic_endpoints():
    """Test basic API endpoints"""
    log_message("Testing basic API endpoints...")

    # Start Flask app
    log_message("Starting Flask application...")
    process = subprocess.Popen(
        [sys.executable, 'app_simple.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )

    # Wait for app to start
    time.sleep(3)

    try:
        base_url = "http://localhost:5000"

        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health")
            log_message(f"Health endpoint: {response.status_code}")
            if response.status_code == 200:
                log_message("✅ Health endpoint working")
            else:
                log_message(f"❌ Health endpoint failed: {response.status_code}")
        except Exception as e:
            log_message(f"❌ Health endpoint error: {e}")

        # Test API docs endpoint
        try:
            response = requests.get(f"{base_url}/api/docs")
            log_message(f"API docs endpoint: {response.status_code}")
            if response.status_code == 200:
                log_message("✅ API docs endpoint working")
            else:
                log_message(f"❌ API docs endpoint failed: {response.status_code}")
        except Exception as e:
            log_message(f"❌ API docs endpoint error: {e}")

        # Test GPU status endpoint
        try:
            response = requests.get(f"{base_url}/api/gpu/status")
            log_message(f"GPU status endpoint: {response.status_code}")
            if response.status_code == 200:
                log_message("✅ GPU status endpoint working")
                try:
                    data = response.json()
                    log_message(f"Response data: {json.dumps(data, indent=2)}")
                except:
                    log_message(f"Response text: {response.text[:200]}")
            else:
                log_message(f"❌ GPU status endpoint failed: {response.status_code}")
        except Exception as e:
            log_message(f"❌ GPU status endpoint error: {e}")

        # Test a few more endpoints
        endpoints_to_test = [
            '/api/gpu/physx',
            '/api/gpu/performance',
            '/api/gpu/frame-sync'
        ]

        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}")
                log_message(f"{endpoint}: {response.status_code}")
                if response.status_code == 200:
                    log_message(f"✅ {endpoint} working")
                else:
                    log_message(f"❌ {endpoint} failed: {response.status_code}")
            except Exception as e:
                log_message(f"❌ {endpoint} error: {e}")

    finally:
        # Clean up
        if process and process.poll() is None:
            log_message("Stopping Flask application...")
            process.terminate()
            process.wait()
            log_message("✅ Flask application stopped")

def main():
    """Main test function"""
    log_message("=== Simple NVIDIA Control Panel API Test ===")

    test_basic_endpoints()

    log_message("Simple API test completed")

if __name__ == "__main__":
    main()
