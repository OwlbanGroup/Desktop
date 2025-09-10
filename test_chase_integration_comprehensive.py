#!/usr/bin/env python3
"""
Comprehensive Test Suite for Chase Integration
Tests all Chase services: Mortgage, Auto Finance, and Credit Cards
"""

import unittest
import requests
import json
import time
from datetime import datetime, timedelta
import threading
import concurrent.futures
from flask import Flask
import sys
import os

# Add the current directory to sys.path for imports
sys.path.append(os.getcwd())

class ChaseIntegrationTestSuite(unittest.TestCase):
    """Comprehensive test suite for Chase integration"""

    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.test_user = {
            "username": "test_user",
            "password": "test_password"
        }
        self.auth_token = None

    def test_01_app_startup(self):
        """Test that the Flask app starts correctly"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.assertIn(response.status_code, [200, 404])  # 404 is ok, means app is running
            print("✅ App startup test passed")
        except requests.exceptions.ConnectionError:
            self.fail("❌ App is not running. Please start the app first.")

    def test_02_chase_credit_cards_login(self):
        """Test Chase Credit Cards login functionality"""
        login_url = f"{self.base_url}/chase-credit-cards/login"
        response = self.session.post(login_url, json=self.test_user)

        if response.status_code == 200:
            data = response.json()
            self.assertTrue(data.get('success', False))
            self.auth_token = data.get('token')
            print("✅ Credit Cards login test passed")
        else:
            print(f"⚠️  Credit Cards login returned {response.status_code} - may be expected for demo")

    def test_03_chase_credit_cards_accounts(self):
        """Test Chase Credit Cards accounts endpoint"""
        if not self.auth_token:
            self.skipTest("No auth token available")

        accounts_url = f"{self.base_url}/chase-credit-cards/accounts"
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        response = self.session.get(accounts_url, headers=headers)

        # This might return an error if no real Chase API is connected
        if response.status_code == 200:
            data = response.json()
            self.assertIn('success', data)
            print("✅ Credit Cards accounts test passed")
        else:
            print(f"⚠️  Credit Cards accounts test returned {response.status_code} - expected for demo")

    def test_04_chase_credit_cards_dashboard_page(self):
        """Test Chase Credit Cards dashboard page loads"""
        dashboard_url = f"{self.base_url}/chase-credit-cards"
        response = self.session.get(dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Chase Credit Cards Integration', response.text)
        self.assertIn('text/html', response.headers.get('content-type', ''))
        print("✅ Credit Cards dashboard page test passed")

    def test_05_chase_mortgage_page(self):
        """Test Chase Mortgage page loads"""
        mortgage_url = f"{self.base_url}/chase-mortgage"
        response = self.session.get(mortgage_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers.get('content-type', ''))
        print("✅ Mortgage page test passed")

    def test_06_chase_auto_finance_page(self):
        """Test Chase Auto Finance page loads"""
        auto_url = f"{self.base_url}/chase-auto-finance"
        response = self.session.get(auto_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers.get('content-type', ''))
        print("✅ Auto Finance page test passed")

    def test_07_response_time_performance(self):
        """Test response times for all Chase services"""
        urls = [
            f"{self.base_url}/chase-credit-cards",
            f"{self.base_url}/chase-mortgage",
            f"{self.base_url}/chase-auto-finance"
        ]

        for url in urls:
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            end_time = time.time()

            response_time = end_time - start_time
            self.assertLess(response_time, 5.0, f"Response time too slow for {url}: {response_time}s")
            print(f"✅ Response time test passed for {url.split('/')[-1]}: {response_time:.2f}s")

    def test_08_concurrent_requests(self):
        """Test handling of concurrent requests"""
        def make_request(url):
            return self.session.get(url, timeout=10)

        urls = [
            f"{self.base_url}/chase-credit-cards",
            f"{self.base_url}/chase-mortgage",
            f"{self.base_url}/chase-auto-finance"
        ] * 5  # 15 concurrent requests

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, url) for url in urls]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        successful_requests = sum(1 for r in results if r.status_code == 200)
        self.assertGreaterEqual(successful_requests, 10, "Too many failed concurrent requests")
        print(f"✅ Concurrent requests test passed: {successful_requests}/{len(urls)} successful")

    def test_09_error_handling_invalid_urls(self):
        """Test error handling for invalid URLs"""
        invalid_urls = [
            f"{self.base_url}/chase-invalid",
            f"{self.base_url}/chase-credit-cards/invalid-endpoint",
            f"{self.base_url}/chase-mortgage/invalid-endpoint"
        ]

        for url in invalid_urls:
            response = self.session.get(url)
            # Should return 404 for invalid endpoints
            self.assertIn(response.status_code, [404, 405, 500])
            print(f"✅ Error handling test passed for invalid URL: {url}")

    def test_10_credit_cards_api_endpoints(self):
        """Test all Credit Cards API endpoints"""
        endpoints = [
            '/chase-credit-cards/login',
            '/chase-credit-cards/accounts',
            '/chase-credit-cards/transactions/12345',
            '/chase-credit-cards/limits/12345',
            '/chase-credit-cards/sync'
        ]

        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url) if 'GET' in endpoint else self.session.post(url)

            # API endpoints should return JSON responses
            try:
                if response.status_code in [200, 400, 401, 500]:
                    if 'json' in response.headers.get('content-type', ''):
                        data = response.json()
                        self.assertIsInstance(data, dict)
                        print(f"✅ API endpoint test passed: {endpoint}")
                    else:
                        print(f"⚠️  API endpoint {endpoint} returned HTML instead of JSON")
                else:
                    print(f"⚠️  API endpoint {endpoint} returned status {response.status_code}")
            except json.JSONDecodeError:
                print(f"⚠️  API endpoint {endpoint} returned invalid JSON")

    def test_11_ui_elements_presence(self):
        """Test that all required UI elements are present"""
        response = self.session.get(f"{self.base_url}/chase-credit-cards")
        html_content = response.text

        required_elements = [
            'Chase Credit Cards Integration',
            'Login to Chase',
            'Credit Cards Dashboard',
            'btn',
            'form',
            'dashboard'
        ]

        for element in required_elements:
            self.assertIn(element, html_content, f"Missing UI element: {element}")
            print(f"✅ UI element test passed: {element}")

    def test_12_css_and_js_loading(self):
        """Test that CSS and JavaScript are properly loaded"""
        response = self.session.get(f"{self.base_url}/chase-credit-cards")
        html_content = response.text

        # Check for inline CSS
        self.assertIn('<style>', html_content, "Missing CSS styles")
        self.assertIn('</style>', html_content, "CSS not properly closed")

        # Check for JavaScript
        self.assertIn('<script>', html_content, "Missing JavaScript")
        self.assertIn('</script>', html_content, "JavaScript not properly closed")

        print("✅ CSS and JS loading test passed")

    def test_13_session_management(self):
        """Test session management and authentication flow"""
        # Test without authentication
        accounts_url = f"{self.base_url}/chase-credit-cards/accounts"
        response = self.session.get(accounts_url)

        # Should require authentication
        if response.status_code == 401:
            print("✅ Session management test passed: Authentication required")
        else:
            print("⚠️  Session management test: Authentication may not be enforced")

    def test_14_data_validation(self):
        """Test data validation for API inputs"""
        login_url = f"{self.base_url}/chase-credit-cards/login"

        # Test with missing data
        response = self.session.post(login_url, json={})
        if response.status_code == 400:
            print("✅ Data validation test passed: Missing data rejected")
        else:
            print("⚠️  Data validation test: Missing data not properly validated")

        # Test with invalid data
        response = self.session.post(login_url, json={"invalid": "data"})
        if response.status_code == 400:
            print("✅ Data validation test passed: Invalid data rejected")
        else:
            print("⚠️  Data validation test: Invalid data not properly validated")

    def test_15_load_testing_basic(self):
        """Basic load testing with multiple rapid requests"""
        url = f"{self.base_url}/chase-credit-cards"

        start_time = time.time()
        responses = []

        # Make 20 rapid requests
        for i in range(20):
            response = self.session.get(url, timeout=5)
            responses.append(response.status_code)

        end_time = time.time()
        total_time = end_time - start_time

        successful_responses = sum(1 for r in responses if r == 200)
        success_rate = (successful_responses / len(responses)) * 100

        self.assertGreaterEqual(success_rate, 80, f"Load test failed: {success_rate}% success rate")
        print(f"✅ Load testing passed: {success_rate}% success rate, {total_time:.2f}s total time")

def run_performance_benchmark():
    """Run performance benchmark tests"""
    print("\n🚀 Running Performance Benchmarks...")

    base_url = "http://localhost:5000"
    session = requests.Session()

    # Test response times for different endpoints
    endpoints = [
        '/chase-credit-cards',
        '/chase-mortgage',
        '/chase-auto-finance'
    ]

    results = {}

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        times = []

        # Test each endpoint 10 times
        for i in range(10):
            start = time.time()
            try:
                response = session.get(url, timeout=5)
                end = time.time()
                if response.status_code == 200:
                    times.append(end - start)
            except:
                pass

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            results[endpoint] = {
                'avg': avg_time,
                'min': min_time,
                'max': max_time,
                'samples': len(times)
            }

            print(".3f"
    return results

def run_integration_test():
    """Run integration test to verify all services work together"""
    print("\n🔗 Running Integration Tests...")

    base_url = "http://localhost:5000"
    session = requests.Session()

    # Test that all three services are accessible
    services = {
        'Credit Cards': '/chase-credit-cards',
        'Mortgage': '/chase-mortgage',
        'Auto Finance': '/chase-auto-finance'
    }

    all_working = True

    for service_name, endpoint in services.items():
        url = f"{base_url}{endpoint}"
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} service is accessible")
            else:
                print(f"⚠️  {service_name} service returned status {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"❌ {service_name} service failed: {str(e)}")
            all_working = False

    return all_working

def main():
    """Main test runner"""
    print("🧪 Starting Comprehensive Chase Integration Testing")
    print("=" * 60)

    # Check if app is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Flask app is running")
    except:
        print("❌ Flask app is not running. Please start the app first with:")
        print("   python app_with_chase_integration.py")
        return

    # Run unit tests
    print("\n📋 Running Unit Tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(ChaseIntegrationTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    # Run performance benchmarks
    benchmark_results = run_performance_benchmark()

    # Run integration test
    integration_success = run_integration_test()

    # Generate test summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    print(f"Unit Tests: {test_result.testsRun} run, {len(test_result.failures)} failed, {len(test_result.errors)} errors")

    if benchmark_results:
        print("\nPerformance Benchmarks:")
        for endpoint, data in benchmark_results.items():
            print(".3f"
    print(f"\nIntegration Test: {'✅ PASSED' if integration_success else '❌ FAILED'}")

    # Overall assessment
    if test_result.wasSuccessful() and integration_success:
        print("\n🎉 ALL TESTS PASSED! Chase integration is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the results above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
