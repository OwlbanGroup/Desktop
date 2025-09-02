#!/usr/bin/env python3
"""
Test script for the new get_contacts_and_policy_numbers method in NvidiaIntegration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nvidia_integration import NvidiaIntegration

def test_contacts_and_policy_numbers():
    """Test the get_contacts_and_policy_numbers method."""
    print("Testing get_contacts_and_policy_numbers method...")

    # Initialize NVIDIA integration
    nvidia = NvidiaIntegration()

    # Test the method
    try:
        result = nvidia.get_contacts_and_policy_numbers()

        print("✅ Method executed successfully!")
        print(f"Source: {result.get('source', 'N/A')}")
        print(f"Last updated: {result.get('last_updated', 'N/A')}")
        print(f"Number of contacts: {len(result.get('contacts', []))}")
        print(f"Number of policy numbers: {len(result.get('policy_numbers', []))}")
        print(f"Number of links: {len(result.get('links', []))}")

        print("\n📞 Contacts:")
        for contact in result.get('contacts', []):
            print(f"  • {contact}")

        print("\n📋 Policy Numbers:")
        for policy in result.get('policy_numbers', []):
            print(f"  • {policy}")

        print("\n🌐 Links:")
        for link in result.get('links', []):
            print(f"  • {link}")

        return True

    except Exception as e:
        print(f"❌ Error testing method: {e}")
        return False

if __name__ == "__main__":
    success = test_contacts_and_policy_numbers()
    sys.exit(0 if success else 1)
