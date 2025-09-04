#!/usr/bin/env python3

import sys
import traceback

with open('test_imports_results.txt', 'w') as f:
    f.write("=== IMPORT TEST RESULTS ===\n\n")

    # Test organizational_leadership
    try:
        from organizational_leadership import leadership
        f.write("✓ organizational_leadership imported successfully\n")
    except Exception as e:
        f.write(f"✗ Error importing organizational_leadership: {e}\n")
        f.write(f"Traceback: {traceback.format_exc()}\n")

    # Test revenue_tracking
    try:
        from revenue_tracking import RevenueTracker
        f.write("✓ revenue_tracking imported successfully\n")
    except Exception as e:
        f.write(f"✗ Error importing revenue_tracking: {e}\n")
        f.write(f"Traceback: {traceback.format_exc()}\n")

    # Test nvidia_integration
    try:
        from nvidia_integration import NvidiaIntegration
        f.write("✓ nvidia_integration imported successfully\n")
    except Exception as e:
        f.write(f"✗ Error importing nvidia_integration: {e}\n")
        f.write(f"Traceback: {traceback.format_exc()}\n")

    # Test chase_mortgage
    try:
        from OSCAR_BROOME_REVENUE.earnings_dashboard import chase_mortgage
        f.write("✓ chase_mortgage imported successfully\n")
        f.write(f"  router: {chase_mortgage.router}\n")
    except Exception as e:
        f.write(f"✗ Error importing chase_mortgage: {e}\n")
        f.write(f"Traceback: {traceback.format_exc()}\n")

    # Test chase_auto_finance
    try:
        from OSCAR_BROOME_REVENUE.earnings_dashboard import chase_auto_finance
        f.write("✓ chase_auto_finance imported successfully\n")
        f.write(f"  router: {chase_auto_finance.router}\n")
    except Exception as e:
        f.write(f"✗ Error importing chase_auto_finance: {e}\n")
        f.write(f"Traceback: {traceback.format_exc()}\n")

    # Test app_with_chase_integration
    try:
        from app_with_chase_integration import app
        f.write("✓ app_with_chase_integration imported successfully\n")
        f.write(f"  app: {app}\n")
    except Exception as e:
        f.write(f"✗ Error importing app_with_chase_integration: {e}\n")
        f.write(f"Traceback: {traceback.format_exc()}\n")

    f.write("\n=== IMPORT TEST COMPLETED ===\n")

print("Import test completed - check test_imports_results.txt")
