#!/usr/bin/env python3

import sys
import os
import json
import subprocess
import time
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def log_message(message, status="INFO"):
    """Log messages with timestamps"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{status}] {message}")

class FlaskAPITester:
    """Comprehensive API tester for NVIDIA Control Panel Flask application"""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.auth_header = {'Authorization': 'Bearer test-token-123'}
        self.session = requests.Session()
        self.session.headers.update(self.auth_header)

    def test_endpoint(self, method, endpoint, data=None, expected_status=200):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                return {'success': False, 'error': f'Unsupported method: {method}'}

            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': response.status_code == expected_status,
                'response_time': response.elapsed.total_seconds() * 1000,  # ms
                'content_length': len(response.content)
            }

            if response.status_code == 200:
                try:
                    result['data'] = response.json()
                except:
                    result['data'] = response.text[:200]  # First 200 chars
            else:
                result['error'] = response.text[:200]

            return result

        except requests.exceptions.RequestException as e:
            return {
                'endpoint': endpoint,
                'method': method,
                'success': False,
                'error': str(e),
                'expected_status': expected_status
            }

    def test_authentication(self):
        """Test authentication requirements"""
        log_message("Testing authentication...")

        # Test without auth header
        url = f"{self.base_url}/api/gpu/status"
        response = requests.get(url)  # No auth header

        if response.status_code == 401:
            log_message("✅ Authentication properly enforced")
            return True
        else:
            log_message("❌ Authentication not properly enforced", "ERROR")
            return False

    def test_all_endpoints(self):
        """Test all API endpoints comprehensively"""
        log_message("Starting comprehensive API endpoint testing...")

        endpoints = [
            # GET endpoints
            ('GET', '/api/gpu/status'),
            ('GET', '/api/gpu/physx'),
            ('GET', '/api/gpu/performance'),
            ('GET', '/api/gpu/frame-sync'),
            ('GET', '/api/gpu/sdi-output'),
            ('GET', '/api/gpu/edid'),
            ('GET', '/api/gpu/workstation'),
            ('GET', '/api/gpu/profiles'),
            ('GET', '/health'),
            ('GET', '/api/docs'),

            # POST endpoints with valid data
            ('POST', '/api/gpu/physx', {'processor': 'gpu'}),
            ('POST', '/api/gpu/frame-sync', {'mode': 'gsync'}),
            ('POST', '/api/gpu/sdi-output', {'enabled': True, 'format': 'HD'}),
            ('POST', '/api/gpu/edid', {'action': 'apply'}),
            ('POST', '/api/gpu/workstation', {'feature': 'rtx_features', 'enabled': True}),
            ('POST', '/api/gpu/profiles', {'action': 'apply', 'profile_id': 'gaming'}),
            ('POST', '/api/gpu/clone-displays', {'source_display': 'Display 1', 'target_displays': ['Display 2']}),

            # POST endpoints with invalid data (error cases)
            ('POST', '/api/gpu/physx', {'processor': 'invalid'}),
            ('POST', '/api/gpu/frame-sync', {'mode': 'invalid'}),
            ('POST', '/api/gpu/sdi-output', {'format': 'invalid'}),
            ('POST', '/api/gpu/edid', {'action': 'invalid'}),
            ('POST', '/api/gpu/profiles', {'action': 'invalid'}),
        ]

        results = []
        success_count = 0
        total_count = len(endpoints)

        for method, endpoint, *data in endpoints:
            test_data = data[0] if data else None
            log_message(f"Testing {method} {endpoint}...")

            result = self.test_endpoint(method, endpoint, test_data)
            results.append(result)

            if result['success']:
                success_count += 1
                log_message(f"✅ {method} {endpoint} - {result['status_code']} ({result['response_time']:.1f}ms)")
            else:
                log_message(f"❌ {method} {endpoint} - {result.get('status_code', 'ERROR')}: {result.get('error', 'Unknown error')}", "ERROR")

        log_message(f"API Testing Summary: {success_count}/{total_count} endpoints passed")
        return results, success_count, total_count

    def test_performance_load(self, num_requests=50, concurrent_users=5):
        """Test performance under load"""
        log_message(f"Testing performance with {num_requests} requests, {concurrent_users} concurrent users...")

        def make_request():
            return self.test_endpoint('GET', '/api/gpu/status')

        start_time = time.time()
        response_times = []

        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            for future in as_completed(futures):
                result = future.result()
                if result['success']:
                    response_times.append(result['response_time'])

        end_time = time.time()
        total_time = end_time - start_time

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            success_rate = len(response_times) / num_requests * 100

            log_message(".1f")
            log_message(".1f")
            log_message(".1f")
            log_message(".1f")

            return {
                'total_requests': num_requests,
                'successful_requests': len(response_times),
                'success_rate': success_rate,
                'total_time': total_time,
                'avg_response_time': avg_response_time,
                'min_response_time': min_response_time,
                'max_response_time': max_response_time,
                'requests_per_second': num_requests / total_time
            }
        else:
            log_message("❌ No successful requests during performance test", "ERROR")
            return None

    def test_error_handling(self):
        """Test error handling scenarios"""
        log_message("Testing error handling...")

        error_tests = [
            ('GET', '/api/nonexistent'),
            ('POST', '/api/gpu/status', {'invalid': 'data'}),
            ('GET', '/api/gpu/status', None, 401),  # Test without auth
        ]

        results = []
        for test in error_tests:
            method, endpoint = test[0], test[1]
            data = test[2] if len(test) > 2 else None
            expected_status = test[3] if len(test) > 3 else 404

            log_message(f"Testing error case: {method} {endpoint}")
            result = self.test_endpoint(method, endpoint, data, expected_status)
            results.append(result)

            if result['success']:
                log_message(f"✅ Error handling correct for {method} {endpoint}")
            else:
                log_message(f"❌ Error handling failed for {method} {endpoint}", "ERROR")

        return results

def start_flask_app():
    """Start the Flask application in a separate process"""
    log_message("Starting Flask application...")

    try:
        process = subprocess.Popen(
            [sys.executable, 'app_simple.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )

        # Wait for the app to start
        time.sleep(5)

        # Check if process is still running
        if process.poll() is None:
            log_message("✅ Flask application started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            log_message(f"❌ Flask app failed to start", "ERROR")
            log_message(f"STDOUT: {stdout.decode()}", "ERROR")
            log_message(f"STDERR: {stderr.decode()}", "ERROR")
            return None

    except Exception as e:
        log_message(f"❌ Error starting Flask app: {e}", "ERROR")
        return None

def main():
    """Main test execution function"""
    log_message("=== Comprehensive NVIDIA Control Panel API Test Suite ===")

    # Start Flask app
    flask_process = start_flask_app()
    if not flask_process:
        log_message("❌ Cannot proceed without Flask app running", "ERROR")
        return False

    try:
        # Initialize API tester
        tester = FlaskAPITester()

        # Test authentication
        auth_success = tester.test_authentication()

        # Test all endpoints
        endpoint_results, success_count, total_count = tester.test_all_endpoints()

        # Test error handling
        error_results = tester.test_error_handling()

        # Test performance under load
        performance_results = tester.test_performance_load(num_requests=30, concurrent_users=3)

        # Generate comprehensive test report
        test_report = {
            'timestamp': datetime.now().isoformat(),
            'authentication_test': auth_success,
            'endpoint_tests': {
                'total': total_count,
                'successful': success_count,
                'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
                'results': endpoint_results
            },
            'error_handling_tests': error_results,
            'performance_test': performance_results,
            'overall_success': auth_success and (success_count >= total_count * 0.8)  # 80% success rate
        }

        # Save detailed test report
        with open('comprehensive_api_test_results.json', 'w') as f:
            json.dump(test_report, f, indent=2, default=str)

        log_message("✅ Comprehensive test results saved to comprehensive_api_test_results.json")

        # Summary
        if test_report['overall_success']:
            log_message("🎉 All tests completed successfully!", "SUCCESS")
        else:
            log_message("⚠️ Some tests failed. Check the detailed report.", "WARNING")

        return test_report['overall_success']

    finally:
        # Clean up Flask process
        if flask_process and flask_process.poll() is None:
            log_message("Stopping Flask application...")
            flask_process.terminate()
            flask_process.wait()
            log_message("✅ Flask application stopped")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
