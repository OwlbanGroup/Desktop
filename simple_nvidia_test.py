#!/usr/bin/env python3
"""
Simple test to verify NVIDIA integration is working
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from nvidia_integration import NvidiaIntegration
    
    print("=" * 50)
    print("Testing NVIDIA Integration")
    print("=" * 50)
    
    # Initialize NVIDIA integration
    nvidia = NvidiaIntegration()
    print(f"✓ NVIDIA Integration initialized")
    print(f"✓ NVIDIA Available: {nvidia.is_available}")
    
    # Test GPU settings
    settings = nvidia.get_gpu_settings()
    print(f"✓ GPU Settings retrieved successfully")
    print(f"  Power Mode: {settings.get('power_mode', 'N/A')}")
    print(f"  Temperature: {settings.get('temperature', 'N/A')}°C")
    
    # Test advanced status
    status = nvidia.get_advanced_status()
    print(f"✓ Advanced status retrieved")
    print(f"  NVIDIA Control Panel Available: {status.get('nvidia_control_panel_available', False)}")
    
    print("=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
