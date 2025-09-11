#!/usr/bin/env python3
"""
Simple Integration Test for NVIDIA OSCAR-BROOME-REVENUE Platform

This script performs basic validation of the integration platform.
"""

import sys
import os
import json
import time
import subprocess
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from nvidia_oscar_broome_integration import (
            NVIDIAMonitor,
            app,
            gpu_monitoring_data,
            system_metrics,
            NVIDIA_REQUIREMENTS
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_monitor_initialization():
    """Test NVIDIA monitor initialization."""
    print("Testing monitor initialization...")
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

def test_gpu_data_collection():
    """Test GPU data collection (mocked)."""
    print("Testing GPU data collection...")
    try:
        from nvidia_oscar_broome_integration import NVIDIAMonitor
        from unittest.mock import patch, Mock

        monitor = NVIDIAMonitor()

        # Mock nvidia-smi command
        mock_result = Mock()
        mock_result.stdout = "0, NVIDIA GeForce RTX 3080, 75, 10240, 8192, 65, 470.00\n"
        mock_result.stderr = ""
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            monitor._collect_gpu_data()

        # Check that data was collected
        assert 'gpus' in monitor.gpu_data
        assert len(monitor.gpu_data['gpus']) == 1

        gpu = monitor.gpu_data['gpus'][0]
        assert gpu['name'] == 'NVIDIA GeForce RTX 3080'
        assert gpu['utilization_gpu_percent'] == 75

        print("✅ GPU data collection successful")
        return True
    except Exception as e:
        print(f"❌ GPU data collection failed: {e}")
        return False

def test_system_metrics_collection():
    """Test system metrics collection."""
    print("Testing system metrics collection...")
    try:
        from nvidia_oscar_broome_integration import NVIDIAMonitor
        from unittest.mock import patch, Mock

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

        print("✅ System metrics collection successful")
        return True
    except Exception as e:
        print(f"❌ System metrics collection failed: {e}")
        return False

def test_flask_app():
    """Test Flask application initialization."""
    print("Testing Flask application...")
    try:
        from nvidia_oscar_broome_integration import app

        # Test client
        client = app.test_client()
        client.testing = True

        # Test health endpoint
        response = client.get('/api/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'

        print("✅ Flask application test successful")
        return True
    except Exception as e:
        print(f"❌ Flask application test failed: {e}")
        return False

def test_dashboard_rendering():
    """Test dashboard HTML rendering."""
    print("Testing dashboard rendering...")
    try:
        from nvidia_oscar_broome_integration import app

        client = app.test_client()
        client.testing = True

        response = client.get('/')
        assert response.status_code == 200

        html_content = response.data.decode('utf-8')
        assert 'NVIDIA OSCAR-BROOME-REVENUE Integration Platform' in html_content
        assert 'System Overview' in html_content
        assert 'GPU Monitoring' in html_content

        print("✅ Dashboard rendering test successful")
        return True
    except Exception as e:
        print(f"❌ Dashboard rendering test failed: {e}")
        return False

def test_nvidia_requirements():
    """Test NVIDIA requirements structure."""
    print("Testing NVIDIA requirements...")
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

def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("NVIDIA OSCAR-BROOME-REVENUE INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        test_imports,
        test_monitor_initialization,
        test_gpu_data_collection,
        test_system_metrics_collection,
        test_flask_app,
        test_dashboard_rendering,
        test_nvidia_requirements
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
