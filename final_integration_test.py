#!/usr/bin/env python3
"""
Final integration test for NVIDIA Control Panel with resolution management.
Tests the complete functionality including GPU settings and resolution management.
"""

import sys
import os
import logging
from datetime import datetime

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='final_integration_test.log',
    filemode='w'
)

def test_complete_integration():
    """Test complete NVIDIA Control Panel integration."""
    print("Starting final integration test...")
    logging.info("Starting final integration test")
    
    try:
        # Import and initialize
        from nvidia_control_panel import NVIDIAControlPanel, CustomResolution
        
        ncp = NVIDIAControlPanel()
        logging.info(f"System: GPUs={ncp.gpu_count}, Driver={ncp.driver_version}, NVAPI={ncp.nvapi_available}")
        
        # Test 1: Basic GPU functionality
        logging.info("Test 1: Basic GPU functionality")
        settings = ncp.get_gpu_settings()
        logging.info(f"GPU Settings: {settings}")
        
        # Test 2: Optimization profiles
        logging.info("Test 2: Optimization profiles")
        
        # AI optimization
        ai_result = ncp.optimize_for_ai_workload()
        logging.info(f"AI Optimization: {ai_result['result']}")
        
        # Gaming optimization
        gaming_result = ncp.optimize_for_gaming()
        logging.info(f"Gaming Optimization: {gaming_result['result']}")
        
        # Power saving optimization
        power_result = ncp.optimize_for_power_saving()
        logging.info(f"Power Saving Optimization: {power_result['result']}")
        
        # Test 3: Resolution management
        logging.info("Test 3: Resolution management")
        
        # Get current resolutions
        resolutions = ncp.get_current_resolutions()
        logging.info(f"Available resolutions: {len(resolutions)}")
        for res in resolutions:
            logging.info(f"  {res['width']}x{res['height']} @ {res['refresh_rate']}Hz")
        
        # Create and manage custom resolutions
        custom_resolutions = [
            CustomResolution(1920, 1080, 120, name="1080p_120Hz"),
            CustomResolution(2560, 1440, 144, name="1440p_144Hz"),
            CustomResolution(3840, 2160, 60, name="4K_60Hz")
        ]
        
        for res in custom_resolutions:
            try:
                # Add
                add_result = ncp.add_custom_resolution(res)
                logging.info(f"Added {res.name}: {add_result}")
                
                # Apply
                apply_result = ncp.apply_custom_resolution(res)
                logging.info(f"Applied {res.name}: {apply_result}")
                
                # Remove
                remove_result = ncp.remove_custom_resolution(res.name)
                logging.info(f"Removed {res.name}: {remove_result}")
                
            except Exception as e:
                logging.error(f"Failed to manage {res.name}: {e}")
        
        # Test 4: Multi-display support
        logging.info("Test 4: Multi-display support")
        for display_idx in range(3):
            try:
                display_res = ncp.get_current_resolutions(display_idx)
                logging.info(f"Display {display_idx}: {len(display_res)} resolutions")
            except Exception as e:
                logging.warning(f"Display {display_idx}: {e}")
        
        # Test 5: Error handling and validation
        logging.info("Test 5: Error handling")
        
        # Test invalid resolutions
        invalid_cases = [
            {"width": 100, "height": 100, "refresh_rate": 10, "name": "Invalid_Small"},
            {"width": 10000, "height": 10000, "refresh_rate": 300, "name": "Invalid_Large"}
        ]
        
        for case in invalid_cases:
            try:
                res = CustomResolution(**case)
                logging.error(f"ERROR: Should have rejected {case['name']}")
            except ValueError as e:
                logging.info(f"Correctly rejected {case['name']}: {e}")
        
        # Test 6: Cleanup
        logging.info("Test 6: Cleanup")
        ncp.cleanup()
        logging.info("Cleanup completed successfully")
        
        # Test 7: Singleton pattern
        logging.info("Test 7: Singleton pattern")
        from nvidia_control_panel import get_nvidia_control_panel
        ncp2 = get_nvidia_control_panel()
        ncp3 = get_nvidia_control_panel()
        logging.info(f"Singleton instances match: {ncp2 is ncp3}")
        
        logging.info("Final integration test completed successfully!")
        print("Final integration test completed! Check final_integration_test.log for details.")
        
        return True
        
    except Exception as e:
        logging.error(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_integration()
    sys.exit(0 if success else 1)
