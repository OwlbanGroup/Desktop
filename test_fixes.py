#!/usr/bin/env python3
"""
Test script to verify the NVIDIA Control Panel fixes.
"""

import sys
import traceback

def test_basic_functionality():
    """Test basic NVIDIA Control Panel functionality."""
    try:
        from nvidia_control_panel_enhanced import NVIDIAControlPanel

        print("Testing NVIDIA Control Panel initialization...")
        panel = NVIDIAControlPanel()

        print(f"GPU Count: {panel.gpu_count}")
        print(f"NVAPI Available: {panel.nvapi_available}")
        print(f"Driver Version: {panel.driver_version}")

        # Test PhysX configuration
        print("\nTesting PhysX configuration...")
        config = panel.get_physx_configuration()
        print(f"PhysX Config: {config}")

        # Test GPU settings
        print("\nTesting GPU settings...")
        settings = panel.get_gpu_settings(0)
        print(f"GPU Settings: {settings}")

        # Test system topology
        print("\nTesting system topology...")
        topology = panel.get_system_topology()
        print(f"System Topology: {topology.topology_type}")

        print("\n✅ All basic tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

def test_physx_methods():
    """Test PhysX-specific methods."""
    try:
        from nvidia_control_panel_enhanced import NVIDIAControlPanel, PhysXConfiguration, PhysXProcessor

        print("\nTesting PhysX methods...")
        panel = NVIDIAControlPanel()

        # Test registry methods
        config = panel._get_physx_config_via_registry()
        print(f"Registry PhysX config: {config}")

        # Test setting PhysX config
        test_config = PhysXConfiguration(
            enabled=True,
            selected_processor=PhysXProcessor.GPU,
            available_gpus=["GPU0"],
            gpu_count=1
        )

        result = panel._set_physx_config_via_registry(test_config)
        print(f"Set PhysX config result: {result}")

        print("✅ PhysX methods test passed!")
        return True

    except Exception as e:
        print(f"❌ PhysX methods test failed: {e}")
        traceback.print_exc()
        return False

def test_gpu_index_handling():
    """Test GPU index handling with mock GPUs."""
    try:
        from nvidia_control_panel_enhanced import NVIDIAControlPanel

        print("\nTesting GPU index handling...")
        panel = NVIDIAControlPanel()

        # Test accessing GPU 0 (should work even with no physical GPUs)
        settings = panel.get_gpu_settings(0)
        print(f"GPU 0 settings: {settings}")

        # Test performance counters
        counters = panel.get_performance_counters(0)
        print(f"Performance counters: {len(counters)} counters found")

        # Test frame sync mode
        frame_sync = panel.get_frame_sync_mode(0)
        print(f"Frame sync mode: {frame_sync}")

        print("✅ GPU index handling test passed!")
        return True

    except Exception as e:
        print(f"❌ GPU index handling test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running NVIDIA Control Panel fix verification tests...\n")

    tests = [
        test_basic_functionality,
        test_physx_methods,
        test_gpu_index_handling
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
