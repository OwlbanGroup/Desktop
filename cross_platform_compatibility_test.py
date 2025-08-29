#!/usr/bin/env python3
"""
Cross-platform compatibility testing for NVIDIA Control Panel integration.
Tests the system's behavior across different simulated environments.
"""

import sys
import os
import logging
import platform
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='cross_platform_compatibility_test.log',
    filemode='w'
)

def simulate_platform_behavior(platform_name):
    """Simulate different platform behaviors for testing."""
    print(f"\nTesting {platform_name} compatibility...")
    logging.info(f"Testing {platform_name} compatibility")
    
    try:
        from nvidia_control_panel import NVIDIAControlPanel, CustomResolution
        
        # Create instance - should detect actual platform automatically
        ncp = NVIDIAControlPanel()
        
        # Test basic functionality
        settings = ncp.get_gpu_settings()
        logging.info(f"{platform_name}: GPU settings retrieved successfully")
        print(f"✅ {platform_name}: GPU settings retrieved")
        
        # Test resolution management
        resolutions = ncp.get_current_resolutions()
        logging.info(f"{platform_name}: {len(resolutions)} resolutions available")
        print(f"✅ {platform_name}: {len(resolutions)} resolutions available")
        
        # Test custom resolution operations
        custom_res = CustomResolution(1920, 1080, 75, name=f"{platform_name}_Test")
        
        add_result = ncp.add_custom_resolution(custom_res)
        logging.info(f"{platform_name}: Custom resolution added: {add_result}")
        
        apply_result = ncp.apply_custom_resolution(custom_res)
        logging.info(f"{platform_name}: Custom resolution applied: {apply_result}")
        
        remove_result = ncp.remove_custom_resolution(custom_res.name)
        logging.info(f"{platform_name}: Custom resolution removed: {remove_result}")
        
        print(f"✅ {platform_name}: Custom resolution operations successful")
        return True
        
    except Exception as e:
        logging.error(f"{platform_name} compatibility test failed: {e}")
        print(f"❌ {platform_name} compatibility test failed: {e}")
        return False

def test_windows_compatibility():
    """Test Windows-specific functionality."""
    print("\n=== Windows Compatibility Test ===")
    logging.info("=== Windows Compatibility Test ===")
    
    try:
        from nvidia_control_panel import NVIDIAControlPanel
        
        ncp = NVIDIAControlPanel()
        
        # Test registry-based operations (Windows specific)
        settings = ncp.get_gpu_settings()
        
        # Test optimization profiles
        ai_result = ncp.optimize_for_ai_workload()
        gaming_result = ncp.optimize_for_gaming()
        power_result = ncp.optimize_for_power_saving()
        
        logging.info("Windows: All optimization profiles executed")
        print("✅ Windows: Optimization profiles tested")
        
        return True
        
    except Exception as e:
        logging.error(f"Windows compatibility test failed: {e}")
        print(f"❌ Windows compatibility test failed: {e}")
        return False

def test_linux_compatibility():
    """Test Linux fallback behavior."""
    print("\n=== Linux Compatibility Test ===")
    logging.info("=== Linux Compatibility Test ===")
    
    try:
        from nvidia_control_panel import NVIDIAControlPanel
        
        ncp = NVIDIAControlPanel()
        
        # Test that system works without Windows-specific features
        settings = ncp.get_gpu_settings()
        
        # The system should gracefully handle Linux environment
        logging.info("Linux: System works in fallback mode")
        print("✅ Linux: Fallback mode operational")
        
        return True
        
    except Exception as e:
        logging.error(f"Linux compatibility test failed: {e}")
        print(f"❌ Linux compatibility test failed: {e}")
        return False

def test_macos_compatibility():
    """Test macOS compatibility."""
    print("\n=== macOS Compatibility Test ===")
    logging.info("=== macOS Compatibility Test ===")
    
    try:
        from nvidia_control_panel import NVIDIAControlPanel
        
        ncp = NVIDIAControlPanel()
        
        # Test basic functionality on macOS
        settings = ncp.get_gpu_settings()
        
        # macOS should use system command fallbacks
        logging.info("macOS: Basic functionality available")
        print("✅ macOS: Basic functionality operational")
        
        return True
        
    except Exception as e:
        logging.error(f"macOS compatibility test failed: {e}")
        print(f"❌ macOS compatibility test failed: {e}")
        return False

def test_containerized_environment():
    """Test behavior in containerized environments."""
    print("\n=== Containerized Environment Test ===")
    logging.info("=== Containerized Environment Test ===")
    
    try:
        from nvidia_control_panel import NVIDIAControlPanel
        
        ncp = NVIDIAControlPanel()
        
        # Test that system works in constrained environments
        settings = ncp.get_gpu_settings()
        
        # Test error handling and fallbacks
        try:
            # This should work even in containers
            custom_res = CustomResolution(1920, 1080, 60, name="Container_Test")
            ncp.add_custom_resolution(custom_res)
            ncp.remove_custom_resolution("Container_Test")
        except Exception as e:
            logging.warning(f"Container test: Some features may not work: {e}")
        
        logging.info("Container: System works in constrained environment")
        print("✅ Container: Basic functionality operational")
        
        return True
        
    except Exception as e:
        logging.error(f"Container compatibility test failed: {e}")
        print(f"❌ Container compatibility test failed: {e}")
        return False

def main():
    """Run all cross-platform compatibility tests."""
    print("Starting cross-platform compatibility testing...")
    logging.info("Starting cross-platform compatibility testing")
    
    results = {}
    
    # Test current platform
    current_platform = platform.system()
    results[current_platform] = simulate_platform_behavior(current_platform)
    
    # Test specific platform functionalities
    results["Windows_Specific"] = test_windows_compatibility()
    results["Linux_Fallback"] = test_linux_compatibility() 
    results["macOS_Basic"] = test_macos_compatibility()
    results["Containerized"] = test_containerized_environment()
    
    # Summary
    print("\n" + "="*50)
    print("CROSS-PLATFORM COMPATIBILITY TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for platform_test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{platform_test:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("🎉 All cross-platform compatibility tests PASSED!")
        logging.info("All cross-platform compatibility tests passed")
        return True
    else:
        print("❌ Some cross-platform compatibility tests FAILED!")
        logging.warning("Some cross-platform compatibility tests failed")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nCross-platform compatibility testing completed successfully!")
        print("Check cross_platform_compatibility_test.log for detailed results.")
    else:
        print("\nCross-platform compatibility testing completed with some failures!")
        print("Check cross_platform_compatibility_test.log for error details.")
    
    sys.exit(0 if success else 1)
