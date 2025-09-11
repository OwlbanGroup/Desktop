#!/usr/bin/env python3
"""
Comprehensive Test Suite for NVIDIA OSCAR-BROOME-REVENUE Integration Platform

This test suite validates:
- GPU monitoring functionality
- Flask API endpoints
- System metrics collection
- Financial integration
- Dashboard UI rendering
- Error handling and edge cases
"""

import unittest
import json
import subprocess
import sys
import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import requests
from flask import Flask
import psutil
import platform

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from nvidia_oscar_broome_integration import (
        NVIDIAMonitor,
        app,
        gpu_monitoring_data,
        system_metrics,
        NVIDIA_REQUIREMENTS
    )
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Warning: Could not import integration modules: {e}")
    IMPORTS_SUCCESSFUL = False

class TestNVIDIAMonitor(unittest.TestCase):
    """Test cases for NVIDIA GPU monitoring system."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = NVIDIAMonitor()

    def tearDown(self):
        """Clean up after tests."""
        if self.monitor.monitoring_active:
            self.monitor.stop_monitoring()

    def test_monitor_initialization(self):
        """Test monitor initialization."""
        self.assertFalse(self.monitor.monitoring_active)
        self.assertIsNone(self.monitor.monitoring_thread)
        self.assertEqual(self.monitor.gpu_data, {})
        self.assertEqual(self.monitor.system_info, {})

    def test_monitor_start_stop(self):
        """Test starting and stopping monitoring."""
        # Start monitoring
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.monitoring_active)
        self.assertIsNotNone(self.monitor.monitoring_thread)
        self.assertTrue(self.monitor.monitoring_thread.is_alive())

        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_active)
        time.sleep(0.1)  # Allow thread to finish

    @patch('subprocess.run')
    def test_gpu_data_collection_success(self, mock_subprocess):
        """Test successful GPU data collection."""
        mock_result = Mock()
        mock_result.stdout = "0, NVIDIA GeForce RTX 3080, 75, 10240, 8192, 65, 470.00\n"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        self.monitor._collect_gpu_data()

        # Check that GPU data was collected
        self.assertIn('gpus', self.monitor.gpu_data)
        self.assertEqual(len(self.monitor.gpu_data['gpus']), 1)

        gpu = self.monitor.gpu_data['gpus'][0]
        self.assertEqual(gpu['index'], 0)
        self.assertEqual(gpu['name'], 'NVIDIA GeForce RTX 3080')
        self.assertEqual(gpu['utilization_gpu_percent'], 75)
        self.assertEqual(gpu['memory_total_mb'], 10240)
        self.assertEqual(gpu['memory_used_mb'], 8192)
        self.assertEqual(gpu['temperature_celsius'], 65)
        self.assertEqual(gpu['driver_version'], '470.00')

    @patch('subprocess.run')
    def test_gpu_data_collection_failure(self, mock_subprocess):
        """Test GPU data collection failure."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'nvidia-smi', stderr='Command failed')

        # Should not raise exception
        self.monitor._collect_gpu_data()

        # GPU data should be empty list
        self.assertEqual(self.monitor.gpu_data, {'gpus': []})

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    def test_system_metrics_collection(self, mock_net, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection."""
        # Mock system data
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(total=17179869184, used=8589934592, percent=50.0)
        mock_disk.return_value = Mock(total=1000000000000, used=500000000000, percent=50.0)
        mock_net.return_value = Mock(bytes_sent=1000000, bytes_recv=2000000)

        self.monitor._collect_system_metrics()

        # Check system info
        self.assertAlmostEqual(self.monitor.system_info['cpu_percent'], 45.5)
        self.assertEqual(self.monitor.system_info['memory_total_mb'], 16384)
        self.assertEqual(self.monitor.system_info['memory_used_mb'], 8192)
        self.assertEqual(self.monitor.system_info['memory_percent'], 50.0)
        self.assertEqual(self.monitor.system_info['disk_total_gb'], 931)
        self.assertEqual(self.monitor.system_info['disk_used_gb'], 465)
        self.assertEqual(self.monitor.system_info['disk_percent'], 50.0)
        self.assertEqual(self.monitor.system_info['net_bytes_sent'], 1000000)
        self.assertEqual(self.monitor.system_info['net_bytes_recv'], 2000000)

class TestFlaskAPI(unittest.TestCase):
    """Test cases for Flask API endpoints."""

    def setUp(self):
        """Set up test client."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Integration modules not available")

        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('services', data)
        self.assertEqual(data['status'], 'healthy')

    def test_nvidia_requirements_endpoint(self):
        """Test NVIDIA requirements endpoint."""
        response = self.app.get('/api/nvidia_requirements')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('min_driver_version', data)
        self.assertIn('recommended_driver_version', data)
        self.assertIn('min_cuda_version', data)
        self.assertIn('recommended_cuda_version', data)
        self.assertIn('min_vram', data)
        self.assertIn('recommended_vram', data)

    def test_system_info_endpoint(self):
        """Test system info endpoint."""
        response = self.app.get('/api/system/info')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('system', data['data'])

        system_info = data['data']['system']
        self.assertIn('system', system_info)
        self.assertIn('release', system_info)
        self.assertIn('version', system_info)
        self.assertIn('machine', system_info)
        self.assertIn('processor', system_info)

    def test_dashboard_rendering(self):
        """Test dashboard HTML rendering."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        html_content = response.data.decode('utf-8')
        self.assertIn('NVIDIA OSCAR-BROOME-REVENUE Integration Platform', html_content)
        self.assertIn('Real-time GPU monitoring', html_content)
        self.assertIn('System Overview', html_content)
        self.assertIn('GPU Monitoring', html_content)
        self.assertIn('Financial Integration', html_content)

class TestIntegration(unittest.TestCase):
    """Test cases for overall integration."""

    def setUp(self):
        """Set up integration tests."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Integration modules not available")

    def test_global_state_management(self):
        """Test global state management."""
        # Test initial state
        self.assertIsInstance(gpu_monitoring_data, dict)
        self.assertIsInstance(system_metrics, dict)

        # Test NVIDIA requirements structure
        self.assertIsInstance(NVIDIA_REQUIREMENTS, dict)
        required_keys = ['min_driver_version', 'recommended_driver_version',
                        'min_cuda_version', 'recommended_cuda_version',
                        'min_vram', 'recommended_vram']
        for key in required_keys:
            self.assertIn(key, NVIDIA_REQUIREMENTS)

    def test_monitor_integration(self):
        """Test monitor integration with global state."""
        monitor = NVIDIAMonitor()

        # Start monitoring briefly
        monitor.start_monitoring()
        time.sleep(0.1)  # Allow some data collection

        # Check that global state is updated
        self.assertIsInstance(gpu_monitoring_data, dict)
        self.assertIsInstance(system_metrics, dict)

        monitor.stop_monitoring()

class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""

    def setUp(self):
        """Set up error handling tests."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Integration modules not available")

        self.app = app.test_client()
        self.app.testing = True

    def test_invalid_endpoint(self):
        """Test invalid endpoint handling."""
        response = self.app.get('/api/invalid-endpoint')
        self.assertEqual(response.status_code, 404)

    def test_method_not_allowed(self):
        """Test method not allowed handling."""
        response = self.app.post('/api/health')  # Health endpoint only supports GET
        self.assertEqual(response.status_code, 405)

class TestPerformance(unittest.TestCase):
    """Test cases for performance validation."""

    def setUp(self):
        """Set up performance tests."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Integration modules not available")

    def test_monitor_performance(self):
        """Test monitoring system performance."""
        monitor = NVIDIAMonitor()

        start_time = time.time()
        monitor.start_monitoring()
        time.sleep(1)  # Run for 1 second
        monitor.stop_monitoring()
        end_time = time.time()

        execution_time = end_time - start_time
        # Should complete within reasonable time (allowing for thread cleanup)
        self.assertLess(execution_time, 5.0)

def run_integration_tests():
    """Run comprehensive integration tests."""
    print("Running NVIDIA OSCAR-BROOME-REVENUE Integration Tests...")
    print("=" * 60)

    # Test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestNVIDIAMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    if result.skipped:
        print("\nSKIPPED:")
        for test, reason in result.skipped:
            print(f"- {test}: {reason}")

    # Overall result
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        return False

if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
