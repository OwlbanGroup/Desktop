#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from nvidia_integration import NvidiaIntegration

    # Create instance
    nvidia = NvidiaIntegration()

    # Test get_benefits_resources method
    print("Testing get_benefits_resources method...")
    benefits = nvidia.get_benefits_resources()

    print("Benefits resources retrieved successfully!")
    print(f"Number of benefits: {len(benefits)}")

    # Check for Schwab Financial Concierge
    schwab_found = False
    for benefit in benefits:
        if 'schwab' in benefit.lower() or 'financial concierge' in benefit.lower():
            schwab_found = True
            print(f"Found Schwab benefit: {benefit}")
            break

    if schwab_found:
        print("✓ Schwab Financial Concierge benefit found!")
    else:
        print("✗ Schwab Financial Concierge benefit not found")

    # Check for Personal Loans
    personal_loans_found = False
    for benefit in benefits:
        if 'personal loans' in benefit.lower():
            personal_loans_found = True
            print(f"Found Personal Loans benefit: {benefit}")
            break

    if personal_loans_found:
        print("✓ Personal Loans benefit found!")
    else:
        print("✗ Personal Loans benefit not found")

    print("\nTest completed successfully!")

except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure nvidia_integration.py is in the current directory")

except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
