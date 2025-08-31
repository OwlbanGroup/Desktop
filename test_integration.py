#!/usr/bin/env python3
"""
Integration test script for Owlban Group platform
"""

import sys
import os
import subprocess
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        from organizational_leadership import leadership
        print("✓ organizational_leadership imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import organizational_leadership: {e}")
        return False

    try:
        from revenue_tracking import RevenueTracker
        print("✓ revenue_tracking imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import revenue_tracking: {e}")
        return False

    try:
        from nvidia_integration import NvidiaIntegration
        print("✓ nvidia_integration imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import nvidia_integration: {e}")
        return False

    try:
        from flask import Flask
        print("✓ flask imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import flask: {e}")
        return False

    return True

def test_backend_functionality():
    """Test backend functionality without starting server"""
    print("\nTesting backend functionality...")

    try:
        from organizational_leadership import leadership
        from revenue_tracking import RevenueTracker

        # Test leadership creation
        leader = leadership.Leader("Test Leader", leadership.LeadershipStyle.DEMOCRATIC)
        print("✓ Leader created successfully")

        # Test team creation
        team = leadership.Team(leader)
        team.add_member(leadership.TeamMember("Test Member", "Developer"))
        print("✓ Team created and member added successfully")

        # Test revenue tracking
        revenue_tracker = RevenueTracker()
        leader.set_revenue_tracker(revenue_tracker)
        result = leader.lead_team()
        print(f"✓ Leadership simulation successful: {result[:50]}...")

        return True
    except Exception as e:
        print(f"✗ Backend functionality test failed: {e}")
        return False

def test_nvidia_integration():
    """Test NVIDIA integration"""
    print("\nTesting NVIDIA integration...")

    try:
        from nvidia_integration import NvidiaIntegration
        nvidia = NvidiaIntegration()
        status = nvidia.get_gpu_settings()
        print(f"✓ NVIDIA integration working: {type(status)}")
        return True
    except Exception as e:
        print(f"✗ NVIDIA integration test failed: {e}")
        return False

def test_frontend_files():
    """Test that frontend files exist and are accessible"""
    print("\nTesting frontend files...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("✗ Frontend directory not found")
        return False

    required_files = [
        "index.html",
        "OSCAR-BROOME-REVENUE/executive-portal/dashboard.html",
        "OSCAR-BROOME-REVENUE/executive-portal/dashboard.js",
        "OSCAR-BROOME-REVENUE/executive-portal/styles.css"
    ]

    for file_path in required_files:
        full_path = frontend_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} not found")
            return False

    return True

def main():
    """Run all integration tests"""
    print("🐦 Owlban Group Integration Test Suite")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("Backend Functionality", test_backend_functionality),
        ("NVIDIA Integration", test_nvidia_integration),
        ("Frontend Files", test_frontend_files)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
