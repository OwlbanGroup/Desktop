#!/usr/bin/env python3
"""
Advanced test for NVIDIA Control Panel resolution management functionality.
Tests edge cases, multi-display support, and advanced settings.
"""

import sys
import os
import logging
from datetime import datetime

# Set up logging to file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='advanced_resolution_test.log',
    filemode='w'
)

def test_advanced_scenarios():
    """Test advanced resolution management scenarios."""
    print("Starting advanced resolution management test...")
    logging.info("Starting advanced resolution management test")
    
    try:
        # Import and initialize
        from nvidia_control_panel import NVIDIAControlPanel, CustomResolution
        
        ncp = NVIDIAControlPanel()
        logging.info(f"NVIDIA Control Panel initialized: GPUs={ncp.gpu_count}, Driver={ncp.driver_version}, NVAPI={ncp.nvapi_available}")
        
        # Test 1: Multiple display support
        logging.info("Test 1: Testing multi-display support")
        for display_index in range(3):  # Test up to 3 displays
            try:
                resolutions = ncp.get_current_resolutions(display_index)
                logging.info(f"Display {display_index}: {len(resolutions)} resolutions found")
            except Exception as e:
                logging.warning(f"Display {display_index}: {e}")
        
        # Test 2: Edge case resolutions
        logging.info("Test 2: Testing edge case resolutions")
        edge_cases = [
            # Minimum valid resolution
            {"width": 640, "height": 480, "refresh_rate": 24, "name": "Min_640x480_24Hz"},
            # Maximum valid resolution
            {"width": 7680, "height": 4320, "refresh_rate": 240, "name": "Max_8K_240Hz"},
            # Common high refresh rates
            {"width": 1920, "height": 1080, "refresh_rate": 144, "name": "1080p_144Hz"},
            {"width": 2560, "height": 1440, "refresh_rate": 165, "name": "1440p_165Hz"},
        ]
        
        for case in edge_cases:
            try:
                res = CustomResolution(**case)
                logging.info(f"Created edge case: {res.name}")
                
                # Test adding
                result = ncp.add_custom_resolution(res)
                logging.info(f"Added {res.name}: {result}")
                
                # Test applying
                result = ncp.apply_custom_resolution(res)
                logging.info(f"Applied {res.name}: {result}")
                
                # Test removing
                result = ncp.remove_custom_resolution(res.name)
                logging.info(f"Removed {res.name}: {result}")
                
            except Exception as e:
                logging.error(f"Edge case {case.get('name', 'unknown')} failed: {e}")
        
        # Test 3: Different color depths and timing standards
        logging.info("Test 3: Testing color depths and timing standards")
        variations = [
            {"color_depth": 8, "timing_standard": "CVT", "name": "8bit_CVT"},
            {"color_depth": 16, "timing_standard": "CVT-RB", "name": "16bit_CVT-RB"},
            {"color_depth": 24, "timing_standard": "GTF", "name": "24bit_GTF"},
            {"color_depth": 32, "timing_standard": "Manual", "name": "32bit_Manual"},
        ]
        
        base_res = {"width": 1920, "height": 1080, "refresh_rate": 60}
        
        for variation in variations:
            try:
                params = {**base_res, **variation}
                res = CustomResolution(**params)
                logging.info(f"Created variation: {res.name}")
                
                result = ncp.add_custom_resolution(res)
                logging.info(f"Added variation {res.name}: {result}")
                
                result = ncp.remove_custom_resolution(res.name)
                logging.info(f"Removed variation {res.name}: {result}")
                
            except Exception as e:
                logging.error(f"Variation {variation['name']} failed: {e}")
        
        # Test 4: Error handling with extreme values
        logging.info("Test 4: Testing extreme value error handling")
        extreme_cases = [
            {"width": 639, "height": 480, "refresh_rate": 60, "name": "Too_Narrow"},
            {"width": 640, "height": 479, "refresh_rate": 60, "name": "Too_Short"},
            {"width": 7681, "height": 4320, "refresh_rate": 60, "name": "Too_Wide"},
            {"width": 7680, "height": 4321, "refresh_rate": 60, "name": "Too_Tall"},
            {"width": 1920, "height": 1080, "refresh_rate": 23, "name": "Refresh_Too_Low"},
            {"width": 1920, "height": 1080, "refresh_rate": 241, "name": "Refresh_Too_High"},
            {"width": 1920, "height": 1080, "refresh_rate": 60, "color_depth": 7, "name": "Invalid_Color_Depth"},
        ]
        
        for case in extreme_cases:
            try:
                res = CustomResolution(**case)
                logging.error(f"ERROR: Should have rejected {case['name']} but didn't!")
            except ValueError as e:
                logging.info(f"Correctly rejected {case['name']}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error with {case['name']}: {e}")
        
        # Test 5: Bulk operations
        logging.info("Test 5: Testing bulk operations")
        bulk_resolutions = [
            {"width": 1280, "height": 720, "refresh_rate": 75, "name": "Bulk_720p_75Hz"},
            {"width": 1366, "height": 768, "refresh_rate": 60, "name": "Bulk_768p_60Hz"},
            {"width": 1600, "height": 900, "refresh_rate": 90, "name": "Bulk_900p_90Hz"},
        ]
        
        # Add all
        for case in bulk_resolutions:
            try:
                res = CustomResolution(**case)
                result = ncp.add_custom_resolution(res)
                logging.info(f"Bulk added {res.name}: {result}")
            except Exception as e:
                logging.error(f"Bulk add failed for {case['name']}: {e}")
        
        # Remove all
        for case in bulk_resolutions:
            try:
                result = ncp.remove_custom_resolution(case["name"])
                logging.info(f"Bulk removed {case['name']}: {result}")
            except Exception as e:
                logging.error(f"Bulk remove failed for {case['name']}: {e}")
        
        # Test 6: Cleanup and resource management
        logging.info("Test 6: Testing cleanup functionality")
        try:
            ncp.cleanup()
            logging.info("Cleanup completed successfully")
        except Exception as e:
            logging.error(f"Cleanup failed: {e}")
        
        logging.info("All advanced tests completed successfully!")
        print("Advanced tests completed! Check advanced_resolution_test.log for details.")
        
    except Exception as e:
        logging.error(f"Advanced test failed with error: {e}")
        print(f"Advanced test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_advanced_scenarios()
    sys.exit(0 if success else 1)
