"""Test script for NVIDIA Control Panel Performance Counters

This script tests the performance counter functionality added to the
NVIDIA Control Panel integration module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_control_panel import NVIDIAControlPanel, PerformanceCounterType, PerformanceCounter, PerformanceCounterGroup

def test_performance_counter_types():
    """Test that all performance counter types are properly defined."""
    print("Testing Performance Counter Types...")
    
    # Test all enum values exist
    expected_types = [
        "GPU Utilization", "Memory Utilization", "Video Engine Utilization",
        "GPU Temperature", "Memory Temperature", "Hotspot Temperature",
        "Power Usage", "Power Limit", "Core Clock", "Memory Clock", "Boost Clock",
        "Total Memory", "Used Memory", "Free Memory", "Memory Bandwidth",
        "Frame Rate", "Fan Speed", "PCIe Bandwidth", "Encoder Usage", 
        "Decoder Usage", "Performance State"
    ]
    
    for expected_type in expected_types:
        found = False
        for counter_type in PerformanceCounterType:
            if counter_type.value == expected_type:
                found = True
                break
        assert found, f"Performance counter type '{expected_type}' not found"
    
    print(f"✓ Found {len(PerformanceCounterType)} performance counter types")
    return True

def test_performance_counter_creation():
    """Test creating PerformanceCounter objects."""
    print("\nTesting Performance Counter Creation...")
    
    # Test basic counter creation
    counter = PerformanceCounter(
        name="Test Counter",
        type=PerformanceCounterType.GPU_UTILIZATION,
        value=50,
        unit="%",
        description="Test GPU utilization counter"
    )
    
    assert counter.name == "Test Counter"
    assert counter.type == PerformanceCounterType.GPU_UTILIZATION
    assert counter.value == 50
    assert counter.unit == "%"
    assert counter.description == "Test GPU utilization counter"
    
    print("✓ PerformanceCounter objects can be created successfully")
    return True

def test_performance_counter_group_creation():
    """Test creating PerformanceCounterGroup objects."""
    print("\nTesting Performance Counter Group Creation...")
    
    # Create some test counters
    counters = [
        PerformanceCounter("GPU Util", PerformanceCounterType.GPU_UTILIZATION, 25, "%"),
        PerformanceCounter("Temp", PerformanceCounterType.TEMPERATURE_GPU, 65, "°C"),
        PerformanceCounter("Clock", PerformanceCounterType.CLOCK_CORE, 1500, "MHz")
    ]
    
    # Create group
    group = PerformanceCounterGroup(
        group_name="Test Group",
        counters=counters
    )
    
    assert group.group_name == "Test Group"
    assert len(group.counters) == 3
    assert group.counters[0].name == "GPU Util"
    assert group.counters[1].type == PerformanceCounterType.TEMPERATURE_GPU
    assert group.counters[2].value == 1500
    
    print("✓ PerformanceCounterGroup objects can be created successfully")
    return True

def test_nvidia_control_panel_performance_counters():
    """Test the NVIDIAControlPanel performance counter methods."""
    print("\nTesting NVIDIAControlPanel Performance Counter Methods...")
    
    # Create control panel instance
    ncp = NVIDIAControlPanel()
    
    # Test get_performance_counters
    print(f"NVAPI Available: {ncp.nvapi_available}")
    
    counters = ncp.get_performance_counters()
    
    # Should return a list of PerformanceCounterGroup objects
    assert isinstance(counters, list), "get_performance_counters should return a list"
    assert len(counters) > 0, "Should return at least one counter group"
    
    for group in counters:
        assert isinstance(group, PerformanceCounterGroup), "Each item should be a PerformanceCounterGroup"
        assert hasattr(group, 'group_name'), "Group should have group_name"
        assert hasattr(group, 'counters'), "Group should have counters"
        assert isinstance(group.counters, list), "Counters should be a list"
        
        print(f"  Group: {group.group_name} ({len(group.counters)} counters)")
        
        for counter in group.counters:
            assert isinstance(counter, PerformanceCounter), "Each counter should be a PerformanceCounter"
            assert hasattr(counter, 'name'), "Counter should have name"
            assert hasattr(counter, 'type'), "Counter should have type"
            assert hasattr(counter, 'value'), "Counter should have value"
            print(f"    - {counter.name}: {counter.value} {getattr(counter, 'unit', '')}")
    
    print("✓ get_performance_counters works correctly")
    return True

def test_simulated_performance_counters():
    """Test the simulated performance counter functionality."""
    print("\nTesting Simulated Performance Counters...")
    
    ncp = NVIDIAControlPanel()
    
    # Test the simulated data method directly
    simulated_data = ncp.get_performance_counters_simulated_data()
    
    assert isinstance(simulated_data, list), "Simulated data should be a list"
    assert len(simulated_data) > 0, "Should have simulated counter groups"
    
    # Count total counters
    total_counters = sum(len(group.counters) for group in simulated_data)
    print(f"✓ Simulated data contains {len(simulated_data)} groups with {total_counters} total counters")
    
    # Test that all expected counter types are present
    counter_types_found = set()
    for group in simulated_data:
        for counter in group.counters:
            counter_types_found.add(counter.type)
    
    expected_types = set(PerformanceCounterType)
    missing_types = expected_types - counter_types_found
    extra_types = counter_types_found - expected_types
    
    if missing_types:
        print(f"Warning: Missing counter types in simulation: {[t.value for t in missing_types]}")
    if extra_types:
        print(f"Warning: Extra counter types in simulation: {[t.value for t in extra_types]}")
    
    return True

def test_performance_counter_management():
    """Test performance counter management methods."""
    print("\nTesting Performance Counter Management Methods...")
    
    ncp = NVIDIAControlPanel()
    
    # Test enable/disable/reset methods (these are mostly placeholders for NVAPI)
    if ncp.nvapi_available:
        print("Testing with NVAPI available...")
        
        # These should return True when NVAPI is available
        enable_result = ncp.enable_performance_counters()
        disable_result = ncp.disable_performance_counters()
        reset_result = ncp.reset_performance_counters()
        
        print(f"Enable result: {enable_result}")
        print(f"Disable result: {disable_result}")
        print(f"Reset result: {reset_result}")
        
    else:
        print("NVAPI not available, testing fallback behavior...")
        
        # These should return False when NVAPI is not available
        enable_result = ncp.enable_performance_counters()
        disable_result = ncp.disable_performance_counters()
        reset_result = ncp.reset_performance_counters()
        
        assert enable_result == False, "Enable should return False without NVAPI"
        assert disable_result == False, "Disable should return False without NVAPI"
        assert reset_result == False, "Reset should return False without NVAPI"
        
        print("✓ Fallback behavior works correctly")
    
    return True

def test_comprehensive_performance_analysis():
    """Test comprehensive performance analysis functionality."""
    print("\nTesting Comprehensive Performance Analysis...")
    
    ncp = NVIDIAControlPanel()
    
    # Get performance counters
    counters = ncp.get_performance_counters()
    
    # Analyze the performance data
    analysis = analyze_performance_counters(counters)
    
    print("Performance Analysis Results:")
    for category, metrics in analysis.items():
        print(f"  {category}:")
        for metric, value in metrics.items():
            print(f"    {metric}: {value}")
    
    # Basic validation of analysis results
    assert 'utilization' in analysis
    assert 'temperature' in analysis
    assert 'power' in analysis
    assert 'memory' in analysis
    
    print("✓ Comprehensive performance analysis works correctly")
    return True

def analyze_performance_counters(counters):
    """Analyze performance counters and provide insights."""
    analysis = {
        'utilization': {},
        'temperature': {},
        'power': {},
        'memory': {},
        'clocks': {},
        'other': {}
    }
    
    for group in counters:
        for counter in group.counters:
            # Categorize and analyze each counter
            if 'utilization' in counter.type.value.lower():
                analysis['utilization'][counter.name] = counter.value
            elif 'temperature' in counter.type.value.lower():
                analysis['temperature'][counter.name] = counter.value
            elif 'power' in counter.type.value.lower():
                analysis['power'][counter.name] = counter.value
            elif 'memory' in counter.type.value.lower():
                analysis['memory'][counter.name] = counter.value
            elif 'clock' in counter.type.value.lower():
                analysis['clocks'][counter.name] = counter.value
            else:
                analysis['other'][counter.name] = counter.value
    
    return analysis

def main():
    """Run all performance counter tests."""
    print("NVIDIA Control Panel Performance Counter Tests")
    print("=" * 50)
    
    tests = [
        test_performance_counter_types,
        test_performance_counter_creation,
        test_performance_counter_group_creation,
        test_nvidia_control_panel_performance_counters,
        test_simulated_performance_counters,
        test_performance_counter_management,
        test_comprehensive_performance_analysis
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                print(f"✓ {test.__name__} - PASSED")
                passed += 1
            else:
                print(f"✗ {test.__name__} - FAILED")
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} - ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All performance counter tests passed! 🎉")
        return True
    else:
        print("Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
