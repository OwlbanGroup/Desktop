#!/usr/bin/env python3
"""
Improved Chase integration test with better timeout handling and encoding fixes
"""

import requests
import sys
import time
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ChaseIntegrationTester:
    def __init__(self, base_url="http://localhost:5000", timeout=15, retries=3):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session(retries)

    def _create_session(self, retries):
        """Create a session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def test_route(self, route, expected_status=200):
        """Test a single route with improved error handling"""
        url = f"{self.base_url}{route}"

        try:
            print(f"Testing {route}...")
            response = self.session.get(url, timeout=self.timeout)

            # Handle different content types properly
            content_type = response.headers.get('content-type', '').lower()

            if 'application/json' in content_type:
                try:
                    response_data = response.json()
                    print(f"  Response: {json.dumps(response_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"  Response (text): {response.text[:200]}...")
            else:
                # Handle text/html or other content types
                print(f"  Response: {response.text[:200]}...")

            if response.status_code == expected_status:
                print(f"  ✓ SUCCESS: {route} returned {response.status_code}")
                return True
            else:
                print(f"  ✗ FAIL: {route} returned {response.status_code} (expected {expected_status})")
                return False

        except requests.exceptions.Timeout:
            print(f"  ✗ TIMEOUT: {route} timed out after {self.timeout}s")
            return False
        except requests.exceptions.ConnectionError:
            print(f"  ✗ CONNECTION ERROR: Could not connect to {url}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"  ✗ REQUEST ERROR: {route} - {str(e)}")
            return False
        except Exception as e:
            print(f"  ✗ UNEXPECTED ERROR: {route} - {str(e)}")
            return False

    def test_all_routes(self):
        """Test all Chase integration routes"""
        routes = [
            ('/', 200),
            ('/chase-credit-cards', 200),
            ('/chase-mortgage', 200),
            ('/chase-auto-finance', 200)
        ]

        print("🚀 Starting Chase Integration Tests")
        print("=" * 50)

        results = []
        for route, expected_status in routes:
            success = self.test_route(route, expected_status)
            results.append((route, success))
            time.sleep(0.5)  # Brief pause between requests

        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")

        successful = sum(1 for _, success in results if success)
        total = len(results)

        for route, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status}: {route}")

        print(f"\nOverall: {successful}/{total} tests passed")

        if successful == total:
            print("🎉 SUCCESS: All Chase integration routes are working!")
            return True
        else:
            print("⚠️  WARNING: Some routes failed. Check the Flask app and dependencies.")
            return False

def main():
    tester = ChaseIntegrationTester()

    # Test if server is responding at all
    try:
        response = requests.get(f"{tester.base_url}/", timeout=5)
        print(f"Server is responding (status: {response.status_code})")
    except requests.exceptions.RequestException:
        print("❌ ERROR: Flask server is not running or not accessible")
        print("Please start the Flask app first:")
        print("  python simple_flask_test_fixed.py")
        sys.exit(1)

    success = tester.test_all_routes()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
