#!/usr/bin/env python3
"""Test script for the enhanced NVIDIA Control Panel module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_control_panel_enhanced import NVIDIAControlPanel

def main():
    print("Testing Enhanced NVIDIA Control Panel...")
    
    try:
        # Initialize the control panel
        panel = NVIDIAControlPanel()
        print(f"[OK] NVIDIA Control Panel initialized successfully")
        print(f"  - GPU Count: {panel.gpu_count}")
        print(f"  - Driver Version: {panel.driver_version}")
        print(f"  - NVAPI Available: {panel.nvapi_available}")
        print(f"  - Platform: {panel.is_windows}")
        
        # Test getting GPU settings
        print("\nTesting GPU settings retrieval...")
        settings = panel.get_gpu_settings()
        print(f"[OK] GPU settings retrieved successfully")
        print(f"  - Settings keys: {list(settings.keys())}")
        print(f"  - Power Mode: {settings.get('power_mode', 'Not found')}")
        print(f"  - Texture Filtering: {settings.get('texture_filtering', 'Not found')}")
        print(f"  - Vertical Sync: {settings.get('vertical_sync', 'Not found')}")
        
        # Test system topology
        print("\nTesting system topology...")
        topology = panel.get_system_topology()
        print(f"[OK] System topology retrieved successfully")
        print(f"  - Topology Type: {topology.topology_type}")
        print(f"  - GPU Nodes: {len(topology.gpu_nodes)}")
        print(f"  - Display Nodes: {len(topology.display_nodes)}")
        
        # Test PhysX configuration
        print("\nTesting PhysX configuration...")
        physx_config = panel.get_physx_configuration()
        print(f"[OK] PhysX configuration retrieved successfully")
        print(f"  - Enabled: {physx_config.enabled}")
        print(f"  - Selected Processor: {physx_config.selected_processor}")
        print(f"  - Available GPUs: {physx_config.available_gpus}")
        
        # Test performance counters
        print("\nTesting performance counters...")
        counters = panel.get_performance_counters()
        print(f"[OK] Performance counters retrieved successfully")
        print(f"  - Counter count: {len(counters)}")
        for counter in counters[:3]:  # Show first 3 counters
            print(f"    - {counter.name}: {counter.value} {counter.unit or ''}")
            
        print("\n[OK] All tests completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
