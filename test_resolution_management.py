#!/usr/bin/env python3
"""
Test script for NVIDIA Control Panel resolution management functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_control_panel import NVIDIAControlPanel, CustomResolution

def test_resolution_management():
    """Test the resolution management functionality."""
    print("Testing NVIDIA Control Panel Resolution Management")
    print("=" * 50)
    
    # Initialize the control panel
    ncp = NVIDIAControlPanel()
    
    print(f"GPUs detected: {ncp.gpu_count}")
    print(f"Driver version: {ncp.driver_version}")
    print(f"NVAPI available: {ncp.nvapi_available}")
    print()
    
    # Test getting current resolutions
    print("1. Getting current available resolutions...")
    resolutions = ncp.get_current_resolutions()
    print(f"Available resolutions: {len(resolutions)} found")
    for i, res in enumerate(resolutions[:5]):  # Show first 5
        print(f"  {i+1}. {res['width']}x{res['height']} @ {res['refresh_rate']}Hz")
    if len(resolutions) > 5:
        print(f"  ... and {len(resolutions) - 5} more")
    print()
    
    # Test creating a custom resolution
    print("2. Creating a custom resolution...")
    try:
        custom_res = CustomResolution(
            width=2560,
            height=1440,
            refresh_rate=75,
            color_depth=32,
            scaling="No scaling",
            timing_standard="CVT",
            name="Custom_2560x1440_75Hz"
        )
        print(f"Created custom resolution: {custom_res.name}")
        print(f"  Resolution: {custom_res.width}x{custom_res.height}")
        print(f"  Refresh rate: {custom_res.refresh_rate}Hz")
        print(f"  Color depth: {custom_res.color_depth} bits")
        print()
        
        # Test adding the custom resolution
        print("3. Adding custom resolution to NVIDIA Control Panel...")
        result = ncp.add_custom_resolution(custom_res)
        print(f"Result: {result}")
        print()
        
        # Test applying the custom resolution
        print("4. Applying custom resolution...")
        result = ncp.apply_custom_resolution(custom_res)
        print(f"Result: {result}")
        print()
        
        # Test removing the custom resolution
        print("5. Removing custom resolution...")
        result = ncp.remove_custom_resolution(custom_res.name)
        print(f"Result: {result}")
        print()
        
    except Exception as e:
        print(f"Error during resolution testing: {e}")
        print("This is expected if NVIDIA drivers are not installed or running on non-Windows system")
        print()
    
    # Test error handling with invalid resolution
    print("6. Testing error handling with invalid resolution...")
    try:
        invalid_res = CustomResolution(
            width=100,  # Too small
            height=100,  # Too small
            refresh_rate=10,  # Too low
            name="Invalid_Test"
        )
    except ValueError as e:
        print(f"Correctly caught validation error: {e}")
    print()
    
    print("Resolution management test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_resolution_management()
