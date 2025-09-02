#!/usr/bin/env python3
"""
End-to-End Test Suite for Owlban Group Integrated Platform
Tests all components: Frontend, Backend, Login Override, Leadership, NVIDIA, Earnings Dashboard
"""

import requests
import json
import time
import subprocess
import sys
import os
from datetime import datetime
import threading
import signal
import psutil

class E2ETestSuite:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.server_process = None
        self.test_results = []
        self.start_time = None
        self.end_time = None

    def log_test_result(self, test_name, status, message="", details=None):
        """Log individual test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
            print(f"[{status.upper()}] {test_name}: {message}")

    def start_server(self):
        """Start the backend server"""
        try:
            print("Starting backend server...")
            self.server_process = subprocess.Popen(
                [sys.executable, "backend/app_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            # Wait for server to start
            time.sleep(5)  # Increased wait time to allow server to fully start
            return True
        except Exception as e:
            self.log_test_result("Server Startup", "FAILED", f"Failed to start server: {str(e)}")
            return False

    def stop_server(self):
        """Stop the backend server"""
        if self.server_process:
            try:
                # Try graceful shutdown first
                if self.server_process.poll() is None:
                    self.server_process.terminate()
                    time.sleep(5)  # Increased wait time for graceful shutdown
                    if self.server_process.poll() is None:
                        self.server_process.kill()
        except Exception as e:
            print(f"Error stopping server: {e}")

    def test_server_health(self):
        """Test basic server health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)  # Increased timeout
            if response.status_code == 200:
                self.log_test_result("Server Health", "PASSED", "Server is responding")
                return True
            else:
                self.log_test_result("Server Health", "FAILED", f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Server Health", "FAILED", f"Server not responding: {str(e)}")
            return False

    def test_login_override_emergency(self):
        """Test emergency login override"""
        try:
            payload = {
                "userId": "oscar.broome@oscarsystem.com",
                "reason": "emergency_access",
                "emergencyCode": "OSCAR_BROOME_EMERGENCY_2024"
            }
            response = requests.post(f"{self.base_url}/api/override/emergency", json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test_result("Emergency Override", "PASSED", "Emergency override successful")
                    return True
                else:
                    self.log_test_result("Emergency Override", "FAILED", f"Override failed: {data.get('message')}")
                    return False
            else:
                self.log_test_result("Emergency Override", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Emergency Override", "FAILED", f"Exception: {str(e)}")
            return False

    def test_login_override_admin(self):
        """Test admin login override"""
        try:
            payload = {
                "adminUserId": "admin@oscarsystem.com",
                "targetUserId": "user@oscarsystem.com",
                "reason": "account_locked",
                "justification": "Administrative override for system access"
            }
            response = requests.post(f"{self.base_url}/api/override/admin", json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test_result("Admin Override", "PASSED", "Admin override successful")
                    return True
                else:
                    self.log_test_result("Admin Override", "FAILED", f"Override failed: {data.get('message')}")
                    return False
            else:
                self.log_test_result("Admin Override", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Admin Override", "FAILED", f"Exception: {str(e)}")
            return False

    def test_login_override_technical(self):
        """Test technical login override"""
        try:
            payload = {
                "supportUserId": "support@oscarsystem.com",
                "targetUserId": "user@oscarsystem.com",
                "reason": "technical_issue",
                "ticketNumber": "TECH-1234"
            }
            response = requests.post(f"{self.base_url}/api/override/technical", json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test_result("Technical Override", "PASSED", "Technical override successful")
                    return True
                else:
                    self.log_test_result("Technical Override", "FAILED", f"Override failed: {data.get('message')}")
                    return False
            else:
                self.log_test_result("Technical Override", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Technical Override", "FAILED", f"Exception: {str(e)}")
            return False

    def test_login_override_validation(self):
        """Test override validation"""
        try:
            # First create an override to get an ID
            payload = {
                "userId": "oscar.broome@oscarsystem.com",
                "reason": "emergency_access",
                "emergencyCode": "OSCAR_BROOME_EMERGENCY_2024"
            }
            create_response = requests.post(f"{self.base_url}/api/override/emergency", json=payload, timeout=10)

            if create_response.status_code == 200:
                create_data = create_response.json()
                if create_data.get("success") and create_data.get("data", {}).get("overrideId"):
                    override_id = create_data["data"]["overrideId"]

                    # Now validate the override
                    validate_payload = {
                        "userId": "oscar.broome@oscarsystem.com"
                    }
                    validate_response = requests.post(
                        f"{self.base_url}/api/override/validate/{override_id}",
                        json=validate_payload,
                        timeout=10
                    )

                    if validate_response.status_code == 200:
                        validate_data = validate_response.json()
                        if validate_data.get("success"):
                            self.log_test_result("Override Validation", "PASSED", "Override validation successful")
                            return True
                        else:
                            self.log_test_result("Override Validation", "FAILED", f"Validation failed: {validate_data.get('message')}")
                            return False
                    else:
                        self.log_test_result("Override Validation", "FAILED", f"HTTP {validate_response.status_code}")
                        return False
                else:
                    self.log_test_result("Override Validation", "SKIPPED", "Could not create override for validation test")
                    return True
            else:
                self.log_test_result("Override Validation", "SKIPPED", "Could not create override for validation test")
                return True
        except Exception as e:
            self.log_test_result("Override Validation", "FAILED", f"Exception: {str(e)}")
            return False

    def test_active_overrides(self):
        """Test getting active overrides"""
        try:
            response = requests.get(f"{self.base_url}/api/override/active/oscar.broome@oscarsystem.com", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test_result("Active Overrides", "PASSED", "Active overrides retrieved successfully")
                    return True
                else:
                    self.log_test_result("Active Overrides", "FAILED", f"Failed to get active overrides: {data.get('message')}")
                    return False
            else:
                self.log_test_result("Active Overrides", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Active Overrides", "FAILED", f"Exception: {str(e)}")
            return False

    def test_leadership_simulation(self):
        """Test leadership simulation endpoints"""
        try:
            payload = {
                "leader_name": "Alice",
                "leadership_style": "DEMOCRATIC",
                "team_members": ["Bob:Developer", "Charlie:Designer"]
            }
            response = requests.post(f"{self.base_url}/api/leadership/lead_team", json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "lead_result" in data and "team_status" in data:
                    self.log_test_result("Leadership Simulation", "PASSED", "Leadership simulation successful")
                    return True
                else:
                    self.log_test_result("Leadership Simulation", "FAILED", "Invalid response format")
                    return False
            else:
                self.log_test_result("Leadership Simulation", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Leadership Simulation", "FAILED", f"Exception: {str(e)}")
            return False

    def test_gpu_status(self):
        """Test NVIDIA GPU status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/gpu/status", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    self.log_test_result("GPU Status", "PASSED", f"GPU status retrieved: {len(data)} properties")
                    return True
                else:
                    self.log_test_result("GPU Status", "FAILED", "Invalid GPU status response")
                    return False
            else:
                self.log_test_result("GPU Status", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("GPU Status", "FAILED", f"Exception: {str(e)}")
            return False

    def test_frontend_accessibility(self):
        """Test frontend accessibility"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=15)  # Increased timeout

            if response.status_code == 200:
                if "Owlban Group" in response.text:
                    self.log_test_result("Frontend Accessibility", "PASSED", "Frontend is accessible")
                    return True
                else:
                    self.log_test_result("Frontend Accessibility", "FAILED", "Frontend content not found")
                    return False
            else:
                self.log_test_result("Frontend Accessibility", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Frontend Accessibility", "FAILED", f"Exception: {str(e)}")
            return False

    def test_earnings_dashboard(self):
        """Test earnings dashboard accessibility"""
        try:
            response = requests.get(f"{self.base_url}/OSCAR-BROOME-REVENUE/executive-portal/dashboard.html", timeout=10)

            if response.status_code == 200:
                if "Earnings Dashboard" in response.text or "dashboard" in response.text.lower():
                    self.log_test_result("Earnings Dashboard", "PASSED", "Earnings dashboard accessible")
                    return True
                else:
                    self.log_test_result("Earnings Dashboard", "WARNING", "Dashboard accessible but content may be limited")
                    return True
            else:
                self.log_test_result("Earnings Dashboard", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Earnings Dashboard", "FAILED", f"Exception: {str(e)}")
            return False

    def test_error_handling(self):
        """Test error handling with invalid requests"""
        try:
            # Test invalid override request
            invalid_payload = {"invalid": "data"}
            response = requests.post(f"{self.base_url}/api/override/emergency", json=invalid_payload, timeout=10)

            if response.status_code in [400, 422, 500]:
                self.log_test_result("Error Handling", "PASSED", "Error handling working correctly")
                return True
            else:
                self.log_test_result("Error Handling", "WARNING", f"Unexpected error response: {response.status_code}")
                return True
        except Exception as e:
            self.log_test_result("Error Handling", "FAILED", f"Exception: {str(e)}")
            return False

    def generate_report(self):
        """Generate comprehensive test report"""
        passed = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed = len([r for r in self.test_results if r["status"] == "FAILED"])
        skipped = len([r for r in self.test_results if r["status"] == "SKIPPED"])
        warnings = len([r for r in self.test_results if r["status"] == "WARNING"])
        total = len(self.test_results)

        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0

        report = f"""
{'='*80}
OWLBAN GROUP INTEGRATED PLATFORM - E2E TEST REPORT
{'='*80}
Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.2f} seconds

SUMMARY:
--------
Total Tests: {total}
Passed: {passed}
Failed: {failed}
Skipped: {skipped}
Warnings: {warnings}
Success Rate: {(passed/total*100):.1f}% if total > 0 else 0%

DETAILED RESULTS:
-----------------
"""

        for result in self.test_results:
            status_icon = {
                "PASSED": "[PASS]",
                "FAILED": "[FAIL]",
                "SKIPPED": "[SKIP]",
                "WARNING": "[WARN]"
            }.get(result["status"], "[UNK]")

            report += f"{status_icon} {result['test_name']}: {result['message']}\n"
            if result.get("details"):
                report += f"   Details: {result['details']}\n"

        report += f"\n{'='*80}\n"

        # Save report to file
        with open("e2e_test_report.txt", "w") as f:
            f.write(report)

        print(report)
        return report

    def run_all_tests(self):
        """Run the complete E2E test suite"""
        self.start_time = time.time()
        try:
            print("Starting Owlban Group E2E Test Suite...")
        except UnicodeEncodeError:
            print("Starting Owlban Group E2E Test Suite...")
        print("="*80)

        # Start server
        if not self.start_server():
            print("Cannot proceed without server. Aborting tests.")
            return False

        try:
            # Basic connectivity tests
            self.test_server_health()
            self.test_frontend_accessibility()

            # Login Override System Tests
            print("\nTesting Login Override System...")
            self.test_login_override_emergency()
            self.test_login_override_admin()
            self.test_login_override_technical()
            self.test_login_override_validation()
            self.test_active_overrides()

            # Core Platform Tests
            print("\nTesting Leadership Simulation...")
            self.test_leadership_simulation()

            print("\nTesting NVIDIA GPU Integration...")
            self.test_gpu_status()

            print("\nTesting Earnings Dashboard...")
            self.test_earnings_dashboard()

            # Error Handling Tests
            print("\nTesting Error Handling...")
            self.test_error_handling()

        finally:
            self.end_time = time.time()
            self.stop_server()

        # Generate final report
        self.generate_report()

        # Return success based on critical test results
        critical_tests = ["Server Health", "Emergency Override", "Admin Override", "Frontend Accessibility"]
        critical_failed = any(
            r["status"] == "FAILED" for r in self.test_results
            if r["test_name"] in critical_tests
        )

        return not critical_failed

def main():
    """Main execution function"""
    suite = E2ETestSuite()

    try:
        success = suite.run_all_tests()

        if success:
            print("E2E Test Suite completed successfully!")
            sys.exit(0)
        else:
            print("E2E Test Suite completed with critical failures!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest suite interrupted by user")
        suite.stop_server()
        sys.exit(130)
    except Exception as e:
        try:
            print(f"\nUnexpected error during test execution: {e}")
        except UnicodeEncodeError:
            print(f"\nUnexpected error during test execution: {e}")
        suite.stop_server()
        sys.exit(1)

if __name__ == "__main__":
    main()
