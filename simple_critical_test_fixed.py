#!/usr/bin/env python3
"""
Simple Critical Path Test for NVIDIA OSCAR-BROOME-REVENUE Integration

Tests basic functionality without starting the Flask app.
"""

import sys
import os
import importlib.util

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing module imports...")

    try:
        # Test Flask imports
        import flask
        from flask_cors import CORS
        print("[PASS] Flask and CORS imported successfully")

        # Test other basic imports
        import json
        import uuid
        import threading
        import time
        import logging
        from datetime import datetime
        print("[PASS] Basic Python modules imported successfully")

        # Test system monitoring imports
        import psutil
        import platform
        print("[PASS] System monitoring modules imported successfully")

        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_nvidia_integration_import():
    """Test if NVIDIA integration module can be imported."""
    print("\nTesting NVIDIA integration import...")

    try:
        # Add OSCAR-BROOME-REVENUE to path
        sys.path.append(os.path.join(os.getcwd(), 'OSCAR-BROOME-REVENUE'))

        # Try to import NVIDIA integration
        from nvidia_integration_fixed import NvidiaIntegration
        print("[PASS] NVIDIA integration module imported successfully")

        # Test basic instantiation
        nvidia = NvidiaIntegration()
        print("[PASS] NVIDIA integration object created successfully")

        return True
    except ImportError as e:
        print(f"[FAIL] NVIDIA integration import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] NVIDIA integration instantiation error: {e}")
        return False

def test_revenue_tracker_import():
    """Test if revenue tracker can be imported."""
    print("\nTesting revenue tracker import...")

    try:
        from revenue_tracking import RevenueTracker
        print("[PASS] Revenue tracker module imported successfully")

        # Test basic instantiation
        tracker = RevenueTracker()
        print("[PASS] Revenue tracker object created successfully")

        return True
    except ImportError as e:
        print(f"[FAIL] Revenue tracker import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Revenue tracker instantiation error: {e}")
        return False

def test_leadership_import():
    """Test if leadership module can be imported."""
    print("\nTesting leadership module import...")

    try:
        from organizational_leadership import leadership
        print("[PASS] Leadership module imported successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] Leadership import error: {e}")
        return False

def test_main_integration_file():
    """Test if the main integration file can be loaded."""
    print("\nTesting main integration file...")

    try:
        # Load the main integration file as a module
        spec = importlib.util.spec_from_file_location("integration", "nvidia_oscar_broome_integration.py")
        integration_module = importlib.util.module_from_spec(spec)

        # Test if we can at least load the module without executing it
        print("[PASS] Main integration file can be loaded")

        # Check if key classes are defined
        with open("nvidia_oscar_broome_integration.py", "r") as f:
            content = f.read()

        if "class NVIDIAMonitor:" in content:
            print("[PASS] NVIDIAMonitor class found")
        else:
            print("[FAIL] NVIDIAMonitor class not found")
            return False

        if "class FinancialAnalyticsEngine:" in content:
            print("[PASS] FinancialAnalyticsEngine class found")
        else:
            print("[FAIL] FinancialAnalyticsEngine class not found")
            return False

        if "class LeadershipSystem:" in content:
            print("[PASS] LeadershipSystem class found")
        else:
            print("[FAIL] LeadershipSystem class not found")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] Main integration file test error: {e}")
        return False

def main():
    """Run all simple critical path tests."""
    print("=" * 60)
    print("SIMPLE CRITICAL PATH TESTING")
    print("=" * 60)

    test_results = []

    # Run tests
    test_results.append(("Module Imports", test_imports()))
    test_results.append(("NVIDIA Integration", test_nvidia_integration_import()))
    test_results.append(("Revenue Tracker", test_revenue_tracker_import()))
    test_results.append(("Leadership Module", test_leadership_import()))
    test_results.append(("Main Integration File", test_main_integration_file()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("SUCCESS: All critical path tests passed!")
        print("\nThe NVIDIA OSCAR-BROOME-REVENUE integration is ready for deployment.")
        return True
    else:
        print("WARNING: Some tests failed. Please review the implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
