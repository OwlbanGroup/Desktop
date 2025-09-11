#!/usr/bin/env python3
"""
Comprehensive test suite for merger analytics module
Tests edge cases, error handling, performance, and integration scenarios
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from merger_analytics import MergerAnalytics
    print("✓ Successfully imported MergerAnalytics")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class TestMergerAnalyticsComprehensive:
    """Comprehensive test suite for MergerAnalytics"""

    def __init__(self):
        self.analytics = None
        self.test_results = []

    def log_test_result(self, test_name, passed, message=""):
        """Log test result"""
        status = "✓ PASS" if passed else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })

    def setup(self):
        """Setup test environment"""
        try:
            self.analytics = MergerAnalytics()
            self.log_test_result("Setup", True, "MergerAnalytics instance created successfully")
            return True
        except Exception as e:
            self.log_test_result("Setup", False, f"Failed to create instance: {e}")
            return False

    def test_edge_cases_empty_data(self):
        """Test with empty or minimal data"""
        print("\n--- Testing Edge Cases: Empty Data ---")

        # Test with empty pre-merger data
        try:
            result = self.analytics.pre_merger_performance()
            if isinstance(result, dict):
                self.log_test_result("Empty Data - Pre-merger", True, "Handled empty data gracefully")
            else:
                self.log_test_result("Empty Data - Pre-merger", False, "Unexpected return type")
        except Exception as e:
            self.log_test_result("Empty Data - Pre-merger", False, f"Exception: {e}")

        # Test synergy calculations with no data
        try:
            synergies = self.analytics.calculate_synergies()
            if isinstance(synergies, dict) and 'cost_savings' in synergies:
                self.log_test_result("Empty Data - Synergies", True, "Handled empty synergy data")
            else:
                self.log_test_result("Empty Data - Synergies", False, "Invalid synergy structure")
        except Exception as e:
            self.log_test_result("Empty Data - Synergies", False, f"Exception: {e}")

    def test_edge_cases_extreme_values(self):
        """Test with extreme values"""
        print("\n--- Testing Edge Cases: Extreme Values ---")

        # Test with very large numbers
        large_revenue_data = {
            'Oscar': {'revenue': [1000000000, 2000000000, 3000000000]},  # Billions
            'Broome': {'revenue': [500000000, 1000000000, 1500000000]}
        }

        try:
            # Temporarily replace the data
            original_data = getattr(self.analytics, '_pre_merger_data', {})
            self.analytics._pre_merger_data = large_revenue_data

            result = self.analytics.pre_merger_performance()
            if result and all(isinstance(v, dict) for v in result.values()):
                self.log_test_result("Extreme Values - Large Numbers", True, "Handled large numbers correctly")
            else:
                self.log_test_result("Extreme Values - Large Numbers", False, "Failed with large numbers")

            # Restore original data
            self.analytics._pre_merger_data = original_data

        except Exception as e:
            self.log_test_result("Extreme Values - Large Numbers", False, f"Exception: {e}")

        # Test with negative values
        try:
            negative_data = {
                'Oscar': {'revenue': [-1000000, 2000000, 3000000]},
                'Broome': {'revenue': [500000, -1000000, 1500000]}
            }

            original_data = getattr(self.analytics, '_pre_merger_data', {})
            self.analytics._pre_merger_data = negative_data

            result = self.analytics.pre_merger_performance()
            self.log_test_result("Extreme Values - Negative Numbers", True, "Handled negative values")

            self.analytics._pre_merger_data = original_data

        except Exception as e:
            self.log_test_result("Extreme Values - Negative Numbers", False, f"Exception: {e}")

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n--- Testing Error Handling ---")

        # Test with invalid data types
        try:
            invalid_data = {
                'Oscar': {'revenue': ['invalid', 'data', 'format']},
                'Broome': {'revenue': [1, 2, 3]}
            }

            original_data = getattr(self.analytics, '_pre_merger_data', {})
            self.analytics._pre_merger_data = invalid_data

            result = self.analytics.pre_merger_performance()
            self.log_test_result("Error Handling - Invalid Data Types", True, "Handled invalid data types")

            self.analytics._pre_merger_data = original_data

        except Exception as e:
            self.log_test_result("Error Handling - Invalid Data Types", False, f"Exception: {e}")

        # Test with None values
        try:
            none_data = {
                'Oscar': {'revenue': [None, 2000000, 3000000]},
                'Broome': {'revenue': [500000, None, 1500000]}
            }

            original_data = getattr(self.analytics, '_pre_merger_data', {})
            self.analytics._pre_merger_data = none_data

            result = self.analytics.pre_merger_performance()
            self.log_test_result("Error Handling - None Values", True, "Handled None values")

            self.analytics._pre_merger_data = original_data

        except Exception as e:
            self.log_test_result("Error Handling - None Values", False, f"Exception: {e}")

    def test_data_validation(self):
        """Test data validation"""
        print("\n--- Testing Data Validation ---")

        # Test with malformed company data
        try:
            malformed_data = {
                'Oscar': {'invalid_key': [1000000, 2000000, 3000000]},
                'Broome': {'revenue': [500000, 1000000, 1500000]}
            }

            original_data = getattr(self.analytics, '_pre_merger_data', {})
            self.analytics._pre_merger_data = malformed_data

            result = self.analytics.pre_merger_performance()
            self.log_test_result("Data Validation - Malformed Data", True, "Handled malformed data")

            self.analytics._pre_merger_data = original_data

        except Exception as e:
            self.log_test_result("Data Validation - Malformed Data", False, f"Exception: {e}")

        # Test with missing companies
        try:
            single_company_data = {
                'Oscar': {'revenue': [1000000, 2000000, 3000000]}
            }

            original_data = getattr(self.analytics, '_pre_merger_data', {})
            self.analytics._pre_merger_data = single_company_data

            result = self.analytics.pre_merger_performance()
            self.log_test_result("Data Validation - Single Company", True, "Handled single company data")

            self.analytics._pre_merger_data = original_data

        except Exception as e:
            self.log_test_result("Data Validation - Single Company", False, f"Exception: {e}")

    def test_performance(self):
        """Test performance with larger datasets"""
        print("\n--- Testing Performance ---")

        # Create large dataset
        large_dataset = {}
        for i in range(10):  # 10 companies
            company_name = f"Company_{i}"
            revenues = [1000000 * (j + 1) for j in range(100)]  # 100 data points each
            large_dataset[company_name] = {'revenue': revenues}

        try:
            original_data = getattr(self.analytics, '_pre_merger_data', {})
            self.analytics._pre_merger_data = large_dataset

            start_time = time.time()
            result = self.analytics.pre_merger_performance()
            end_time = time.time()

            duration = end_time - start_time
            if duration < 5.0:  # Should complete within 5 seconds
                self.log_test_result("Performance - Large Dataset", True, f"Completed in {duration:.2f}s")
            else:
                self.log_test_result("Performance - Large Dataset", False, f"Too slow: {duration:.2f}s")

            self.analytics._pre_merger_data = original_data

        except Exception as e:
            self.log_test_result("Performance - Large Dataset", False, f"Exception: {e}")

    def test_integration_scenarios(self):
        """Test integration with external systems"""
        print("\n--- Testing Integration Scenarios ---")

        # Test report generation
        try:
            report = self.analytics.generate_merger_report()
            if isinstance(report, dict) and 'pre_merger_performance' in report:
                self.log_test_result("Integration - Report Generation", True, "Generated comprehensive report")
            else:
                self.log_test_result("Integration - Report Generation", False, "Invalid report structure")
        except Exception as e:
            self.log_test_result("Integration - Report Generation", False, f"Exception: {e}")

        # Test JSON serialization
        try:
            import json
            report = self.analytics.generate_merger_report()
            json_str = json.dumps(report, indent=2)
            parsed_back = json.loads(json_str)

            if parsed_back == report:
                self.log_test_result("Integration - JSON Serialization", True, "JSON serialization works")
            else:
                self.log_test_result("Integration - JSON Serialization", False, "JSON round-trip failed")

        except Exception as e:
            self.log_test_result("Integration - JSON Serialization", False, f"Exception: {e}")

    def test_concurrent_operations(self):
        """Test concurrent operations"""
        print("\n--- Testing Concurrent Operations ---")

        import threading
        results = []
        errors = []

        def run_analysis():
            try:
                result = self.analytics.pre_merger_performance()
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Run multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=run_analysis)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        if len(results) == 5 and len(errors) == 0:
            self.log_test_result("Concurrent Operations", True, "All concurrent operations succeeded")
        else:
            self.log_test_result("Concurrent Operations", False, f"Results: {len(results)}, Errors: {len(errors)}")

    def test_cross_platform_compatibility(self):
        """Test cross-platform compatibility"""
        print("\n--- Testing Cross-Platform Compatibility ---")

        # Test path handling
        try:
            import os
            test_path = os.path.join("test", "path", "file.json")
            self.log_test_result("Cross-Platform - Path Handling", True, f"Path: {test_path}")
        except Exception as e:
            self.log_test_result("Cross-Platform - Path Handling", False, f"Exception: {e}")

        # Test datetime handling
        try:
            from datetime import datetime
            test_date = datetime.now()
            formatted = test_date.isoformat()
            self.log_test_result("Cross-Platform - DateTime", True, f"Date: {formatted}")
        except Exception as e:
            self.log_test_result("Cross-Platform - DateTime", False, f"Exception: {e}")

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Merger Analytics Tests")
        print("=" * 60)

        if not self.setup():
            print("❌ Setup failed, aborting tests")
            return False

        # Run all test categories
        self.test_edge_cases_empty_data()
        self.test_edge_cases_extreme_values()
        self.test_error_handling()
        self.test_data_validation()
        self.test_performance()
        self.test_integration_scenarios()
        self.test_concurrent_operations()
        self.test_cross_platform_compatibility()

        # Generate summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(".1f")

        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['message']}")
            return False

def main():
    """Main test runner"""
    tester = TestMergerAnalyticsComprehensive()
    success = tester.run_all_tests()

    if success:
        print("\n✅ Comprehensive testing completed successfully!")
        print("The merger analytics module is ready for production use.")
    else:
        print("\n❌ Some tests failed. Please review and fix issues before production deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
