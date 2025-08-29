#!/usr/bin/env python3
"""
Test script for NVIDIA Control Panel integration with NVIDIA NeMo-Agent-Toolkit.
This script demonstrates the GPU settings management capabilities.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_integration import NvidiaIntegration

def test_gpu_settings_integration():
    """Test the NVIDIA Control Panel integration functionality."""
    print("=" * 60)
    print("Testing NVIDIA Control Panel Integration")
    print("=" * 60)
    
    # Initialize the NVIDIA integration
    nvidia = NvidiaIntegration()
    
    print(f"NVIDIA Integration Available: {nvidia.is_available}")
    
    # Test 1: Get current GPU settings
    print("\n1. Getting current GPU settings...")
    try:
        current_settings = nvidia.get_gpu_settings()
        print("✓ Current GPU Settings Retrieved:")
        for key, value in current_settings.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"✗ Error getting GPU settings: {e}")
    
    # Test 2: Set GPU settings (simulated or real)
    print("\n2. Setting GPU settings...")
    try:
        new_settings = {
            "power_mode": "Prefer Maximum Performance",
            "texture_filtering": "High Quality",
            "vertical_sync": "Adaptive"
        }
        
        result = nvidia.set_gpu_settings(new_settings)
        print(f"✓ GPU Settings Update Result: {result}")
    except Exception as e:
        print(f"✗ Error setting GPU settings: {e}")
    
    # Test 3: Get advanced status including Control Panel info
    print("\n3. Getting advanced system status...")
    try:
        status = nvidia.get_advanced_status()
        print("✓ Advanced System Status:")
        for key, value in status.items():
            if key == "timestamp":
                print(f"   {key}: {value}")
            elif isinstance(value, bool):
                print(f"   {key}: {'✓' if value else '✗'}")
            elif isinstance(value, list):
                print(f"   {key}: {len(value)} items")
            else:
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"✗ Error getting advanced status: {e}")
    
    # Test 4: Test simulation mode behavior
    print("\n4. Testing simulation mode behavior...")
    try:
        # Test with a more comprehensive settings object
        comprehensive_settings = {
            "power_mode": "Optimal Power",
            "texture_filtering": "Performance",
            "vertical_sync": "Off",
            "gpu_clock": 1800,
            "memory_clock": 8000,
            "fan_speed": 70
        }
        
        result = nvidia.set_gpu_settings(comprehensive_settings)
        print(f"✓ Comprehensive Settings Result: {result}")
        
        # Verify the settings were applied (or simulated)
        updated_settings = nvidia.get_gpu_settings()
        print("✓ Updated Settings Verification:")
        for key in comprehensive_settings.keys():
            if key in updated_settings:
                print(f"   {key}: {updated_settings[key]}")
                
    except Exception as e:
        print(f"✗ Error in comprehensive test: {e}")
    
    print("\n" + "=" * 60)
    print("NVIDIA Control Panel Integration Test Complete!")
    print("=" * 60)

    # Additional Test: Invalid settings
    print("\n5. Testing invalid GPU settings...")
    try:
        invalid_settings = {
            "power_mode": "Invalid Mode",
            "texture_filtering": "High Quality"
        }
        result = nvidia.set_gpu_settings(invalid_settings)
        print(f"✓ Invalid Settings Result: {result}")
    except Exception as e:
        print(f"✗ Error setting invalid GPU settings: {e}")

    # Additional Test: Edge case for no GPU
    print("\n6. Testing behavior with no GPU available...")
    try:
        nvidia.is_available = False  # Simulate no GPU available
        result = nvidia.get_gpu_settings()
        print("✓ Retrieved settings in no GPU scenario:")
        print(result)
    except Exception as e:
    """Test the NVIDIA Control Panel integration functionality."""
    print("=" * 60)
    print("Testing NVIDIA Control Panel Integration")
    print("=" * 60)
    
    # Initialize the NVIDIA integration
    nvidia = NvidiaIntegration()
    
    print(f"NVIDIA Integration Available: {nvidia.is_available}")
    
    # Test 1: Get current GPU settings
    print("\n1. Getting current GPU settings...")
    try:
        current_settings = nvidia.get_gpu_settings()
        print("✓ Current GPU Settings Retrieved:")
        for key, value in current_settings.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"✗ Error getting GPU settings: {e}")
    
    # Test 2: Set GPU settings (simulated or real)
    print("\n2. Setting GPU settings...")
    try:
        new_settings = {
            "power_mode": "Prefer Maximum Performance",
            "texture_filtering": "High Quality",
            "vertical_sync": "Adaptive"
        }
        
        result = nvidia.set_gpu_settings(new_settings)
        print(f"✓ GPU Settings Update Result: {result}")
    except Exception as e:
        print(f"✗ Error setting GPU settings: {e}")
    
    # Test 3: Get advanced status including Control Panel info
    print("\n3. Getting advanced system status...")
    try:
        status = nvidia.get_advanced_status()
        print("✓ Advanced System Status:")
        for key, value in status.items():
            if key == "timestamp":
                print(f"   {key}: {value}")
            elif isinstance(value, bool):
                print(f"   {key}: {'✓' if value else '✗'}")
            elif isinstance(value, list):
                print(f"   {key}: {len(value)} items")
            else:
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"✗ Error getting advanced status: {e}")
    
    # Test 4: Test simulation mode behavior
    print("\n4. Testing simulation mode behavior...")
    try:
        # Test with a more comprehensive settings object
        comprehensive_settings = {
            "power_mode": "Optimal Power",
            "texture_filtering": "Performance",
            "vertical_sync": "Off",
            "gpu_clock": 1800,
            "memory_clock": 8000,
            "fan_speed": 70
        }
        
        result = nvidia.set_gpu_settings(comprehensive_settings)
        print(f"✓ Comprehensive Settings Result: {result}")
        
        # Verify the settings were applied (or simulated)
        updated_settings = nvidia.get_gpu_settings()
        print("✓ Updated Settings Verification:")
        for key in comprehensive_settings.keys():
            if key in updated_settings:
                print(f"   {key}: {updated_settings[key]}")
                
    except Exception as e:
        print(f"✗ Error in comprehensive test: {e}")
    
    print("\n" + "=" * 60)
    print("NVIDIA Control Panel Integration Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_gpu_settings_integration()
