#!/usr/bin/env python3
"""
Critical-path testing for the newly added get_frame_sync_mode method.
Tests basic functionality and error handling.
"""

import sys
import os
import logging
from typing import Any

# Add current directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from nvidia_control_panel_enhanced import NVIDIAControlPanel, FrameSyncMode, get_nvidia_control_panel
    print("✓ Successfully imported NVIDIAControlPanel and FrameSyncMode")
except ImportError as e:
    print(f"✗ Failed to import required modules: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic functionality of get_frame_sync_mode method."""
    print("\n=== Testing Basic Functionality ===")

    try:
        # Get the singleton instance
        panel = get_nvidia_control_panel()
        print("✓ Successfully obtained NVIDIAControlPanel instance")

        # Test get_frame_sync_mode with default GPU index
        result = panel.get_frame_sync_mode()
        print(f"✓ get_frame_sync_mode() returned: {result}")

        # Verify return type
        if isinstance(result, FrameSyncMode):
            print("✓ Return value is valid FrameSyncMode enum")
        else:
            print(f"✗ Return value is not FrameSyncMode enum: {type(result)}")
            return False

        # Test with specific GPU index
        result_gpu0 = panel.get_frame_sync_mode(0)
        print(f"✓ get_frame_sync_mode(0) returned: {result_gpu0}")

        # Test with different GPU index (if available)
        if panel.gpu_count > 1:
            result_gpu1 = panel.get_frame_sync_mode(1)
            print(f"✓ get_frame_sync_mode(1) returned: {result_gpu1}")
        else:
            print("ℹ Only one GPU detected, skipping multi-GPU test")

        return True

    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_error_handling():
    """Test error handling of get_frame_sync_mode method."""
    print("\n=== Testing Error Handling ===")

    try:
        panel = get_nvidia_control_panel()

        # Test with invalid GPU index (negative)
        try:
            result = panel.get_frame_sync_mode(-1)
            print(f"✓ Invalid GPU index -1 handled gracefully: {result}")
        except Exception as e:
            print(f"✗ Invalid GPU index -1 caused exception: {e}")
            return False

        # Test with invalid GPU index (too high)
        try:
            result = panel.get_frame_sync_mode(999)
            print(f"✓ Invalid GPU index 999 handled gracefully: {result}")
        except Exception as e:
            print(f"✗ Invalid GPU index 999 caused exception: {e}")
            return False

        # Test with non-integer GPU index
        try:
            result = panel.get_frame_sync_mode("invalid")
            print(f"✗ Non-integer GPU index should have failed but returned: {result}")
            return False
        except (TypeError, ValueError) as e:
            print(f"✓ Non-integer GPU index properly rejected: {e}")
        except Exception as e:
            print(f"✗ Non-integer GPU index caused unexpected exception: {e}")
            return False

        return True

    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def test_integration():
    """Test integration with existing class methods."""
    print("\n=== Testing Integration ===")

    try:
        panel = get_nvidia_control_panel()

        # Test that the method exists and is callable
        if hasattr(panel, 'get_frame_sync_mode'):
            print("✓ get_frame_sync_mode method exists")
        else:
            print("✗ get_frame_sync_mode method missing")
            return False

        if callable(getattr(panel, 'get_frame_sync_mode', None)):
            print("✓ get_frame_sync_mode method is callable")
        else:
            print("✗ get_frame_sync_mode method is not callable")
            return False

        # Test that helper methods exist
        if hasattr(panel, '_get_frame_sync_mode_via_nvapi'):
            print("✓ _get_frame_sync_mode_via_nvapi helper method exists")
        else:
            print("✗ _get_frame_sync_mode_via_nvapi helper method missing")
            return False

        if hasattr(panel, '_get_frame_sync_mode_via_system'):
            print("✓ _get_frame_sync_mode_via_system helper method exists")
        else:
            print("✗ _get_frame_sync_mode_via_system helper method missing")
            return False

        # Test that FrameSyncMode enum values are accessible
        frame_sync_values = [mode.value for mode in FrameSyncMode]
        print(f"✓ FrameSyncMode enum values: {frame_sync_values}")

        return True

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all critical-path tests."""
    print("Starting Critical-Path Testing for get_frame_sync_mode method")
    print("=" * 60)

    # Configure logging to see any warnings/errors
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Error Handling", test_error_handling),
        ("Integration", test_integration)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All critical-path tests PASSED!")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
