#!/usr/bin/env python3
"""
Test script for the new get_driver_updates method in NvidiaIntegration
"""

from nvidia_integration import NvidiaIntegration

def test_driver_updates():
    """Test the get_driver_updates method"""
    try:
        ni = NvidiaIntegration()

        # Check if method exists
        if hasattr(ni, 'get_driver_updates'):
            print("✓ get_driver_updates method found")

            # Test the method
            result = ni.get_driver_updates()
            print("✓ Method executed successfully")
            print(f"Result keys: {list(result.keys())}")

            # Check expected keys
            expected_keys = ['driver_versions', 'download_links', 'system_requirements',
                           'release_notes', 'supported_products', 'last_updated', 'source']

            for key in expected_keys:
                if key in result:
                    print(f"✓ Found expected key: {key}")
                else:
                    print(f"✗ Missing expected key: {key}")

            # Print some sample data
            print(f"\nDriver versions found: {len(result.get('driver_versions', []))}")
            print(f"Download links found: {len(result.get('download_links', []))}")
            print(f"Source: {result.get('source', 'N/A')}")

            return True
        else:
            print("✗ get_driver_updates method not found")
            return False

    except Exception as e:
        print(f"✗ Error testing method: {e}")
        return False

if __name__ == "__main__":
    print("Testing get_driver_updates method...")
    success = test_driver_updates()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
