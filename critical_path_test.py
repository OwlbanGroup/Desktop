#!/usr/bin/env python3
"""
Critical Path Test for NVIDIA OSCAR-BROOME-REVENUE Integration Platform

This script performs essential validation of core functionality.
"""

import sys
import os
import json
import time
import requests
import subprocess
import threading
from unittest.mock import patch, Mock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_critical_imports():
    """Test critical module imports."""
    print("🔍 Testing critical imports...")
    try:
        from nvidia_oscar_broome_integration import (
            NVIDIAMonitor,
            app,
            NVIDIA_REQUIREMENTS
        )
        print("✅ Critical imports successful")
        return True
    except ImportError as e:
        print(f"❌ Critical import failed: {e}")
        return False

def test_monitor_initialization():
    """Test NVIDIA monitor initialization."""
    print("🔍 Testing monitor initialization...")
    try:
        from nvidia_oscar_broome_integration import NVIDIAMonitor
        monitor = NVIDIAMonitor()

        # Check initial state
        assert not monitor.monitoring_active
        assert monitor.monitoring_thread is None
        assert monitor.gpu_data == {}
        assert monitor.system_info == {}

        print("✅ Monitor initialization successful")
        return True
    except Exception as e:
        print(f"❌ Monitor initialization failed: {e}")
        return False

def test_flask_app_creation():
    """Test Flask application creation."""
    print("🔍 Testing Flask application creation...")
    try:
        from nvidia_oscar_broome_integration import app

        # Test that app is created
        assert app is not None
        assert hasattr(app, 'route')
        assert hasattr(app, 'run')

        print("✅ Flask application creation successful")
        return True
    except Exception as e:
        print(f"❌ Flask application creation failed: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint functionality."""
    print("🔍 Testing health endpoint...")
    try:
        from nvidia_oscar_broome_integration import app

        client = app.test_client()
        client.testing = True

        response = client.get('/api/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'

        print("✅ Health endpoint test successful")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_system_info_endpoint():
    """Test system info endpoint functionality."""
    print("🔍 Testing system info endpoint...")
    try:
        from nvidia_oscar_broome_integration import app

        client = app.test_client()
        client.testing = True

        response = client.get('/api/system/info')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'timestamp' in data

        print("✅ System info endpoint test successful")
        return True
    except Exception as e:
        print(f"❌ System info endpoint test failed: {e}")
        return False

def test_dashboard_rendering():
    """Test dashboard HTML rendering."""
    print("🔍 Testing dashboard rendering...")
    try:
        from nvidia_oscar_broome_integration import app

        client = app.test_client()
        client.testing = True

        response = client.get('/')
        assert response.status_code == 200

        html_content = response.data.decode('utf-8')
        assert 'NVIDIA OSCAR-BROOME-REVENUE' in html_content
        assert 'System Overview' in html_content

        print("✅ Dashboard rendering test successful")
        return True
    except Exception as e:
        print(f"❌ Dashboard rendering test failed: {e}")
        return False

def test_gpu_data_collection():
    """Test GPU data collection (mocked)."""
    print("🔍 Testing GPU data collection...")
    try:
        from nvidia_oscar_broome_integration import NVIDIAMonitor, gpu_monitoring_data

        monitor = NVIDIAMonitor()

        # Clear global data
        gpu_monitoring_data.clear()

        # Mock nvidia-smi command
        mock_result = Mock()
        mock_result.stdout = "0, NVIDIA GeForce RTX 3080, 75, 10240, 8192, 65, 470.00\n"
        mock_result.stderr = ""
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            monitor._collect_gpu_data()

        # Check that data was collected in global variable
        assert 'gpus' in gpu_monitoring_data
        assert len(gpu_monitoring_data['gpus']) == 1

        gpu = gpu_monitoring_data['gpus'][0]
        assert gpu['name'] == 'NVIDIA GeForce RTX 3080'
        assert gpu['utilization_gpu_percent'] == 75

        print("✅ GPU data collection test successful")
        return True
    except Exception as e:
        print(f"❌ GPU data collection test failed: {e}")
        return False

def test_system_metrics_collection():
    """Test system metrics collection."""
    print("🔍 Testing system metrics collection...")
    try:
        from nvidia_oscar_broome_integration import NVIDIAMonitor

        monitor = NVIDIAMonitor()

        # Mock psutil functions
        with patch('psutil.cpu_percent', return_value=45.5), \
             patch('psutil.virtual_memory', return_value=Mock(total=17179869184, used=8589934592, percent=50.0)), \
             patch('psutil.disk_usage', return_value=Mock(total=1000000000000, used=500000000000, percent=50.0)), \
             patch('psutil.net_io_counters', return_value=Mock(bytes_sent=1000000, bytes_recv=2000000)):

            monitor._collect_system_metrics()

        # Check system info
        assert monitor.system_info['cpu_percent'] == 45.5
        assert monitor.system_info['memory_percent'] == 50.0
        assert monitor.system_info['disk_percent'] == 50.0

        print("✅ System metrics collection test successful")
        return True
    except Exception as e:
        print(f"❌ System metrics collection test failed: {e}")
        return False

def test_nvidia_requirements():
    """Test NVIDIA requirements structure."""
    print("🔍 Testing NVIDIA requirements...")
    try:
        from nvidia_oscar_broome_integration import NVIDIA_REQUIREMENTS

        required_keys = [
            'min_driver_version',
            'recommended_driver_version',
            'min_cuda_version',
            'recommended_cuda_version',
            'min_vram',
            'recommended_vram'
        ]

        for key in required_keys:
            assert key in NVIDIA_REQUIREMENTS

        print("✅ NVIDIA requirements test successful")
        return True
    except Exception as e:
        print(f"❌ NVIDIA requirements test failed: {e}")
        return False

def run_critical_path_tests():
    """Run all critical path tests."""
    print("=" * 60)
    print("CRITICAL PATH TEST SUITE")
    print("NVIDIA OSCAR-BROOME-REVENUE INTEGRATION PLATFORM")
    print("=" * 60)

    critical_tests = [
        test_critical_imports,
        test_monitor_initialization,
        test_flask_app_creation,
        test_health_endpoint,
        test_system_info_endpoint,
        test_dashboard_rendering,
        test_gpu_data_collection,
        test_system_metrics_collection,
        test_nvidia_requirements
    ]

    passed = 0
    failed = 0
    results = []

    for test in critical_tests:
        try:
            result = test()
            results.append((test.__name__, result))
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append((test.__name__, False))
            failed += 1

    print("\n" + "=" * 60)
    print("CRITICAL PATH TEST RESULTS")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n📊 SUMMARY: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 ALL CRITICAL PATH TESTS PASSED!")
        print("🚀 The integration platform is ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {failed} critical test(s) failed.")
        print("🔧 Please review the failures before deployment.")
        return False

if __name__ == '__main__':
    success = run_critical_path_tests()
    sys.exit(0 if success else 1)
