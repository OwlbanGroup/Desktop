#!/usr/bin/env python3
"""
Simple NVIDIA API Test
Basic test to verify the NVIDIA API endpoints are properly registered
"""

import unittest
import json
from app import create_app


class TestNVIDIAAPISimple(unittest.TestCase):
    """Simple test for NVIDIA API endpoints"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_app_creation(self):
        """Test that the app can be created"""
        self.assertIsNotNone(self.app)

    def test_gpu_status_endpoint_exists(self):
        """Test that GPU status endpoint exists"""
        with self.app.test_request_context():
            # Check if the endpoint is registered
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            gpu_status_rule = any('gpu/status' in rule for rule in rules)
            self.assertTrue(gpu_status_rule, "GPU status endpoint should be registered")

    def test_physx_endpoint_exists(self):
        """Test that PhysX endpoint exists"""
        with self.app.test_request_context():
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            physx_rule = any('gpu/physx' in rule for rule in rules)
            self.assertTrue(physx_rule, "PhysX endpoint should be registered")

    def test_performance_endpoint_exists(self):
        """Test that performance endpoint exists"""
        with self.app.test_request_context():
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            performance_rule = any('gpu/performance' in rule for rule in rules)
            self.assertTrue(performance_rule, "Performance endpoint should be registered")

    def test_frame_sync_endpoint_exists(self):
        """Test that frame sync endpoint exists"""
        with self.app.test_request_context():
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            frame_sync_rule = any('gpu/frame-sync' in rule for rule in rules)
            self.assertTrue(frame_sync_rule, "Frame sync endpoint should be registered")

    def test_sdi_output_endpoint_exists(self):
        """Test that SDI output endpoint exists"""
        with self.app.test_request_context():
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            sdi_rule = any('gpu/sdi-output' in rule for rule in rules)
            self.assertTrue(sdi_rule, "SDI output endpoint should be registered")

    def test_edid_endpoint_exists(self):
        """Test that EDID endpoint exists"""
        with self.app.test_request_context():
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            edid_rule = any('gpu/edid' in rule for rule in rules)
            self.assertTrue(edid_rule, "EDID endpoint should be registered")

    def test_workstation_endpoint_exists(self):
        """Test that workstation endpoint exists"""
        with self.app.test_request_context():
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            workstation_rule = any('gpu/workstation' in rule for rule in rules)
            self.assertTrue(workstation_rule, "Workstation endpoint should be registered")

    def test_profiles_endpoint_exists(self):
        """Test that profiles endpoint exists"""
        with self.app.test_request_context():
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            profiles_rule = any('gpu/profiles' in rule for rule in rules)
            self.assertTrue(profiles_rule, "Profiles endpoint should be registered")

    def test_clone_displays_endpoint_exists(self):
        """Test that clone displays endpoint exists"""
        with self.app.test_request_context():
            rules = [str(rule) for rule in self.app.url_map.iter_rules()]
            clone_rule = any('gpu/clone-displays' in rule for rule in rules)
            self.assertTrue(clone_rule, "Clone displays endpoint should be registered")

    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')

    def test_gpu_status_requires_auth(self):
        """Test that GPU status requires authentication"""
        response = self.client.get('/api/gpu/status')
        # Should return 401 Unauthorized due to missing JWT token
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main(verbosity=2)
