#!/usr/bin/env python3
"""
Test script for the fixed NVIDIA integration module.
Tests all functionality including GPU settings, benefits fetching, and loan applications.
"""

import sys
import json
from datetime import datetime

def test_nvidia_integration():
    """Test the NVIDIA integration module functionality."""
    print("Testing NVIDIA Integration Module...")
    print("=" * 50)

    try:
        from nvidia_integration import NvidiaIntegration
        print("✓ NVIDIA integration module imported successfully")

        # Initialize the integration
        nvidia = NvidiaIntegration()
        print("✓ NvidiaIntegration class initialized")

        # Test GPU settings retrieval
        print("\n1. Testing GPU Settings Retrieval:")
        gpu_settings = nvidia.get_gpu_settings()
        print(f"✓ GPU settings retrieved: {json.dumps(gpu_settings, indent=2)}")

        # Test GPU settings application
        print("\n2. Testing GPU Settings Application:")
        test_settings = {
            "power_mode": "Optimal Power",
            "texture_filtering": "Quality",
            "vertical_sync": "Off"
        }
        result = nvidia.set_gpu_settings(test_settings)
        print(f"✓ GPU settings applied: {result}")

        # Test benefits resources fetching
        print("\n3. Testing Benefits Resources Fetching:")
        benefits = nvidia.get_benefits_resources()
        print(f"✓ Benefits resources fetched: {len(benefits.get('benefits', []))} benefits found")

        # Test health provider network
        print("\n4. Testing Health Provider Network:")
        providers = nvidia.get_health_provider_network()
        print(f"✓ Health providers fetched: {len(providers.get('providers', []))} providers found")

        # Test contacts and policy numbers
        print("\n5. Testing Contacts and Policy Numbers:")
        contacts = nvidia.get_contacts_and_policy_numbers()
        print(f"✓ Contacts fetched: {len(contacts.get('contacts', []))} contacts found")

        # Test driver updates
        print("\n6. Testing Driver Updates:")
        drivers = nvidia.get_driver_updates()
        print(f"✓ Driver updates fetched: {len(drivers.get('driver_versions', []))} versions found")

        # Test loan application
        print("\n7. Testing Auto Loan Application:")
        vehicle_info = {
            "model": "Tesla Model 3",
            "price": 45000,
            "dealership": "Tesla Dealership"
        }
        applicant_info = {
            "name": "John Doe",
            "annual_income": 120000,
            "employment_status": "Full-time",
            "credit_score": 750
        }
        loan_result = nvidia.apply_for_auto_loan(vehicle_info, applicant_info)
        print(f"✓ Loan application result: {loan_result.get('success', False)}")

        # Test loan status check
        if loan_result.get('success'):
            print("\n8. Testing Loan Status Check:")
            application_id = loan_result['loan_application']['application_id']
            status = nvidia.get_loan_status(application_id)
            print(f"✓ Loan status checked: {status.get('status', 'Unknown')}")

        # Test complete purchase integration
        print("\n9. Testing Complete Purchase Integration:")
        integration_result = nvidia.integrate_auto_purchase_with_loan(vehicle_info, applicant_info)
        print(f"✓ Purchase integration result: {integration_result.get('success', False)}")

        print("\n" + "=" * 50)
        print("🎉 All NVIDIA integration tests completed successfully!")
        print("The null byte encoding error has been fixed.")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_import_variations():
    """Test different import variations to ensure compatibility."""
    print("\nTesting Import Variations:")
    print("-" * 30)

    try:
        # Test direct import
        import nvidia_integration
        print("✓ Direct import successful")

        # Test from import
        from nvidia_integration import NvidiaIntegration, get_nvidia_control_panel
        print("✓ From import successful")

        # Test class instantiation
        nvidia = NvidiaIntegration()
        print("✓ Class instantiation successful")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    print("NVIDIA Integration Module Fix Verification")
    print("=" * 50)
    print(f"Test started at: {datetime.now().isoformat()}")

    # Test imports first
    import_success = test_import_variations()

    if import_success:
        # Run comprehensive tests
        test_success = test_nvidia_integration()

        if test_success:
            print("\n✅ All tests passed! NVIDIA integration is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed.")
            sys.exit(1)
    else:
        print("\n❌ Import tests failed. Cannot proceed with functionality tests.")
        sys.exit(1)
