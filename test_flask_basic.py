#!/usr/bin/env python3
"""
Basic test to check if Flask app is responding
"""

import requests
import sys

def test_basic_response():
    """Test basic Flask app response"""
    base_url = "http://localhost:5000"

    try:
        print("Testing basic Flask response...")
        response = requests.get(base_url, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 200:
            print("SUCCESS: Flask app is responding!")
            return True
        else:
            print(f"ERROR: Unexpected status code {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Connection failed - {str(e)}")
        return False

if __name__ == "__main__":
    success = test_basic_response()
    sys.exit(0 if success else 1)
