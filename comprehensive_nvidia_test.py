#!/usr/bin/env python3
"""
Comprehensive test suite for NVIDIA Control Panel Enhanced module.
Tests all major functionality including GPU settings, PhysX, topology, and performance monitoring.
"""

import sys
import os
import logging
from typing import Any, Dict, List

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from nvidia_control_panel_enhanced import (
        NVIDIAControlPanel, get_nvidia_control_panel,
        FrameSyncMode, PowerMode, TextureFiltering, VerticalSync,
        AntiAliasingMode, AnisotropicFiltering, PhysXProcessor,
        PerformanceCounterType, TopologyType, ConnectionType,
        DisplayTopologyMode, PCIeGeneration, PCIeLinkWidth,
        PhysXConfiguration, SystemTopology, GPUTopologyNode,
        DisplayTopologyNode, PerformanceCounter, VideoSettings,
        CustomResolution, GPUProfile
    )
    print("[PASS] Successfully imported all NVIDIA Control Panel classes and enums")
except ImportError as e:
    print(f"[FAIL] Failed to import required modules: {e}")
    sys.exit(1)

def test_initialization():
    """Test module initialization and singleton pattern."""
    print("\n=== Testing Initialization ===")

    try:
        # Test singleton pattern
        panel1 = get_nvidia_control_panel()
        panel2 = get_nvidia_control_panel()
        if panel1 is panel2:
            print("[PASS] Singleton pattern working correctly")
        else:
            print("[FAIL] Singleton pattern not working")
            return False

        # Test basic attributes
        if hasattr(panel1, 'gpu_count'):
            print(f"[PASS] GPU count: {panel1.gpu_count}")
        else:
            print("[FAIL] GPU count attribute missing")
            return False

        if hasattr(panel1, 'nvapi_available'):
            print(f"[PASS] NVAPI available: {panel1.nvapi_available}")
        else:
            print("[FAIL] NVAPI availability attribute missing")
            return False

        if hasattr(panel1, 'driver_version'):
            print(f"[PASS] Driver version: {panel1.driver_version}")
        else:
            print("[FAIL] Driver version attribute missing")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Initialization test failed: {e}")
        return False

def test_gpu_settings():
    """Test GPU settings retrieval and validation."""
    print("\n=== Testing GPU Settings ===")

    try:
        panel = get_nvidia_control_panel()

        # Test get_gpu_settings
        settings = panel.get_gpu_settings()
        if isinstance(settings, dict):
            print("[PASS] GPU settings retrieved successfully")
            print(f"  - GPU count: {settings.get('gpu_count', 'N/A')}")
            print(f"  - NVAPI available: {settings.get('nvapi_available', 'N/A')}")
            print(f"  - Platform: {settings.get('platform', 'N/A')}")
        else:
            print("[FAIL] GPU settings not returned as dictionary")
            return False

        # Test settings validation
        valid_settings = {
            "power_mode": PowerMode.OPTIMAL_POWER.value,
            "texture_filtering": TextureFiltering.QUALITY.value,
            "vertical_sync": VerticalSync.OFF.value
        }

        invalid_settings = {
            "power_mode": "invalid_mode",
            "texture_filtering": 123,
            "vertical_sync": "invalid_sync"
        }

        # Valid settings should pass
        try:
            panel._validate_settings(valid_settings)
            print("[PASS] Valid settings passed validation")
        except Exception as e:
            print(f"[FAIL] Valid settings failed validation: {e}")
            return False

        # Invalid settings should fail
        try:
            panel._validate_settings(invalid_settings)
            print("[FAIL] Invalid settings should have failed validation")
            return False
        except ValueError:
            print("[PASS] Invalid settings properly rejected")
        except Exception as e:
            print(f"[FAIL] Invalid settings caused unexpected error: {e}")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] GPU settings test failed: {e}")
        return False

def test_frame_sync_mode():
    """Test frame sync mode functionality."""
    print("\n=== Testing Frame Sync Mode ===")

    try:
        panel = get_nvidia_control_panel()

        # Test valid input
        result = panel.get_frame_sync_mode(0)
        if isinstance(result, FrameSyncMode):
            print(f"[PASS] Valid frame sync mode retrieved: {result}")
        else:
            print(f"[FAIL] Invalid frame sync mode type: {type(result)}")
            return False

        # Test invalid inputs
        test_cases = [
            ("string", TypeError),
            (-1, ValueError),
            (999, ValueError)
        ]

        for invalid_input, expected_exception in test_cases:
            try:
                panel.get_frame_sync_mode(invalid_input)
                print(f"[FAIL] Input {invalid_input} should have raised {expected_exception.__name__}")
                return False
            except expected_exception:
                print(f"[PASS] Input {invalid_input} properly rejected with {expected_exception.__name__}")
            except Exception as e:
                print(f"[FAIL] Input {invalid_input} caused unexpected error: {e}")
                return False

        return True

    except Exception as e:
        print(f"[FAIL] Frame sync mode test failed: {e}")
        return False

def test_physx_configuration():
    """Test PhysX configuration functionality."""
    print("\n=== Testing PhysX Configuration ===")

    try:
        panel = get_nvidia_control_panel()

        # Test get_physx_configuration
        config = panel.get_physx_configuration()
        if isinstance(config, PhysXConfiguration):
            print("[PASS] PhysX configuration retrieved successfully")
            print(f"  - Enabled: {config.enabled}")
            print(f"  - Processor: {config.selected_processor}")
            print(f"  - GPU count: {config.gpu_count}")
        else:
            print(f"[FAIL] PhysX configuration not returned as PhysXConfiguration: {type(config)}")
            return False

        # Test set_physx_configuration
        new_config = PhysXConfiguration(
            enabled=True,
            selected_processor=PhysXProcessor.GPU,
            gpu_count=panel.gpu_count
        )

        result = panel.set_physx_configuration(new_config)
        if "successfully" in result.lower():
            print("[PASS] PhysX configuration set successfully")
        else:
            print(f"[FAIL] PhysX configuration set failed: {result}")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] PhysX configuration test failed: {e}")
        return False

def test_system_topology():
    """Test system topology functionality."""
    print("\n=== Testing System Topology ===")

    try:
        panel = get_nvidia_control_panel()

        # Test get_system_topology
        topology = panel.get_system_topology()
        if isinstance(topology, SystemTopology):
            print("[PASS] System topology retrieved successfully")
            print(f"  - Topology type: {topology.topology_type}")
            print(f"  - GPU nodes: {len(topology.gpu_nodes)}")
            print(f"  - Display nodes: {len(topology.display_nodes)}")
            print(f"  - Connections: {len(topology.connections)}")
        else:
            print(f"[FAIL] System topology not returned as SystemTopology: {type(topology)}")
            return False

        # Test GPU topology info
        if topology.gpu_nodes:
            gpu_info = panel.get_gpu_topology_info(0)
            if isinstance(gpu_info, GPUTopologyNode):
                print("[PASS] GPU topology info retrieved successfully")
                print(f"  - GPU name: {gpu_info.name}")
                print(f"  - Memory: {gpu_info.memory_size_mb} MB")
            else:
                print(f"[FAIL] GPU topology info not returned as GPUTopologyNode: {type(gpu_info)}")
                return False

        # Test display topology info
        if topology.display_nodes:
            display_info = panel.get_display_topology_info(0)
            if isinstance(display_info, DisplayTopologyNode):
                print("[PASS] Display topology info retrieved successfully")
                print(f"  - Resolution: {display_info.resolution_width}x{display_info.resolution_height}")
                print(f"  - Refresh rate: {display_info.refresh_rate} Hz")
            else:
                print(f"[FAIL] Display topology info not returned as DisplayTopologyNode: {type(display_info)}")
                return False

        return True

    except Exception as e:
        print(f"[FAIL] System topology test failed: {e}")
        return False

def test_performance_monitoring():
    """Test performance monitoring functionality."""
    print("\n=== Testing Performance Monitoring ===")

    try:
        panel = get_nvidia_control_panel()

        # Test get_performance_counters
        counters = panel.get_performance_counters()
        if isinstance(counters, list):
            print(f"[PASS] Performance counters retrieved: {len(counters)} counters")
            for counter in counters[:3]:  # Show first 3
                if isinstance(counter, PerformanceCounter):
                    print(f"  - {counter.name}: {counter.value} {counter.unit}")
                else:
                    print(f"[FAIL] Invalid counter type: {type(counter)}")
                    return False
        else:
            print(f"[FAIL] Performance counters not returned as list: {type(counters)}")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Performance monitoring test failed: {e}")
        return False

def test_video_settings():
    """Test video settings functionality."""
    print("\n=== Testing Video Settings ===")

    try:
        # Test VideoSettings dataclass
        settings = VideoSettings(
            brightness=75,
            contrast=80,
            gamma=1.2,
            overscan_percentage=5
        )

        if settings.brightness == 75 and settings.contrast == 80:
            print("[PASS] VideoSettings dataclass working correctly")
        else:
            print("[FAIL] VideoSettings dataclass not working")
            return False

        # Test validation
        try:
            invalid_settings = VideoSettings(brightness=150)  # Invalid brightness
            print("[FAIL] Invalid brightness should have been rejected")
            return False
        except ValueError:
            print("[PASS] Invalid brightness properly rejected")
        except Exception as e:
            print(f"[FAIL] Unexpected error with invalid brightness: {e}")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Video settings test failed: {e}")
        return False

def test_custom_resolution():
    """Test custom resolution functionality."""
    print("\n=== Testing Custom Resolution ===")

    try:
        # Test CustomResolution dataclass
        resolution = CustomResolution(
            width=2560,
            height=1440,
            refresh_rate=144,
            color_depth=32
        )

        if resolution.width == 2560 and resolution.height == 1440:
            print("[PASS] CustomResolution dataclass working correctly")
            print(f"  - Name: {resolution.name}")
        else:
            print("[FAIL] CustomResolution dataclass not working")
            return False

        # Test validation
        try:
            invalid_resolution = CustomResolution(width=100, height=100)  # Invalid dimensions
            print("[FAIL] Invalid resolution should have been rejected")
            return False
        except ValueError:
            print("[PASS] Invalid resolution properly rejected")
        except Exception as e:
            print(f"[FAIL] Unexpected error with invalid resolution: {e}")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Custom resolution test failed: {e}")
        return False

def test_enums():
    """Test enum values and functionality."""
    print("\n=== Testing Enums ===")

    try:
        # Test FrameSyncMode enum
        modes = [FrameSyncMode.OFF, FrameSyncMode.ON, FrameSyncMode.MASTER, FrameSyncMode.SLAVE]
        print(f"[PASS] FrameSyncMode values: {[mode.value for mode in modes]}")

        # Test PowerMode enum
        power_modes = [PowerMode.OPTIMAL_POWER, PowerMode.ADAPTIVE, PowerMode.PREFER_MAX_PERFORMANCE]
        print(f"[PASS] PowerMode values: {[mode.value for mode in power_modes]}")

        # Test PhysXProcessor enum
        processors = [PhysXProcessor.CPU, PhysXProcessor.GPU, PhysXProcessor.AUTO]
        print(f"[PASS] PhysXProcessor values: {[mode.value for mode in processors]}")

        # Test TopologyType enum
        topologies = [TopologyType.SINGLE_GPU, TopologyType.SLI, TopologyType.NVLINK]
        print(f"[PASS] TopologyType values: {[mode.value for mode in topologies]}")

        return True

    except Exception as e:
        print(f"[FAIL] Enum test failed: {e}")
        return False

def test_error_handling():
    """Test error handling across the module."""
    print("\n=== Testing Error Handling ===")

    try:
        panel = get_nvidia_control_panel()

        # Test with invalid GPU index for various methods
        methods_to_test = [
            ('get_gpu_settings', lambda: panel.get_gpu_settings(-1)),
            ('get_performance_counters', lambda: panel.get_performance_counters(-1)),
            ('get_gpu_topology_info', lambda: panel.get_gpu_topology_info(-1)),
            ('get_display_topology_info', lambda: panel.get_display_topology_info(-1))
        ]

        for method_name, method_call in methods_to_test:
            try:
                method_call()
                print(f"[PASS] {method_name} handled invalid input gracefully")
            except Exception as e:
                print(f"  - {method_name} error (expected): {type(e).__name__}")

        return True

    except Exception as e:
        print(f"[FAIL] Error handling test failed: {e}")
        return False

def main():
    """Run all comprehensive tests."""
    print("Starting Comprehensive Testing for NVIDIA Control Panel Enhanced Module")
    print("=" * 80)

    # Configure logging
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

    tests = [
        ("Initialization", test_initialization),
        ("GPU Settings", test_gpu_settings),
        ("Frame Sync Mode", test_frame_sync_mode),
        ("PhysX Configuration", test_physx_configuration),
        ("System Topology", test_system_topology),
        ("Performance Monitoring", test_performance_monitoring),
        ("Video Settings", test_video_settings),
        ("Custom Resolution", test_custom_resolution),
        ("Enums", test_enums),
        ("Error Handling", test_error_handling)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        if test_func():
            passed += 1
            print(f"[PASS] {test_name} PASSED")
        else:
            print(f"[FAIL] {test_name} FAILED")

    print("\n" + "=" * 80)
    print(f"Comprehensive Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All comprehensive tests PASSED!")
        return 0
    else:
        print("[ERROR] Some comprehensive tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
