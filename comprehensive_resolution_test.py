#!/usr/bin/env python3
"""
Comprehensive test for NVIDIA Control Panel resolution management functionality.
This test writes results to a file for better visibility.
"""

import sys
import os
import logging
from datetime import datetime

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='resolution_test.log',
    filemode='w'
)

def test_resolution_management():
    """Test the resolution management functionality."""
    print("Starting comprehensive resolution management test...")
    logging.info("Starting comprehensive resolution management test")
    
    try:
        # Import and initialize
        from nvidia_control_panel import NVIDIAControlPanel, CustomResolution
        
        ncp = NVIDIAControlPanel()
        logging.info(f"NVIDIA Control Panel initialized: GPUs={ncp.gpu_count}, Driver={ncp.driver_version}, NVAPI={ncp.nvapi_available}")
        
        # Test 1: Get current resolutions
        logging.info("Test 1: Getting current resolutions")
        resolutions = ncp.get_current_resolutions()
        logging.info(f"Found {len(resolutions)} available resolutions")
        
        for i, res in enumerate(resolutions):
            logging.info(f"Resolution {i+1}: {res['width']}x{res['height']} @ {res['refresh_rate']}Hz")
        
        # Test 2: Create and validate custom resolution
        logging.info("Test 2: Creating custom resolution")
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
            logging.info(f"Custom resolution created: {custom_res.name}")
        except Exception as e:
            logging.error(f"Failed to create custom resolution: {e}")
        
        # Test 3: Add custom resolution
        logging.info("Test 3: Adding custom resolution")
        try:
            result = ncp.add_custom_resolution(custom_res)
            logging.info(f"Add result: {result}")
        except Exception as e:
            logging.error(f"Failed to add custom resolution: {e}")
        
        # Test 4: Apply custom resolution
        logging.info("Test 4: Applying custom resolution")
        try:
            result = ncp.apply_custom_resolution(custom_res)
            logging.info(f"Apply result: {result}")
        except Exception as e:
            logging.error(f"Failed to apply custom resolution: {e}")
        
        # Test 5: Remove custom resolution
        logging.info("Test 5: Removing custom resolution")
        try:
            result = ncp.remove_custom_resolution(custom_res.name)
            logging.info(f"Remove result: {result}")
        except Exception as e:
            logging.error(f"Failed to remove custom resolution: {e}")
        
        # Test 6: Error handling
        logging.info("Test 6: Testing error handling")
        try:
            invalid_res = CustomResolution(
                width=100,  # Too small
                height=100,  # Too small
                refresh_rate=10,  # Too low
                name="Invalid_Test"
            )
            logging.error("ERROR: Invalid resolution should have been rejected!")
        except ValueError as e:
            logging.info(f"Correctly caught validation error: {e}")
        
        logging.info("All tests completed successfully!")
        print("All tests completed! Check resolution_test.log for details.")
        
    except Exception as e:
        logging.error(f"Test failed with error: {e}")
        print(f"Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_resolution_management()
    sys.exit(0 if success else 1)
