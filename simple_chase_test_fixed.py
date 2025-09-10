#!/usr/bin/env python3
"""
Simple test to verify Chase integration routes are working
"""

import requests
import sys

def test_chase_routes():
    """Test all Chase service routes"""
    base_url = "http://localhost:5000"

    routes = [
        '/chase-credit-cards',
        '/chase-mortgage',
        '/chase-auto-finance'
    ]

    print("Testing Chase Integration Routes:")
    print("=" * 40)

    all_working = True

    for route in routes:
        try:
            url = f"{base_url}{route}"
            response = requests.get(url, timeout=10)  # Increased timeout

            if response.status_code == 200:
                print(f"[OK] {route}: {response.status_code} - Working")
            else:
                print(f"[FAIL] {route}: {response.status_code} - Not working")
                all_working = False

        except requests.exceptions.RequestException as e:
            print(f"[FAIL] {route}: Connection failed - {str(e)}")
            all_working = False

    print("=" * 40)
    if all_working:
        print("SUCCESS: All Chase routes are working correctly!")
        return True
    else:
        print("ERROR: Some routes are not working. Please check the Flask app.")
        return False

if __name__ == "__main__":
    success = test_chase_routes()
    sys.exit(0 if success else 1)
