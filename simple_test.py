import requests
import time

print("Starting simple test...")

# Wait for servers to start
time.sleep(3)

try:
    print("Testing health endpoint...")
    response = requests.get('http://localhost:5000/api/jpmorgan-payment/health', timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        print("SUCCESS: Integration is working!")
    else:
        print("FAILED: Integration not working")

except Exception as e:
    print(f"ERROR: {e}")

print("Test completed.")
