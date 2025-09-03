"""Test script for NVIDIA Control Panel Workstation Features

This script tests the workstation-specific features including:
- Frame Synchronisation
- SDI Output Configuration
- Edge Overlap Adjustment
- NVIDIA Mosaic
- SDI Capture Configuration
- EDID Management
- Multi-Display Cloning
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_control_panel_enhanced import (
    NVIDIAControlPanel,
    FrameSyncMode,
    SDIOutputConfig,
    SDIOutputFormat,
    EdgeOverlapConfig,
    SDICaptureConfig
)

def test_frame_sync_features():
    """Test Frame Synchronisation features."""
    print("Testing Frame Synchronisation Features")
    print("=" * 50)
    
    ncp = NVIDIAControlPanel()
    
    # Test getting frame sync mode
    try:
        mode = ncp.get_frame_sync_mode()
        print(f"Current Frame Sync Mode: {mode}")
        print("✓ Frame sync mode retrieval successful")
    except Exception as e:
        print(f"✗ Frame sync mode retrieval failed: {e}")
        return False
    
    # Test setting frame sync mode
    try:
        for test_mode in [FrameSyncMode.OFF, FrameSyncMode.ON, FrameSyncMode.MASTER, FrameSyncMode.SLAVE]:
            success = ncp.set_frame_sync_mode(test_mode)
            if success:
                print(f"✓ Frame sync mode set to {test_mode} successfully")
            else:
                print(f"✗ Failed to set frame sync mode to {test_mode}")
                return False
    except Exception as e:
        print(f"✗ Frame sync mode setting failed: {e}")
        return False
    
    print()
    return True

def test_sdi_output_features():
    """Test SDI Output features."""
    print("Testing SDI Output Features")
    print("=" * 50)
    
    ncp = NVIDIAControlPanel()
    
    # Test getting SDI output config
    try:
        config = ncp.get_sdi_output_config()
        print(f"Current SDI Output Config: {config}")
        print("✓ SDI output config retrieval successful")
    except Exception as e:
        print(f"✗ SDI output config retrieval failed: {e}")
        return False
    
    # Test setting SDI output config
    try:
        test_configs = [
            SDIOutputConfig(enabled=True, format=SDIOutputFormat.SDI_8BIT, stream_count=1),
            SDIOutputConfig(enabled=True, format=SDIOutputFormat.SDI_10BIT, stream_count=2),
            SDIOutputConfig(enabled=False, format=SDIOutputFormat.SDI_12BIT, stream_count=1)
        ]
        
        for config in test_configs:
            success = ncp.set_sdi_output_config(config)
            if success:
                print(f"✓ SDI output config set successfully: {config}")
            else:
                print(f"✗ Failed to set SDI output config: {config}")
                return False
    except Exception as e:
        print(f"✗ SDI output config setting failed: {e}")
        return False
    
    print()
    return True

def test_edge_overlap_features():
    """Test Edge Overlap Adjustment features."""
    print("Testing Edge Overlap Adjustment Features")
    print("=" * 50)
    
    ncp = NVIDIAControlPanel()
    
    # Test getting edge overlap config
    try:
        config = ncp.get_edge_overlap_config()
        print(f"Current Edge Overlap Config: {config}")
        print("✓ Edge overlap config retrieval successful")
    except Exception as e:
        print(f"✗ Edge overlap config retrieval failed: {e}")
        return False
    
    # Test setting edge overlap config
    try:
        test_configs = [
            EdgeOverlapConfig(enabled=True, overlap_pixels=5, display_index=0),
            EdgeOverlapConfig(enabled=False, overlap_pixels=0, display_index=0),
            EdgeOverlapConfig(enabled=True, overlap_pixels=10, display_index=1)
        ]
        
        for config in test_configs:
            success = ncp.set_edge_overlap_config(config)
            if success:
                print(f"✓ Edge overlap config set successfully: {config}")
            else:
                print(f"✗ Failed to set edge overlap config: {config}")
                return False
    except Exception as e:
        print(f"✗ Edge overlap config setting failed: {e}")
        return False
    
    print()
    return True

def test_mosaic_features():
    """Test NVIDIA Mosaic features."""
    print("Testing NVIDIA Mosaic Features")
    print("=" * 50)
    
    ncp = NVIDIAControlPanel()
    
    # Test enabling Mosaic
    try:
        success = ncp.enable_mosaic(True)
        if success:
            print("✓ NVIDIA Mosaic enabled successfully")
        else:
            print("✗ Failed to enable NVIDIA Mosaic")
            return False
    except Exception as e:
        print(f"✗ Mosaic enable failed: {e}")
        return False
    
    # Test disabling Mosaic
    try:
        success = ncp.enable_mosaic(False)
        if success:
            print("✓ NVIDIA Mosaic disabled successfully")
        else:
            print("✗ Failed to disable NVIDIA Mosaic")
            return False
    except Exception as e:
        print(f"✗ Mosaic disable failed: {e}")
        return False
    
    print()
    return True

def test_sdi_capture_features():
    """Test SDI Capture features."""
    print("Testing SDI Capture Features")
    print("=" * 50)
    
    ncp = NVIDIAControlPanel()
    
    # Test getting SDI capture config
    try:
        config = ncp.get_sdi_capture_config()
        print(f"Current SDI Capture Config: {config}")
        print("✓ SDI capture config retrieval successful")
    except Exception as e:
        print(f"✗ SDI capture config retrieval failed: {e}")
        return False
    
    # Test setting SDI capture config
    try:
        test_configs = [
            SDICaptureConfig(enabled=True, stream_count=1, buffer_size_mb=256),
            SDICaptureConfig(enabled=True, stream_count=2, buffer_size_mb=512),
            SDICaptureConfig(enabled=False, stream_count=1, buffer_size_mb=128)
        ]
        
        for config in test_configs:
            success = ncp.set_sdi_capture_config(config)
            if success:
                print(f"✓ SDI capture config set successfully: {config}")
            else:
                print(f"✗ Failed to set SDI capture config: {config}")
                return False
    except Exception as e:
        print(f"✗ SDI capture config setting failed: {e}")
        return False
    
    print()
    return True

def test_edid_features():
    """Test EDID Management features."""
    print("Testing EDID Management Features")
    print("=" * 50)
    
    ncp = NVIDIAControlPanel()
    
    # Test reading EDID
    try:
        edid_data = ncp.read_edid()
        print(f"EDID Data: {edid_data}")
        print("✓ EDID read successful")
    except Exception as e:
        print(f"✗ EDID read failed: {e}")
        return False
    
    # Test applying EDID (simulated with dummy data)
    try:
        # Create dummy EDID data for testing
        dummy_edid = b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00\x10\xAC\x00\x00\x00\x00\x00\x00' + \
                     b'\x00\x15\x01\x03\x80\x00\x00\x78\x0A\xEE\x91\xA3\x54\x4C\x99\x26' + \
                     b'\x0F\x50\x54\x00\x00\x00\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                     b'\x01\x01\x01\x01\x01\x01\x00\x00\x00\xFC\x00\x44\x45\x4C\x4C\x20' + \
                     b'\x55\x32\x34\x31\x35\x0A\x20\x20\x00\x00\x00\xFD\x00\x38\x4C\x1E' + \
                     b'\x51\x0E\x00\x0A\x20\x20\x20\x20\x20\x20\x00\x00\x00\x10\x00\x00' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        success = ncp.apply_edid(dummy_edid)
        if success:
            print("✓ EDID applied successfully")
        else:
            print("✗ Failed to apply EDID")
            return False
    except Exception as e:
        print(f"✗ EDID apply failed: {e}")
        return False
    
    print()
    return True

def test_multi_display_cloning():
    """Test Multi-Display Cloning features."""
    print("Testing Multi-Display Cloning Features")
    print("=" * 50)
    
    ncp = NVIDIAControlPanel()
    
    # Test enabling multi-display cloning
    try:
        success = ncp.enable_multi_display_cloning(True)
        if success:
            print("✓ Multi-display cloning enabled successfully")
        else:
            print("✗ Failed to enable multi-display cloning")
            return False
    except Exception as e:
        print(f"✗ Multi-display cloning enable failed: {e}")
        return False
    
    # Test disabling multi-display cloning
    try:
        success = ncp.enable_multi_display_cloning(False)
        if success:
            print("✓ Multi-display cloning disabled successfully")
        else:
            print("✗ Failed to disable multi-display cloning")
            return False
    except Exception as e:
        print(f"✗ Multi-display cloning disable failed: {e}")
        return False
    
    print()
    return True

def test_comprehensive_workstation_scenario():
    """Test a comprehensive workstation scenario."""
    print("Testing Comprehensive Workstation Scenario")
    print("=" * 50)
    
    ncp = NVIDIAControlPanel()
    
    # Simulate a professional workstation setup
    print("Setting up professional workstation configuration...")
    
    try:
        # Configure frame sync as master
        ncp.set_frame_sync_mode(FrameSyncMode.MASTER)
        
        # Configure SDI output for professional video
        sdi_config = SDIOutputConfig(
            enabled=True,
            format=SDIOutputFormat.SDI_10BIT,
            stream_count=2
        )
        ncp.set_sdi_output_config(sdi_config)
        
        # Configure edge overlap for multi-display setup
        edge_config = EdgeOverlapConfig(
            enabled=True,
            overlap_pixels=8,
            display_index=0
        )
        ncp.set_edge_overlap_config(edge_config)
        
        # Enable Mosaic for unified desktop
        ncp.enable_mosaic(True)
        
        # Configure SDI capture
        capture_config = SDICaptureConfig(
            enabled=True,
            stream_count=1,
            buffer_size_mb=512
        )
        ncp.set_sdi_capture_config(capture_config)
        
        # Enable multi-display cloning
        ncp.enable_multi_display_cloning(True)
        
        print("✓ Comprehensive workstation configuration applied successfully")
        print("Workstation features configured:")
        print(f"  - Frame Sync: {FrameSyncMode.MASTER}")
        print(f"  - SDI Output: {sdi_config}")
        print(f"  - Edge Overlap: {edge_config}")
        print(f"  - Mosaic: Enabled")
        print(f"  - SDI Capture: {capture_config}")
        print(f"  - Multi-Display Cloning: Enabled")
        
    except Exception as e:
        print(f"✗ Comprehensive workstation configuration failed: {e}")
        return False
    
    print()
    return True

def main():
    """Run all workstation feature tests."""
    print("NVIDIA Control Panel Workstation Features Test Suite")
    print("=" * 60)
    print()
    
    test_results = {}
    
    # Run individual feature tests
    test_results['frame_sync'] = test_frame_sync_features()
    test_results['sdi_output'] = test_sdi_output_features()
    test_results['edge_overlap'] = test_edge_overlap_features()
    test_results['mosaic'] = test_mosaic_features()
    test_results['sdi_capture'] = test_sdi_capture_features()
    test_results['edid'] = test_edid_features()
    test_results['multi_display'] = test_multi_display_cloning()
    test_results['comprehensive'] = test_comprehensive_workstation_scenario()
    
    # Print summary
    print("Test Results Summary")
    print("=" * 30)
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} : {status}")
    
    print()
    print(f"Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All workstation feature tests completed successfully!")
        return 0
    else:
        print("❌ Some workstation feature tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
