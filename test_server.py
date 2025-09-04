#!/usr/bin/env python3

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.app_server import app
    print("Flask app imported successfully")

    # Test if we can run the app
    with app.test_client() as client:
        response = client.get('/health')
        print(f"Health endpoint response: {response.status_code}")
        print(f"Response data: {response.get_json()}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
