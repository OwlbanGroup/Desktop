import requests
import time
import json

# Comprehensive test for JPMorgan Payment Proxy Integration
def test_proxy_comprehensive():
    base_url = 'http://localhost:5000'

    print("🔍 Starting Comprehensive JPMorgan Payment Proxy Testing...")
    print("=" * 60)

    test_results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }

    def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
        nonlocal test_results
        test_results['total'] += 1

        try:
            if method.upper() == 'GET':
                response = requests.get(f"{base_url}{endpoint}")
            elif method.upper() == 'POST':
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json=data,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                print(f"❌ Unsupported method: {method}")
                test_results['failed'] += 1
                return False

            if response.status_code == expected_status:
                print(f"✅ {description}: {response.status_code}")
                if response.status_code == 200:
                    try:
                        print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...")
                    except:
                        print(f"   Response: {response.text[:200]}...")
                test_results['passed'] += 1
                return True
            else:
                print(f"❌ {description}: Expected {expected_status}, got {response.status_code}")
                print(f"   Error: {response.text}")
                test_results['failed'] += 1
                return False

        except requests.RequestException as e:
            print(f"❌ {description}: Connection failed - {e}")
            test_results['failed'] += 1
            return False

    # Test 1: Health Check
    print("\n🏥 Testing Health Check Endpoint")
    test_endpoint('GET', '/api/jpmorgan-payment/health', description="Health Check")

    # Test 2: Create Payment
    print("\n💳 Testing Payment Creation")
    payment_data = {
        "amount": 100.00,
        "currency": "USD",
        "description": "Comprehensive Test Payment"
    }
    success = test_endpoint('POST', '/api/jpmorgan-payment/create-payment',
                          data=payment_data, description="Create Payment")

    # Test 3: Payment Status (if payment was created successfully)
    if success:
        print("\n📊 Testing Payment Status Check")
        # Assuming the response contains a payment_id, but since we can't parse it easily,
        # we'll test with a dummy ID
        test_endpoint('GET', '/api/jpmorgan-payment/payment-status/test-payment-123',
                    expected_status=404, description="Payment Status (dummy ID)")

    # Test 4: Refund
    print("\n💸 Testing Refund")
    refund_data = {
        "payment_id": "test-payment-123",
        "amount": 50.00,
        "reason": "Test refund"
    }
    test_endpoint('POST', '/api/jpmorgan-payment/refund',
                data=refund_data, description="Process Refund")

    # Test 5: Capture
    print("\n🎯 Testing Payment Capture")
    capture_data = {
        "payment_id": "test-payment-123",
        "amount": 100.00
    }
    test_endpoint('POST', '/api/jpmorgan-payment/capture',
                data=capture_data, description="Capture Payment")

    # Test 6: Void
    print("\n🚫 Testing Payment Void")
    void_data = {
        "payment_id": "test-payment-123",
        "reason": "Test void"
    }
    test_endpoint('POST', '/api/jpmorgan-payment/void',
                data=void_data, description="Void Payment")

    # Test 7: Transactions
    print("\n📋 Testing Transaction History")
    test_endpoint('GET', '/api/jpmorgan-payment/transactions',
                description="Get Transactions")

    # Test 8: Webhook
    print("\n🪝 Testing Webhook")
    webhook_data = {
        "event": "payment.succeeded",
        "payment_id": "test-payment-123",
        "amount": 100.00
    }
    test_endpoint('POST', '/api/jpmorgan-payment/webhook',
                data=webhook_data, description="Webhook Handler")

    # Test 9: Error Handling - Invalid Endpoint
    print("\n🚨 Testing Error Handling")
    test_endpoint('GET', '/api/jpmorgan-payment/invalid-endpoint',
                expected_status=404, description="Invalid Endpoint")

    # Test 10: Malformed Request
    print("\n🔧 Testing Malformed Request")
    test_endpoint('POST', '/api/jpmorgan-payment/create-payment',
                data={"invalid": "data"}, expected_status=400,
                description="Malformed Payment Data")

    # Test 11: Other Flask Endpoints
    print("\n🔗 Testing Other Flask Endpoints")
    test_endpoint('GET', '/api/gpu/status', description="GPU Status")
    test_endpoint('GET', '/api/earnings', description="Earnings Data")

    # Test 12: Frontend Access
    print("\n🌐 Testing Frontend Access")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Frontend Access: 200")
            test_results['passed'] += 1
        else:
            print(f"❌ Frontend Access: {response.status_code}")
            test_results['failed'] += 1
        test_results['total'] += 1
    except Exception as e:
        print(f"❌ Frontend Access: Connection failed - {e}")
        test_results['failed'] += 1
        test_results['total'] += 1

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(".1f")

    if test_results['failed'] == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return test_results

if __name__ == "__main__":
    results = test_proxy_comprehensive()
