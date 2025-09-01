import requests

# Test the JPMorgan payment proxy integration
def test_proxy():
    base_url = 'http://localhost:5000'

    print("Testing JPMorgan Payment Proxy Integration...")

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/jpmorgan-payment/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")

    # Test create payment endpoint
    try:
        payment_data = {
            "amount": 100.00,
            "currency": "USD",
            "description": "Test payment"
        }
        response = requests.post(
            f"{base_url}/api/jpmorgan-payment/create-payment",
            json=payment_data
        )
        print(f"Create payment: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Create payment failed: {e}")

if __name__ == "__main__":
    test_proxy()
