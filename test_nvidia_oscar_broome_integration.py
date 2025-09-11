#!/usr/bin/env python3
"""
Critical Path Test for NVIDIA OSCAR-BROOME-REVENUE Integration

Tests the core functionality of the integration platform:
- Application startup
- Health check endpoint
- GPU monitoring endpoints
- System metrics endpoints
- Financial analytics endpoints
- Leadership system endpoints
- Payment integration endpoints
"""

import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread

def test_application_startup():
    """Test if the Flask application starts successfully."""
    print("Testing application startup...")
    try:
        # Start the application in a separate thread
        def start_app():
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            subprocess.run([sys.executable, 'integrated_financial_nvidia_app.py'],
                         capture_output=True, timeout=10)

        app_thread = Thread(target=start_app, daemon=True)
        app_thread.start()
        time.sleep(3)  # Wait for app to start

        # Test health endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Application startup successful")
            print(f"  Health status: {data['data']['status']}")
            return True
        else:
            print("[FAIL] Application startup failed")
            return False
    except Exception as e:
        print(f"[FAIL] Application startup error: {e}")
        return False

def test_gpu_monitoring():
    """Test GPU monitoring endpoints."""
    print("\nTesting GPU monitoring...")
    try:
        response = requests.get('http://localhost:5000/api/nvidia/gpu/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] GPU status endpoint working")
            # Adjusted to print actual data keys
            print(f"  GPU count: {len(data.get('data', {}).get('gpus', []))}")
            return True
        else:
            print("[FAIL] GPU status endpoint failed")
            return False
    except Exception as e:
        print(f"[FAIL] GPU monitoring error: {e}")
        return False

def test_system_metrics():
    """Test system metrics endpoints."""
    print("\nTesting system metrics...")
    try:
        response = requests.get('http://localhost:5000/api/system/info', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] System metrics endpoint working")
            print(f"  System name: {data['data']['system']['name']}")
            return True
        else:
            print("[FAIL] System metrics endpoint failed")
            return False
    except Exception as e:
        print(f"[FAIL] System metrics error: {e}")
        return False

def test_financial_analytics():
    """Test financial analytics endpoints."""
    print("\nTesting financial analytics...")
    try:
        response = requests.get('http://localhost:5000/api/financial/analytics', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Financial analytics endpoint working")
            print(f"  Analytics count: {len(data['data']['analytics'])}")
            return True
        else:
            print("[FAIL] Financial analytics endpoint failed")
            return False
    except Exception as e:
        print(f"[FAIL] Financial analytics error: {e}")
        return False

def test_leadership_system():
    """Test leadership system endpoints."""
    print("\nTesting leadership system...")
    try:
        # Test POST team creation
        team_data = {
            'leader_name': 'Alice',
            'leadership_style': 'DEMOCRATIC',
            'team_members': ['Bob:Developer', 'Charlie:Designer']
        }
        response = requests.post('http://localhost:5000/api/leadership/team',
                               json=team_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Leadership system endpoint working")
            print(f"  Team size: {data['data']['team_size']}")
            return True
        else:
            print("[FAIL] Leadership system endpoint failed")
            return False
    except Exception as e:
        print(f"[FAIL] Leadership system error: {e}")
        return False

def test_payment_integration():
    """Test payment integration endpoints."""
    print("\nTesting payment integration...")
    try:
        # Test payment creation
        payment_data = {
            'amount': 100.00,
            'currency': 'USD',
            'method': 'credit_card',
            'description': 'Test payment'
        }
        response = requests.post('http://localhost:5000/api/payment/create',
                               json=payment_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Payment processing endpoint working")
            print(f"  Payment ID: {data['data']['payment_id']}")
            return True
        else:
            print("[FAIL] Payment processing endpoint failed")
            return False
    except Exception as e:
        print(f"[FAIL] Payment integration error: {e}")
        return False

def test_nvidia_benefits():
    """Test NVIDIA benefits endpoint."""
    print("\nTesting NVIDIA benefits...")
    try:
        response = requests.get('http://localhost:5000/api/nvidia/benefits', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] NVIDIA benefits endpoint working")
            print(f"  Benefits count: {len(data['data']['benefits'])}")
            return True
        else:
            print("[FAIL] NVIDIA benefits endpoint failed")
            return False
    except Exception as e:
        print(f"[FAIL] NVIDIA benefits error: {e}")
        return False

def test_financial_predictions():
    """Test financial predictions endpoint."""
    print("\nTesting financial predictions...")
    try:
        response = requests.get('http://localhost:5000/api/financial/predictions', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Financial predictions endpoint working")
            print(f"  Predictions count: {len(data['data']['predictions'])}")
            return True
        else:
            print("[FAIL] Financial predictions endpoint failed")
            return False
    except Exception as e:
        print(f"[FAIL] Financial predictions error: {e}")
        return False

def main():
    """Run all critical path tests."""
    print("=" * 60)
    print("CRITICAL PATH TESTING - NVIDIA OSCAR-BROOME-REVENUE INTEGRATION")
    print("=" * 60)

    # Start Flask app in background
    print("\nStarting Flask application...")
    app_process = subprocess.Popen([sys.executable, 'integrated_financial_nvidia_app.py'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for app to start
    time.sleep(5)

    test_results = []

    # Run tests
    test_results.append(("Application Startup", test_application_startup()))
    test_results.append(("GPU Monitoring", test_gpu_monitoring()))
    test_results.append(("System Metrics", test_system_metrics()))
    test_results.append(("Financial Analytics", test_financial_analytics()))
    test_results.append(("Leadership System", test_leadership_system()))
    test_results.append(("Payment Integration", test_payment_integration()))
    test_results.append(("NVIDIA Benefits", test_nvidia_benefits()))
    test_results.append(("Financial Predictions", test_financial_predictions()))

    # Stop the Flask app
    print("\nStopping Flask application...")
    app_process.terminate()
    app_process.wait()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All critical path tests passed!")
        return True
    else:
        print("[WARNING] Some tests failed. Please review the implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
