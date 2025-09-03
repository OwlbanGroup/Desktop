#!/usr/bin/env python3
"""
Simple test to verify the validation in get_frame_sync_mode method.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_control_panel_enhanced import get_nvidia_control_panel

def test_validation():
    panel = get_nvidia_control_panel()

    print("Testing validation for get_frame_sync_mode...")

    # Test 1: Valid input should work
    try:
        result = panel.get_frame_sync_mode(0)
        print(f"✓ Valid input (0): {result}")
    except Exception as e:
        print(f"✗ Valid input failed: {e}")

    # Test 2: Non-integer should raise TypeError
    try:
        result = panel.get_frame_sync_mode("invalid")
        print(f"✗ Non-integer should have failed but returned: {result}")
    except TypeError as e:
        print(f"✓ Non-integer properly rejected: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Test 3: Negative index should raise ValueError
    try:
        result = panel.get_frame_sync_mode(-1)
        print(f"✗ Negative index should have failed but returned: {result}")
    except ValueError as e:
        print(f"✓ Negative index properly rejected: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Test 4: Out of range index should raise ValueError
    try:
        result = panel.get_frame_sync_mode(999)
        print(f"✗ Out of range index should have failed but returned: {result}")
    except ValueError as e:
        print(f"✓ Out of range index properly rejected: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    test_validation()
