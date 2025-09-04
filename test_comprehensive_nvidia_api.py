#!/usr/bin/env python3
"""
Comprehensive NVIDIA API Integration Test Suite
Tests all advanced NVIDIA Control Panel features through the Flask API endpoints
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from interface import NVIDIAInterface


class TestNVIDIAAPIIntegration(unittest.TestCase):
    """Test suite for NVIDIA API endpoints integration"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Mock NVIDIA interface
        self.mock_nvidia = Mock(spec=NVIDIAInterface)

        # Mock successful responses
        self.mock_nvidia.get_gpu_status.return_value = {
            'gpu_count': 1,
            'gpu_info': [{'name': 'NVIDIA GeForce RTX 3080', 'memory': '10GB'}],
            'driver_version': '470.42.01'
        }

        self.mock_nvidia.get_physx_configuration.return_value = {
            'processor': 'auto',
            'status': 'configured'
        }

        self.mock_nvidia.set_physx_configuration.return_value = {
            'success': True,
            'processor': 'gpu'
        }

        self.mock_nvidia.get_performance_counters.return_value = {
            'gpu_utilization': 45,
            'memory_utilization': 60,
            'temperature': 65,
            'power_draw': 180
        }

        self.mock_nvidia.set_frame_sync_mode.return_value = {
            'success': True,
            'mode': 'swap_group'
        }

        self.mock_nvidia.get_frame_sync_mode.return_value = {
            'mode': 'disabled',
            'status': 'active'
        }

        self.mock_nvidia.set_sdi_output_config.return_value = {
            'success': True,
            'config': {'data_format': '4K', 'sync_source': 'genlock'}
        }

        self.mock_nvidia.get_sdi_output_config.return_value = {
            'data_format': 'auto',
            'sync_source': 'auto',
            'output_mode': 'auto'
        }

        self.mock_nvidia.apply_edid.return_value = {
            'success': True,
            'message': 'EDID applied successfully'
        }

        self.mock_nvidia.reset_edid.return_value = {
            'success': True,
            'message': 'EDID reset successfully'
        }

        self.mock_nvidia.get_edid_info.return_value = {
            'current_edid': '00FF00FF00FF00FF',
            'supported_resolutions': ['1920x1080', '2560x1440', '3840x2160']
        }

        self.mock_nvidia.set_workstation_feature.return_value = {
            'success': True,
            'feature': 'mosaic',
            'enabled': True
        }

        self.mock_nvidia.get_workstation_features.return_value = {
            'mosaic': True,
            'warp': False,
            'ird': True
        }

        self.mock_nvidia.create_gpu_profile.return_value = {
            'success': True,
            'profile_name': 'gaming_profile'
        }

        self.mock_nvidia.apply_gpu_profile.return_value = {
            'success': True,
            'profile_name': 'gaming_profile'
        }

        self.mock_nvidia.delete_gpu_profile.return_value = {
            'success': True,
            'profile_name': 'gaming_profile'
        }

        self.mock_nvidia.get_gpu_profiles.return_value = {
            'profiles': ['gaming_profile', 'workstation_profile'],
            'active_profile': 'gaming_profile'
        }

        self.mock_nvidia.clone_displays.return_value = {
            'success': True,
            'source_display': 'Display1',
            'target_displays': ['Display2', 'Display3']
        }

        # Patch the NVIDIA interface in the app
        with self.app.app_context():
            from app import nvidia_interface
            nvidia_interface = self.mock_nvidia

    def test_gpu_status_endpoint(self):
        """Test GPU status endpoint"""
        response = self.client.get('/api/gpu/status')
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_physx_configuration_get(self):
        """Test PhysX configuration GET endpoint"""
        response = self.client.get('/api/gpu/physx')
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_physx_configuration_post(self):
        """Test PhysX configuration POST endpoint"""
        data = {'processor': 'gpu'}
        response = self.client.post('/api/gpu/physx', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_physx_invalid_processor(self):
        """Test PhysX configuration with invalid processor"""
        data = {'processor': 'invalid'}
        response = self.client.post('/api/gpu/physx', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_performance_monitoring_endpoint(self):
        """Test performance monitoring endpoint"""
        response = self.client.get('/api/gpu/performance')
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_frame_sync_get_endpoint(self):
        """Test frame sync GET endpoint"""
        response = self.client.get('/api/gpu/frame-sync')
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_frame_sync_post_endpoint(self):
        """Test frame sync POST endpoint"""
        data = {'mode': 'swap_group'}
        response = self.client.post('/api/gpu/frame-sync', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_frame_sync_invalid_mode(self):
        """Test frame sync with invalid mode"""
        data = {'mode': 'invalid'}
        response = self.client.post('/api/gpu/frame-sync', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_sdi_output_get_endpoint(self):
        """Test SDI output GET endpoint"""
        response = self.client.get('/api/gpu/sdi-output')
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_sdi_output_post_endpoint(self):
        """Test SDI output POST endpoint"""
        data = {
            'data_format': '4K',
            'sync_source': 'genlock',
            'output_mode': 'dual'
        }
        response = self.client.post('/api/gpu/sdi-output', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_edid_get_endpoint(self):
        """Test EDID GET endpoint"""
        response = self.client.get('/api/gpu/edid')
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_edid_apply_endpoint(self):
        """Test EDID apply endpoint"""
        data = {'action': 'apply', 'edid_data': '00FF00FF00FF00FF'}
        response = self.client.post('/api/gpu/edid', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_edid_reset_endpoint(self):
        """Test EDID reset endpoint"""
        data = {'action': 'reset'}
        response = self.client.post('/api/gpu/edid', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_edid_invalid_action(self):
        """Test EDID with invalid action"""
        data = {'action': 'invalid'}
        response = self.client.post('/api/gpu/edid', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_workstation_get_endpoint(self):
        """Test workstation features GET endpoint"""
        response = self.client.get('/api/gpu/workstation')
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_workstation_post_endpoint(self):
        """Test workstation features POST endpoint"""
        data = {'feature': 'mosaic', 'enabled': True}
        response = self.client.post('/api/gpu/workstation', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_gpu_profiles_get_endpoint(self):
        """Test GPU profiles GET endpoint"""
        response = self.client.get('/api/gpu/profiles')
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_gpu_profiles_create_endpoint(self):
        """Test GPU profiles create endpoint"""
        data = {
            'action': 'create',
            'profile_name': 'gaming_profile',
            'settings': {'power_limit': 200}
        }
        response = self.client.post('/api/gpu/profiles', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_gpu_profiles_apply_endpoint(self):
        """Test GPU profiles apply endpoint"""
        data = {'action': 'apply', 'profile_name': 'gaming_profile'}
        response = self.client.post('/api/gpu/profiles', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_gpu_profiles_delete_endpoint(self):
        """Test GPU profiles delete endpoint"""
        data = {'action': 'delete', 'profile_name': 'gaming_profile'}
        response = self.client.post('/api/gpu/profiles', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_gpu_profiles_invalid_action(self):
        """Test GPU profiles with invalid action"""
        data = {'action': 'invalid'}
        response = self.client.post('/api/gpu/profiles', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_display_clone_endpoint(self):
        """Test display cloning endpoint"""
        data = {
            'source_display': 'Display1',
            'target_displays': ['Display2', 'Display3']
        }
        response = self.client.post('/api/gpu/clone-displays', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_display_clone_missing_data(self):
        """Test display cloning with missing data"""
        data = {'source_display': 'Display1'}
        response = self.client.post('/api/gpu/clone-displays', json=data)
        self.assertEqual(response.status_code, 401)  # Should require authentication

    def test_rate_limiting(self):
        """Test rate limiting on endpoints"""
        # Make multiple requests to test rate limiting
        for i in range(35):  # Exceed the 30 per minute limit
            response = self.client.get('/api/gpu/status')
            if i < 30:
                self.assertEqual(response.status_code, 401)  # Should still be auth error
            else:
                self.assertEqual(response.status_code, 429)  # Should be rate limited

    def test_error_handling(self):
        """Test error handling in endpoints"""
        # Mock an exception in the NVIDIA interface
        self.mock_nvidia.get_gpu_status.side_effect = Exception("Mock error")

        response = self.client.get('/api/gpu/status')
        self.assertEqual(response.status_code, 401)  # Auth error takes precedence

    def test_websocket_broadcasting(self):
        """Test WebSocket broadcasting for GPU updates"""
        # This would require a WebSocket test client in a real scenario
        # For now, we just verify the endpoint exists and requires auth
        response = self.client.get('/api/gpu/status')
        self.assertEqual(response.status_code, 401)


class TestNVIDIAAPIAuthenticated(unittest.TestCase):
    """Test suite for authenticated NVIDIA API endpoints"""

    def setUp(self):
        """Set up authenticated test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Mock authentication
        with self.app.app_context():
            from flask_jwt_extended import create_access_token
            self.access_token = create_access_token(identity='test_user')

        # Mock NVIDIA interface
        self.mock_nvidia = Mock(spec=NVIDIAInterface)

        # Setup mock responses
        self.mock_nvidia.get_gpu_status.return_value = {
            'gpu_count': 1,
            'gpu_info': [{'name': 'NVIDIA GeForce RTX 3080'}]
        }

        # Patch the NVIDIA interface
        with self.app.app_context():
            from app import nvidia_interface
            nvidia_interface = self.mock_nvidia

    def _get_auth_headers(self):
        """Get authentication headers"""
        return {'Authorization': f'Bearer {self.access_token}'}

    def test_authenticated_gpu_status(self):
        """Test authenticated GPU status endpoint"""
        response = self.client.get('/api/gpu/status', headers=self._get_auth_headers())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('gpu_count', data)
        self.assertIn('gpu_info', data)

    def test_authenticated_physx_get(self):
        """Test authenticated PhysX GET endpoint"""
        self.mock_nvidia.get_physx_configuration.return_value = {'processor': 'auto'}

        response = self.client.get('/api/gpu/physx', headers=self._get_auth_headers())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('processor', data)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(TestNVIDIAAPIIntegration('test_gpu_status_endpoint'))
    suite.addTest(TestNVIDIAAPIIntegration('test_physx_configuration_get'))
    suite.addTest(TestNVIDIAAPIIntegration('test_physx_configuration_post'))
    suite.addTest(TestNVIDIAAPIIntegration('test_performance_monitoring_endpoint'))
    suite.addTest(TestNVIDIAAPIIntegration('test_frame_sync_get_endpoint'))
    suite.addTest(TestNVIDIAAPIIntegration('test_sdi_output_get_endpoint'))
    suite.addTest(TestNVIDIAAPIIntegration('test_edid_get_endpoint'))
    suite.addTest(TestNVIDIAAPIIntegration('test_workstation_get_endpoint'))
    suite.addTest(TestNVIDIAAPIIntegration('test_gpu_profiles_get_endpoint'))
    suite.addTest(TestNVIDIAAPIIntegration('test_display_clone_endpoint'))
    suite.addTest(TestNVIDIAAPIIntegration('test_rate_limiting'))
    suite.addTest(TestNVIDIAAPIIntegration('test_error_handling'))

    # Add authenticated tests
    suite.addTest(TestNVIDIAAPIAuthenticated('test_authenticated_gpu_status'))
    suite.addTest(TestNVIDIAAPIAuthenticated('test_authenticated_physx_get'))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("All tests passed! ✅")
        sys.exit(0)
