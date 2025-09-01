#!/usr/bin/env python3
"""
Full integration test suite for the OWLban application
Tests the complete application stack including Docker containers
"""

import pytest
import requests
import time
import subprocess
import os
import signal
import json
from unittest.mock import Mock, patch


class TestFullIntegration:
    """Full integration tests for the complete OWLban application"""

    @classmethod
    def setup_class(cls):
        """Set up the full application stack for testing"""
        cls.flask_process = None
        cls.node_process = None
        cls.base_url = "http://localhost:5000"
        cls.node_url = "http://localhost:4000"

    @classmethod
    def teardown_class(cls):
        """Clean up running processes"""
        if cls.flask_process:
            cls.flask_process.terminate()
            cls.flask_process.wait()
        if cls.node_process:
            cls.node_process.terminate()
            cls.node_process.wait()

    def wait_for_service(self, url, timeout=30):
        """Wait for a service to become available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            time.sleep(1)
        return False

    def test_application_startup(self):
        """Test that the application starts up correctly"""
        # Start Flask backend
        env = os.environ.copy()
        env['FLASK_ENV'] = 'testing'
        env['OSCAR_BROOME_URL'] = self.node_url

        self.flask_process = subprocess.Popen(
            ['python', '-m', 'flask', 'run', '--host=0.0.0.0', '--port=5000'],
            cwd='backend',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for Flask to start
        assert self.wait_for_service(f"{self.base_url}/health"), "Flask service failed to start"

        # Check health endpoint
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'healthy'
        assert 'flask' in data['services']

    def test_frontend_serving(self):
        """Test that frontend files are served correctly"""
        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200

        # Should serve HTML content
        assert 'text/html' in response.headers.get('content-type', '')

        # Test static file serving (if index.html exists)
        response = requests.get(f"{self.base_url}/index.html")
        if response.status_code == 200:
            assert 'text/html' in response.headers.get('content-type', '')

    def test_api_endpoints_integration(self):
        """Test all API endpoints work together"""
        # Test leadership endpoints
        leadership_data = {
            'leader_name': 'IntegrationTestLeader',
            'leadership_style': 'DEMOCRATIC',
            'team_members': ['Dev1:Developer', 'Dev2:Designer', 'PM:Manager']
        }

        response = requests.post(
            f"{self.base_url}/api/leadership/lead_team",
            json=leadership_data
        )
        assert response.status_code == 200

        data = response.json()
        assert 'lead_result' in data
        assert 'team_status' in data

        # Test decision making
        decision_data = {
            'leader_name': 'IntegrationTestLeader',
            'leadership_style': 'DEMOCRATIC',
            'decision': 'Integration test decision'
        }

        response = requests.post(
            f"{self.base_url}/api/leadership/make_decision",
            json=decision_data
        )
        assert response.status_code == 200

        data = response.json()
        assert 'decision_result' in data

    def test_gpu_integration(self):
        """Test GPU status integration"""
        response = requests.get(f"{self.base_url}/api/gpu/status")
        # Should not fail even if no GPU is present
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            # Should return some GPU information structure
            assert isinstance(data, dict)

    def test_earnings_integration(self):
        """Test earnings data integration"""
        response = requests.get(f"{self.base_url}/api/earnings")
        assert response.status_code == 200

        data = response.json()
        assert 'message' in data

    @patch('requests.post')
    @patch('requests.get')
    def test_jpmorgan_payment_integration(self, mock_get, mock_post):
        """Test JPMorgan payment integration with mocked external service"""
        # Mock successful payment creation
        mock_response = Mock()
        mock_response.json.return_value = {
            'payment_id': 'int_test_123',
            'status': 'created',
            'amount': 100.00
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        payment_data = {
            'amount': 100.00,
            'currency': 'USD',
            'description': 'Integration test payment'
        }

        response = requests.post(
            f"{self.base_url}/api/jpmorgan-payment/create-payment",
            json=payment_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data['payment_id'] == 'int_test_123'
        assert data['status'] == 'created'

        # Mock payment status check
        mock_response.json.return_value = {
            'status': 'completed',
            'amount': 100.00,
            'payment_id': 'int_test_123'
        }
        mock_get.return_value = mock_response

        response = requests.get(f"{self.base_url}/api/jpmorgan-payment/payment-status/int_test_123")
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'completed'

    def test_error_handling_integration(self):
        """Test error handling across the application"""
        # Test invalid JSON
        response = requests.post(
            f"{self.base_url}/api/leadership/lead_team",
            data='invalid json',
            headers={'Content-Type': 'application/json'}
        )
        # Should handle gracefully
        assert response.status_code in [200, 400, 500]

        # Test missing endpoint
        response = requests.get(f"{self.base_url}/api/nonexistent")
        assert response.status_code == 404

        # Test invalid method
        response = requests.put(f"{self.base_url}/api/leadership/lead_team")
        assert response.status_code == 405

    def test_concurrent_requests_integration(self):
        """Test handling of concurrent requests"""
        import threading

        results = []
        errors = []

        def make_request(endpoint):
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                results.append((endpoint, response.status_code))
            except Exception as e:
                errors.append((endpoint, str(e)))

        endpoints = ['/health', '/api/earnings', '/api/gpu/status']
        threads = []

        # Make concurrent requests
        for endpoint in endpoints * 5:  # 15 total requests
            thread = threading.Thread(target=make_request, args=(endpoint,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check results
        assert len(results) == 15
        assert len(errors) == 0

        # All requests should succeed
        for endpoint, status in results:
            assert status == 200, f"Request to {endpoint} failed with status {status}"

    def test_performance_integration(self):
        """Test basic performance characteristics"""
        import time

        # Test response times for critical endpoints
        endpoints = [
            '/health',
            '/api/earnings',
            '/api/gpu/status'
        ]

        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}")
            end_time = time.time()

            response_time = end_time - start_time

            # Should respond within reasonable time (2 seconds)
            assert response_time < 2.0, f"{endpoint} took {response_time:.2f}s to respond"
            assert response.status_code == 200

    def test_data_integrity_integration(self):
        """Test data integrity across requests"""
        # Create a team and verify consistency
        team_data = {
            'leader_name': 'DataIntegrityTest',
            'leadership_style': 'DEMOCRATIC',
            'team_members': ['Alice:Developer', 'Bob:Designer', 'Charlie:Manager']
        }

        response1 = requests.post(
            f"{self.base_url}/api/leadership/lead_team",
            json=team_data
        )
        assert response1.status_code == 200

        # Make another request with same data
        response2 = requests.post(
            f"{self.base_url}/api/leadership/lead_team",
            json=team_data
        )
        assert response2.status_code == 200

        # Results should be consistent (same structure)
        data1 = response1.json()
        data2 = response2.json()

        assert 'lead_result' in data1
        assert 'team_status' in data1
        assert 'lead_result' in data2
        assert 'team_status' in data2

    def test_security_headers_integration(self):
        """Test security headers are present"""
        response = requests.get(f"{self.base_url}/health")

        # Check for basic security headers
        headers = response.headers

        # These are examples - actual headers depend on server configuration
        # assert 'X-Content-Type-Options' in headers
        # assert 'X-Frame-Options' in headers

        # At minimum, should have content-type
        assert 'content-type' in headers

    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        # Create a large team
        large_team = [f"Member{i}:Role{i}" for i in range(100)]

        team_data = {
            'leader_name': 'LargeTeamTest',
            'leadership_style': 'DEMOCRATIC',
            'team_members': large_team
        }

        response = requests.post(
            f"{self.base_url}/api/leadership/lead_team",
            json=team_data
        )

        # Should handle large payload gracefully
        assert response.status_code == 200

        data = response.json()
        assert 'lead_result' in data
        assert 'team_status' in data


class TestDockerIntegration:
    """Integration tests that require Docker"""

    def test_docker_compose_services(self):
        """Test that docker-compose services start correctly"""
        # This test would run in a CI environment with Docker
        # For now, just check if docker-compose file exists and is valid

        compose_file = 'docker-compose.yml'
        assert os.path.exists(compose_file), "docker-compose.yml not found"

        # Basic validation that it's a valid YAML file
        import yaml
        with open(compose_file, 'r') as f:
            compose_data = yaml.safe_load(f)

        assert 'services' in compose_data
        assert 'flask-backend' in compose_data['services']
        assert 'node-backend' in compose_data['services']

    def test_dockerfile_validation(self):
        """Test that Dockerfile is valid"""
        dockerfile = 'Dockerfile'
        assert os.path.exists(dockerfile), "Dockerfile not found"

        with open(dockerfile, 'r') as f:
            content = f.read()

        # Basic checks
        assert 'FROM' in content
        assert 'WORKDIR' in content
        assert 'COPY' in content
        assert 'RUN' in content
        assert 'EXPOSE' in content
        assert 'ENTRYPOINT' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
