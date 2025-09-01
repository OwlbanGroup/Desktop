#!/usr/bin/env python3
"""
Test script for the new get_benefits_resources method in NvidiaIntegration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nvidia_integration import NvidiaIntegration

def test_benefits_resources():
    """Test the get_benefits_resources method."""
    print("Testing get_benefits_resources method...")

    # Initialize NVIDIA integration
    nvidia = NvidiaIntegration()

    # Test the method
    try:
        result = nvidia.get_benefits_resources()

        print("✅ Method executed successfully!")
        print(f"Source: {result.get('source', 'N/A')}")
        print(f"Last updated: {result.get('last_updated', 'N/A')}")
        print(f"Number of benefits: {len(result.get('benefits', []))}")
        print(f"Number of resources: {len(result.get('resources', []))}")
        print(f"Number of links: {len(result.get('links', []))}")

        print("\n📋 Benefits:")
        for benefit in result.get('benefits', []):
            print(f"  • {benefit}")

        print("\n🔗 Resources:")
        for resource in result.get('resources', []):
            print(f"  • {resource}")

        print("\n🌐 Links:")
        for link in result.get('links', []):
            print(f"  • {link}")

        # Additional check for business travel accident insurance presence
        if not any("Business Travel Accident Insurance" in b for b in result.get('benefits', [])):
            raise AssertionError("Business Travel Accident Insurance benefit not found in results.")

        # Check for personal loans presence
        if not any("Personal Loans" in b for b in result.get('benefits', [])):
            raise AssertionError("Personal Loans benefit not found in results.")

        # Check for personal loans URL presence
        if "https://www.nvidia.com/en-us/benefits/money/personal-loans/" not in result.get('links', []):
            raise AssertionError("Personal Loans URL not found in results.")

        return True

    except Exception as e:
        print(f"❌ Error testing method: {e}")
        return False

if __name__ == "__main__":
    success = test_benefits_resources()
    sys.exit(0 if success else 1)
