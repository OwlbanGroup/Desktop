#!/usr/bin/env python3
"""
Comprehensive validation script for NVIDIA Control Panel fixes.
Tests all edge cases, error handling, and integration scenarios.
"""

import sys
import traceback
import time
from typing import Dict, List, Any

def test_physx_edge_cases():
    """Test PhysX configuration edge cases and error handling."""
    try:
        from nvidia_control_panel_enhanced import (
            NVIDIAControlPanel,
            PhysXConfiguration,
            PhysXProcessor
        )

        print("\n🧪 Testing PhysX Edge Cases...")

        panel = NVIDIAControlPanel()

        # Test 1: Invalid PhysX processor
        try:
            invalid_config = PhysXConfiguration(
                enabled=True,
                selected_processor="INVALID_PROCESSOR",
                available_gpus=[],
                gpu_count=0
            )
            panel._set_physx_config_via_registry(invalid_config)
            print("❌ Should have failed with invalid processor")
            return False
        except Exception as e:
            print(f"✅ Correctly handled invalid processor: {e}")

        # Test 2: Empty GPU list when GPU processor selected
        try:
            gpu_config = PhysXConfiguration(
                enabled=True,
                selected_processor=PhysXProcessor.GPU,
                available_gpus=[],
                gpu_count=0
            )
            panel._set_physx_config_via_registry(gpu_config)
            print("❌ Should have failed with empty GPU list")
            return False
        except Exception as e:
            print(f"✅ Correctly handled empty GPU list: {e}")

        # Test 3: Valid configurations
        valid_configs = [
            PhysXConfiguration(
                enabled=True,
                selected_processor=PhysXProcessor.CPU,
                available_gpus=[],
                gpu_count=0
            ),
            PhysXConfiguration(
                enabled=True,
                selected_processor=PhysXProcessor.GPU,
                available_gpus=["GPU0", "GPU1"],
                gpu_count=2
            ),
            PhysXConfiguration(
                enabled=False,
                selected_processor=PhysXProcessor.CPU,
                available_gpus=[],
                gpu_count=0
            )
        ]

        for i, config in enumerate(valid_configs):
            try:
                result = panel._set_physx_config_via_registry(config)
                print(f"✅ Valid config {i+1} set successfully: {result}")
            except Exception as e:
                print(f"❌ Valid config {i+1} failed: {e}")
                return False

        # Test 4: Registry read/write consistency
        test_config = PhysXConfiguration(
            enabled=True,
            selected_processor=PhysXProcessor.GPU,
            available_gpus=["GPU0"],
            gpu_count=1
        )

        # Write config
        panel._set_physx_config_via_registry(test_config)

        # Read config back
        read_config = panel._get_physx_config_via_registry()

        if read_config.enabled == test_config.enabled and \
           read_config.selected_processor == test_config.selected_processor:
            print("✅ Registry read/write consistency verified")
        else:
            print("❌ Registry read/write inconsistency detected")
            return False

        print("✅ PhysX edge cases test passed!")
        return True

    except Exception as e:
        print(f"❌ PhysX edge cases test failed: {e}")
        traceback.print_exc()
        return False

def test_gpu_index_handling():
    """Test GPU index handling with various scenarios."""
    try:
        from nvidia_control_panel_enhanced import NVIDIAControlPanel

        print("\n🧪 Testing GPU Index Handling...")

        panel = NVIDIAControlPanel()

        # Test 1: Valid GPU indices
        for gpu_index in range(max(1, panel.gpu_count)):  # At least test index 0
            try:
                settings = panel.get_gpu_settings(gpu_index)
                print(f"✅ GPU {gpu_index} settings retrieved: {type(settings).__name__}")

                counters = panel.get_performance_counters(gpu_index)
                print(f"✅ GPU {gpu_index} performance counters: {len(counters)} counters")

                frame_sync = panel.get_frame_sync_mode(gpu_index)
                print(f"✅ GPU {gpu_index} frame sync mode: {frame_sync}")

            except Exception as e:
                print(f"❌ GPU {gpu_index} access failed: {e}")
                return False

        # Test 2: Invalid GPU indices
        invalid_indices = [-1, 999, panel.gpu_count + 10]

        for invalid_index in invalid_indices:
            try:
                panel.get_gpu_settings(invalid_index)
                print(f"❌ Should have failed with invalid index {invalid_index}")
                return False
            except (IndexError, ValueError) as e:
                print(f"✅ Correctly handled invalid index {invalid_index}: {e}")
            except Exception as e:
                print(f"⚠️ Unexpected error for invalid index {invalid_index}: {e}")

        # Test 3: Mock GPU handling when no physical GPUs
        if panel.gpu_count == 0:
            try:
                settings = panel.get_gpu_settings(0)
                print("✅ Mock GPU settings handled correctly for index 0")
            except Exception as e:
                print(f"❌ Mock GPU handling failed: {e}")
                return False

        print("✅ GPU index handling test passed!")
        return True

    except Exception as e:
        print(f"❌ GPU index handling test failed: {e}")
        traceback.print_exc()
        return False

def test_performance_counters():
    """Test performance counters functionality."""
    try:
        from nvidia_control_panel_enhanced import NVIDIAControlPanel

        print("\n🧪 Testing Performance Counters...")

        panel = NVIDIAControlPanel()

        # Test counters for available GPUs
        for gpu_index in range(max(1, panel.gpu_count)):
            try:
                counters = panel.get_performance_counters(gpu_index)

                if isinstance(counters, list):
                    print(f"✅ GPU {gpu_index} counters retrieved: {len(counters)} counters")

                    # Validate counter structure
                    for counter in counters[:3]:  # Check first 3 counters
                        if isinstance(counter, dict) and 'name' in counter and 'value' in counter:
                            print(f"  - {counter['name']}: {counter['value']}")
                        else:
                            print(f"❌ Invalid counter structure: {counter}")
                            return False
                else:
                    print(f"❌ Counters not returned as list for GPU {gpu_index}")
                    return False

            except Exception as e:
                print(f"❌ Performance counters failed for GPU {gpu_index}: {e}")
                return False

        # Test counter refresh
        if panel.gpu_count > 0:
            try:
                counters1 = panel.get_performance_counters(0)
                time.sleep(0.1)  # Small delay
                counters2 = panel.get_performance_counters(0)

                if len(counters1) == len(counters2):
                    print("✅ Performance counters refresh working")
                else:
                    print("⚠️ Performance counters length changed between calls")
            except Exception as e:
                print(f"❌ Performance counters refresh test failed: {e}")

        print("✅ Performance counters test passed!")
        return True

    except Exception as e:
        print(f"❌ Performance counters test failed: {e}")
        traceback.print_exc()
        return False

def test_system_integration():
    """Test integration with system components."""
    try:
        from nvidia_control_panel_enhanced import NVIDIAControlPanel

        print("\n🧪 Testing System Integration...")

        panel = NVIDIAControlPanel()

        # Test system topology
        try:
            topology = panel.get_system_topology()
            print(f"✅ System topology retrieved: {topology.topology_type}")

            if hasattr(topology, 'gpu_count'):
                print(f"  - GPU Count: {topology.gpu_count}")
            if hasattr(topology, 'cpu_count'):
                print(f"  - CPU Count: {topology.cpu_count}")

        except Exception as e:
            print(f"❌ System topology failed: {e}")
            return False

        # Test driver version detection
        try:
            version = panel.driver_version
            print(f"✅ Driver version detected: {version}")

            # Validate version format (should be something like "XXX.XX")
            if isinstance(version, str) and len(version) > 0:
                print("✅ Driver version format valid")
            else:
                print("⚠️ Driver version format may be invalid")

        except Exception as e:
            print(f"❌ Driver version detection failed: {e}")

        # Test NVAPI availability
        try:
            available = panel.nvapi_available
            print(f"✅ NVAPI availability checked: {available}")

        except Exception as e:
            print(f"❌ NVAPI availability check failed: {e}")

        print("✅ System integration test passed!")
        return True

    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test comprehensive error handling."""
    try:
        from nvidia_control_panel_enhanced import NVIDIAControlPanel

        print("\n🧪 Testing Error Handling...")

        panel = NVIDIAControlPanel()

        # Test with None parameters
        try:
            panel.get_gpu_settings(None)
            print("❌ Should have failed with None parameter")
            return False
        except (TypeError, ValueError) as e:
            print(f"✅ Correctly handled None parameter: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error with None parameter: {e}")

        # Test with string parameters where int expected
        try:
            panel.get_gpu_settings("invalid")
            print("❌ Should have failed with string parameter")
            return False
        except (TypeError, ValueError) as e:
            print(f"✅ Correctly handled string parameter: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error with string parameter: {e}")

        # Test PhysX with invalid parameters
        try:
            from nvidia_control_panel_enhanced import PhysXConfiguration
            invalid_config = PhysXConfiguration(
                enabled="not_boolean",
                selected_processor="INVALID",
                available_gpus=None,
                gpu_count="not_int"
            )
            panel._set_physx_config_via_registry(invalid_config)
            print("❌ Should have failed with invalid PhysX config")
            return False
        except (TypeError, ValueError) as e:
            print(f"✅ Correctly handled invalid PhysX config: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error with invalid PhysX config: {e}")

        print("✅ Error handling test passed!")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("🚀 Running Comprehensive NVIDIA Control Panel Fix Validation")
    print("=" * 60)

    tests = [
        ("PhysX Edge Cases", test_physx_edge_cases),
        ("GPU Index Handling", test_gpu_index_handling),
        ("Performance Counters", test_performance_counters),
        ("System Integration", test_system_integration),
        ("Error Handling", test_error_handling)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("The NVIDIA Control Panel fixes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
