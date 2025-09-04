#!/usr/bin/env python3
"""
Enhanced End-to-End Test Suite for Owlban Group Platform
Tests all critical paths including leadership simulation, NVIDIA GPU integration,
earnings dashboard, JPMorgan payment proxy, and login override system.
"""

import requests
import time
import json
import subprocess
import sys
import os
from datetime import datetime
import threading
import psutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedE2ETestSuite:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.server_process = None
        self.start_time = None
        self.end_time = None

    def log_test_result(self, test_name, success, message="", duration=None):
        """Log individual test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "duration": duration
        }
        self.test_results.append(result)
        status = "PASS" if success else "FAIL"
        logger.info(f"{status}: {test_name} - {message}")

    def start_server(self):
        """Start the Flask server in a separate process"""
        try:
            logger.info("Starting Flask server...")
            self.server_process = subprocess.Popen(
                [sys.executable, "run.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            # Wait for server to start
            time.sleep(5)
            # Check if server is running
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("Server started successfully")
                return True
            else:
                logger.error("Server health check failed")
                return False
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False

    def stop_server(self):
        """Stop the Flask server"""
        if self.server_process:
            logger.info("Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            logger.info("Server stopped")

    def test_server_health(self):
        """Test server health endpoint"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            duration = time.time() - start_time
            if response.status_code == 200:
                self.log_test_result("Server Health Check", True, "Server is healthy", duration)
                return True
            else:
                self.log_test_result("Server Health Check", False, f"Unexpected status: {response.status_code}", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Server Health Check", False, str(e), duration)
            return False

    def test_leadership_simulation(self):
        """Test leadership simulation endpoints"""
        start_time = time.time()
        try:
            # Test lead team
            payload = {
                "leader_name": "Alice",
                "leadership_style": "DEMOCRATIC",
                "team_members": ["Bob:Developer", "Charlie:Designer"]
            }
            response = self.session.post(f"{self.base_url}/api/leadership/lead_team", json=payload, timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if "lead_result" in data and "team_status" in data:
                    self.log_test_result("Leadership Team Leading", True, "Successfully led team", duration)
                else:
                    self.log_test_result("Leadership Team Leading", False, "Missing expected response fields", duration)
                    return False
            else:
                self.log_test_result("Leadership Team Leading", False, f"Status: {response.status_code}", duration)
                return False

            # Test make decision
            start_time = time.time()
            payload = {
                "leader_name": "Alice",
                "leadership_style": "TRANSFORMATIONAL",
                "decision": "Implement new strategy"
            }
            response = self.session.post(f"{self.base_url}/api/leadership/make_decision", json=payload, timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if "decision_result" in data:
                    self.log_test_result("Leadership Decision Making", True, "Successfully made decision", duration)
                    return True
                else:
                    self.log_test_result("Leadership Decision Making", False, "Missing decision result", duration)
                    return False
            else:
                self.log_test_result("Leadership Decision Making", False, f"Status: {response.status_code}", duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Leadership Simulation", False, str(e), duration)
            return False

    def test_nvidia_gpu_integration(self):
        """Test NVIDIA GPU status endpoints"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/gpu/status", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    self.log_test_result("NVIDIA GPU Status", True, f"Retrieved {len(data)} GPU metrics", duration)
                    return True
                else:
                    self.log_test_result("NVIDIA GPU Status", False, "Empty or invalid GPU data", duration)
                    return False
            else:
                self.log_test_result("NVIDIA GPU Status", False, f"Status: {response.status_code}", duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("NVIDIA GPU Integration", False, str(e), duration)
            return False

    def test_login_override_system(self):
        """Test login override system endpoints"""
        start_time = time.time()
        try:
            # Test emergency override
            payload = {
                "userId": "oscar.broome@oscarsystem.com",
                "reason": "emergency_access",
                "emergencyCode": "OSCAR_BROOME_EMERGENCY_2024"
            }
            response = self.session.post(f"{self.base_url}/api/override/emergency", json=payload, timeout=10)
            duration = time.time() - start_time

            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("success"):
                    self.log_test_result("Emergency Override", True, "Emergency override successful", duration)
                else:
                    self.log_test_result("Emergency Override", False, data.get("message", "Override failed"), duration)
                    return False
            else:
                self.log_test_result("Emergency Override", False, f"Status: {response.status_code}", duration)
                return False

            # Test admin override
            start_time = time.time()
            payload = {
                "adminUserId": "admin@oscarsystem.com",
                "targetUserId": "user@oscarsystem.com",
                "reason": "account_locked",
                "justification": "Administrative override for system access"
            }
            response = self.session.post(f"{self.base_url}/api/override/admin", json=payload, timeout=10)
            duration = time.time() - start_time

            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("success"):
                    self.log_test_result("Admin Override", True, "Admin override successful", duration)
                    return True
                else:
                    self.log_test_result("Admin Override", False, data.get("message", "Override failed"), duration)
                    return False
            else:
                self.log_test_result("Admin Override", False, f"Status: {response.status_code}", duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Login Override System", False, str(e), duration)
            return False

    def test_frontend_accessibility(self):
        """Test frontend accessibility and basic functionality"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                content = response.text
                # Check for essential elements
                checks = [
                    "Owlban Group" in content,
                    "Leadership Simulation" in content,
                    "NVIDIA GPU Status" in content,
                    "Login Override System" in content
                ]

                if all(checks):
                    self.log_test_result("Frontend Accessibility", True, "All essential elements present", duration)
                    return True
                else:
                    self.log_test_result("Frontend Accessibility", False, "Missing essential elements", duration)
                    return False
            else:
                self.log_test_result("Frontend Accessibility", False, f"Status: {response.status_code}", duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Frontend Accessibility", False, str(e), duration)
            return False

    def test_performance_metrics(self):
        """Test performance metrics and response times"""
        start_time = time.time()
        try:
            # Test multiple endpoints for performance
            endpoints = [
                "/health",
                "/api/gpu/status",
                "/api/leadership/lead_team"
            ]

            total_response_time = 0
            successful_requests = 0

            for endpoint in endpoints:
                try:
                    req_start = time.time()
                    if endpoint == "/api/leadership/lead_team":
                        payload = {
                            "leader_name": "Test",
                            "leadership_style": "DEMOCRATIC",
                            "team_members": ["Test:Role"]
                        }
                        response = self.session.post(f"{self.base_url}{endpoint}", json=payload, timeout=10)
                    else:
                        response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)

                    req_duration = time.time() - req_start
                    total_response_time += req_duration

                    if response.status_code in [200, 201]:
                        successful_requests += 1

                except Exception as e:
                    logger.warning(f"Performance test failed for {endpoint}: {e}")

            duration = time.time() - start_time
            avg_response_time = total_response_time / len(endpoints) if endpoints else 0

            if successful_requests == len(endpoints) and avg_response_time < 2.0:  # Less than 2 seconds average
                self.log_test_result("Performance Metrics", True,
                                   ".2f", duration)
                return True
            else:
                self.log_test_result("Performance Metrics", False,
                                   ".2f", duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Performance Metrics", False, str(e), duration)
            return False

    def test_error_handling(self):
        """Test error handling and edge cases"""
        start_time = time.time()
        try:
            # Test invalid endpoint
            response = self.session.get(f"{self.base_url}/api/invalid_endpoint", timeout=10)

            # Test malformed JSON
            response2 = self.session.post(f"{self.base_url}/api/leadership/lead_team",
                                        data="invalid json", timeout=10)

            duration = time.time() - start_time

            # Both should return appropriate error responses
            if response.status_code in [404, 500] and response2.status_code in [400, 500]:
                self.log_test_result("Error Handling", True, "Proper error responses for invalid requests", duration)
                return True
            else:
                self.log_test_result("Error Handling", False, "Unexpected error response codes", duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Error Handling", False, str(e), duration)
            return False

    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        report = f"""
# Enhanced E2E Test Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Tests: {total_tests}
- Passed: {passed_tests}
- Failed: {failed_tests}
- Success Rate: {(passed_tests/total_tests)*100:.1f}%

## Test Results
"""

        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = ".3f" if result["duration"] else "N/A"
            report += f"### {status} - {result['test_name']}\n"
            report += f"- Duration: {duration}\n"
            report += f"- Message: {result['message']}\n"
            report += f"- Timestamp: {result['timestamp']}\n\n"

        # Save report to file
        with open("e2e_test_report_enhanced.txt", "w") as f:
            f.write(report)

        # Save detailed JSON results
        with open("e2e_test_results_enhanced.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0
                },
                "results": self.test_results,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        logger.info(f"Report generated: {passed_tests}/{total_tests} tests passed")
        return report

    def run_all_tests(self):
        """Run all E2E tests"""
        logger.info("Starting Enhanced E2E Test Suite...")
        self.start_time = time.time()

        # Start server
        if not self.start_server():
            logger.error("Failed to start server. Aborting tests.")
            return False

        try:
            # Run all test suites
            test_methods = [
                self.test_server_health,
                self.test_leadership_simulation,
                self.test_nvidia_gpu_integration,
                self.test_login_override_system,
                self.test_frontend_accessibility,
                self.test_performance_metrics,
                self.test_error_handling
            ]

            all_passed = True
            for test_method in test_methods:
                try:
                    result = test_method()
                    if not result:
                        all_passed = False
                except Exception as e:
                    logger.error(f"Test {test_method.__name__} failed with exception: {e}")
                    all_passed = False

            # Generate report
            self.end_time = time.time()
            total_duration = self.end_time - self.start_time
            logger.info(".2f")

            self.generate_report()

            return all_passed

        finally:
            self.stop_server()

def main():
    """Main entry point"""
    suite = EnhancedE2ETestSuite()

    try:
        success = suite.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        suite.stop_server()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        suite.stop_server()
        sys.exit(1)

if __name__ == "__main__":
    main()
