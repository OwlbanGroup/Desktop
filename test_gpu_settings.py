#!/usr/bin/env python3
"""
Simple test script for NVIDIA Control Panel GPU settings
"""

import nvidia_control_panel_enhanced

def test_gpu_settings():
    print("Testing NVIDIA Control Panel GPU Settings...")
    print("=" * 50)
    
    try:
        # Create NVIDIA Control Panel instance
        ncp = nvidia_control_panel_enhanced.NVIDIAControlPanel()
        print(f"GPU Count: {ncp.gpu_count}")
        print(f"Driver Version: {ncp.driver_version}")
        print(f"NVAPI Available: {ncp.nvapi_available}")
        print()
        
        # Test getting GPU settings
        print("Getting GPU settings...")
        settings = ncp.get_gpu_settings()
        
        print("Current GPU Settings:")
        print("-" * 30)
        for key, value in settings.items():
            print(f"  {key}: {value}")
            
        print()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gpu_settings()
