#!/usr/bin/env python3
"""
Test script for NVIDIA GPU monitoring methods.
Tests the _collect_gpu_data and _collect_system_metrics methods.
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.getcwd())

try:
    from nvidia_oscar_broome_integration import NVIDIAMonitor, gpu_monitoring_data, system_metrics
    print("✓ Successfully imported NVIDIAMonitor class")
except ImportError as e:
    print(f"✗ Failed to import NVIDIAMonitor: {e}")
    sys.exit(1)

def test_gpu_data_collection():
    """Test GPU data collection method."""
    print("\n=== Testing GPU Data Collection ===")

    monitor = NVIDIAMonitor()

    try:
        monitor._collect_gpu_data()
        print("✓ GPU data collection method executed successfully")

        if monitor.gpu_data:
            print(f"✓ GPU data collected: {len(monitor.gpu_data)} GPU(s) found")
            for i, gpu in enumerate(monitor.gpu_data):
                print(f"  GPU {i}: {gpu['name']} - {gpu['utilization_gpu_percent']}% utilization")
        else:
            print("⚠ No GPU data collected (may be expected if no NVIDIA GPUs present)")

        # Check global data
        if 'gpus' in gpu_monitoring_data:
            print(f"✓ Global GPU monitoring data updated: {len(gpu_monitoring_data['gpus'])} GPU(s)")
        else:
            print("⚠ Global GPU monitoring data not updated")

    except Exception as e:
        print(f"✗ GPU data collection failed: {e}")
        return False

    return True

def test_system_metrics_collection():
    """Test system metrics collection method."""
    print("\n=== Testing System Metrics Collection ===")

    monitor = NVIDIAMonitor()

    try:
        monitor._collect_system_metrics()
        print("✓ System metrics collection method executed successfully")

        if monitor.system_info:
            print("✓ System metrics collected:")
            print(f"  CPU Usage: {monitor.system_info['cpu_percent']}%")
            print(f"  Memory: {monitor.system_info['memory_used_mb']}MB / {monitor.system_info['memory_total_mb']}MB")
            print(f"  Disk: {monitor.system_info['disk_used_gb']}GB / {monitor.system_info['disk_total_gb']}GB")
            print(f"  Platform: {monitor.system_info['platform']} {monitor.system_info['platform_release']}")
        else:
            print("⚠ No system metrics collected")

        # Check global data
        if system_metrics:
            print("✓ Global system metrics updated")
        else:
            print("⚠ Global system metrics not updated")

    except Exception as e:
        print(f"✗ System metrics collection failed: {e}")
        return False

    return True

def test_monitoring_loop():
    """Test the monitoring loop briefly."""
    print("\n=== Testing Monitoring Loop ===")

    monitor = NVIDIAMonitor()

    try:
        # Start monitoring
        monitor.start_monitoring()
        print("✓ Monitoring started")

        # Let it run for a few seconds
        print("  Running monitoring for 10 seconds...")
        time.sleep(10)

        # Stop monitoring
        monitor.stop_monitoring()
        print("✓ Monitoring stopped successfully")

        # Check if data was collected during monitoring
        if monitor.gpu_data or monitor.system_info:
            print("✓ Data collected during monitoring loop")
        else:
            print("⚠ No data collected during monitoring loop")

    except Exception as e:
        print(f"✗ Monitoring loop test failed: {e}")
        return False

    return True

def main():
    """Main test function."""
    print("NVIDIA GPU Monitoring Methods Test")
    print("=" * 40)
    print(f"Test started at: {datetime.now()}")

    tests_passed = 0
    total_tests = 3

    # Test GPU data collection
    if test_gpu_data_collection():
        tests_passed += 1

    # Test system metrics collection
    if test_system_metrics_collection():
        tests_passed += 1

    # Test monitoring loop
    if test_monitoring_loop():
        tests_passed += 1

    print("\n" + "=" * 40)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("✓ All tests passed successfully!")
        return 0
    else:
        print("⚠ Some tests failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
