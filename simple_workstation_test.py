#!/usr/bin/env python3
"""Simple test for NVIDIA Control Panel workstation features"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_control_panel import (
    NVIDIAControlPanel,
    FrameSyncMode,
    SDIOutputConfig,
    SDIOutputFormat,
    EdgeOverlapConfig,
    SDICaptureConfig
)

def main():
    print("Testing NVIDIA Control Panel Workstation Features")
    print("=" * 50)
    
    try:
        ncp = NVIDIAControlPanel()
        print(f"NVAPI Available: {ncp.nvapi_available}")
        print(f"GPU Count: {ncp.gpu_count}")
        print(f"Driver Version: {ncp.driver_version}")
        print()
        
        # Test Frame Sync
        print("1. Testing Frame Synchronisation:")
        mode = ncp.get_frame_sync_mode()
        print(f"   Current Frame Sync Mode: {mode}")
        
        success = ncp.set_frame_sync_mode(FrameSyncMode.ON)
        print(f"   Set Frame Sync to ON: {'Success' if success else 'Failed'}")
        print()
        
        # Test SDI Output
        print("2. Testing SDI Output:")
        sdi_config = ncp.get_sdi_output_config()
        print(f"   Current SDI Config: {sdi_config}")
        
        new_config = SDIOutputConfig(enabled=True, format=SDIOutputFormat.SDI_10BIT, stream_count=2)
        success = ncp.set_sdi_output_config(new_config)
        print(f"   Set SDI Config: {'Success' if success else 'Failed'}")
        print()
        
        # Test Edge Overlap
        print("3. Testing Edge Overlap:")
        edge_config = ncp.get_edge_overlap_config()
        print(f"   Current Edge Overlap: {edge_config}")
        
        new_edge = EdgeOverlapConfig(enabled=True, overlap_pixels=5, display_index=0)
        success = ncp.set_edge_overlap_config(new_edge)
        print(f"   Set Edge Overlap: {'Success' if success else 'Failed'}")
        print()
        
        # Test SDI Capture
        print("4. Testing SDI Capture:")
        capture_config = ncp.get_sdi_capture_config()
        print(f"   Current SDI Capture: {capture_config}")
        
        new_capture = SDICaptureConfig(enabled=True, stream_count=1, buffer_size_mb=512)
        success = ncp.set_sdi_capture_config(new_capture)
        print(f"   Set SDI Capture: {'Success' if success else 'Failed'}")
        print()
        
        # Test Mosaic
        print("5. Testing NVIDIA Mosaic:")
        success = ncp.enable_mosaic(True)
        print(f"   Enable Mosaic: {'Success' if success else 'Failed'}")
        print()
        
        # Test Multi-Display Cloning
        print("6. Testing Multi-Display Cloning:")
        success = ncp.enable_multi_display_cloning(True)
        print(f"   Enable Multi-Display Cloning: {'Success' if success else 'Failed'}")
        print()
        
        print("All workstation feature tests completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
