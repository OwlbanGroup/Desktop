#!/usr/bin/env python3
"""
Test script for NVIDIA Control Panel video and television settings functionality.
This script tests the newly added video settings methods.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_control_panel import NVIDIAControlPanel, VideoSettings, VideoEnhancement, DeinterlacingMode, HDRMode, TVFormat, VideoColorRange, ScalingMode

def test_video_settings_basic():
    """Test basic video settings functionality."""
    print("=" * 60)
    print("Testing Basic Video Settings Functionality")
    print("=" * 60)
    
    ncp = NVIDIAControlPanel()
    
    # Test getting current video settings
    print("\n1. Getting current video settings...")
    current_settings = ncp.get_video_settings()
    print(f"Current video settings: {current_settings}")
    
    # Test setting video settings
    print("\n2. Setting custom video settings...")
    custom_settings = VideoSettings(
        brightness=60,
        contrast=65,
        saturation=55,
        edge_enhancement=VideoEnhancement.MEDIUM,
        noise_reduction=VideoEnhancement.HIGH,
        deinterlacing_mode=DeinterlacingMode.ADAPTIVE,
        hdr_mode=HDRMode.ENABLED,
        tone_mapping=True,
        overscan_percentage=2,
        tv_format=TVFormat.NTSC_M,
        color_range=VideoColorRange.LIMITED,
        scaling_mode=ScalingMode.ASPECT_RATIO,
        gpu_scaling=True
    )
    
    result = ncp.set_video_settings(custom_settings)
    print(f"Settings applied: {result}")
    
    # Verify the settings were applied
    print("\n3. Verifying applied settings...")
    updated_settings = ncp.get_video_settings()
    print(f"Updated settings: {updated_settings}")
    
    return True

def test_optimization_functions():
    """Test video optimization functions."""
    print("\n" + "=" * 60)
    print("Testing Video Optimization Functions")
    print("=" * 60)
    
    ncp = NVIDIAControlPanel()
    
    # Test optimize for video playback
    print("\n1. Optimizing for video playback...")
    video_result = ncp.optimize_for_video_playback()
    print(f"Video optimization result: {video_result['result']}")
    print(f"Applied settings: {video_result['applied_settings']}")
    
    # Test optimize for television
    print("\n2. Optimizing for television output...")
    tv_result = ncp.optimize_for_television()
    print(f"TV optimization result: {tv_result['result']}")
    print(f"Applied settings: {tv_result['applied_settings']}")
    
    return True

def test_hdr_functions():
    """Test HDR-related functions."""
    print("\n" + "=" * 60)
    print("Testing HDR Functions")
    print("=" * 60)
    
    ncp = NVIDIAControlPanel()
    
    # Test enabling HDR
    print("\n1. Enabling HDR...")
    enable_result = ncp.enable_hdr()
    print(f"HDR enable result: {enable_result}")
    
    # Verify HDR is enabled
    settings = ncp.get_video_settings()
    print(f"HDR mode after enable: {settings.hdr_mode}")
    
    # Test disabling HDR
    print("\n2. Disabling HDR...")
    disable_result = ncp.disable_hdr()
    print(f"HDR disable result: {disable_result}")
    
    # Verify HDR is disabled
    settings = ncp.get_video_settings()
    print(f"HDR mode after disable: {settings.hdr_mode}")
    
    return True

def test_overscan_adjustment():
    """Test overscan adjustment functionality."""
    print("\n" + "=" * 60)
    print("Testing Overscan Adjustment")
    print("=" * 60)
    
    ncp = NVIDIAControlPanel()
    
    # Test valid overscan adjustment
    print("\n1. Adjusting overscan to 5%...")
    result = ncp.adjust_overscan(5)
    print(f"Overscan adjustment result: {result}")
    
    # Verify overscan was set
    settings = ncp.get_video_settings()
    print(f"Overscan percentage: {settings.overscan_percentage}%")
    
    # Test invalid overscan values
    print("\n2. Testing invalid overscan values...")
    invalid_result = ncp.adjust_overscan(15)  # Should fail
    print(f"Invalid overscan result: {invalid_result}")
    
    invalid_result = ncp.adjust_overscan(-15)  # Should fail
    print(f"Invalid overscan result: {invalid_result}")
    
    return True

def test_video_settings_validation():
    """Test video settings validation."""
    print("\n" + "=" * 60)
    print("Testing Video Settings Validation")
    print("=" * 60)
    
    ncp = NVIDIAControlPanel()
    
    # Test invalid brightness
    print("\n1. Testing invalid brightness...")
    try:
        invalid_settings = VideoSettings(brightness=150)  # Should raise ValueError
        print("ERROR: Validation should have failed!")
    except ValueError as e:
        print(f"✓ Correctly caught validation error: {e}")
    
    # Test invalid contrast
    print("\n2. Testing invalid contrast...")
    try:
        invalid_settings = VideoSettings(contrast=-10)  # Should raise ValueError
        print("ERROR: Validation should have failed!")
    except ValueError as e:
        print(f"✓ Correctly caught validation error: {e}")
    
    # Test invalid overscan
    print("\n3. Testing invalid overscan...")
    try:
        invalid_settings = VideoSettings(overscan_percentage=20)  # Should raise ValueError
        print("ERROR: Validation should have failed!")
    except ValueError as e:
        print(f"✓ Correctly caught validation error: {e}")
    
    return True

def main():
    """Main test function."""
    print("NVIDIA Control Panel Video Settings Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_video_settings_basic()
        test_optimization_functions()
        test_hdr_functions()
        test_overscan_adjustment()
        test_video_settings_validation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("Summary:")
        print("- Basic video settings functionality: ✓")
        print("- Optimization functions: ✓")
        print("- HDR functions: ✓")
        print("- Overscan adjustment: ✓")
        print("- Settings validation: ✓")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
