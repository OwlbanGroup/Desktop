"""Comprehensive test script for NVIDIA Control Panel integration"""

import sys
import os
import logging
from nvidia_control_panel_complete import (
    NVIDIAControlPanel,
    PowerMode,
    TextureFiltering,
    FrameSyncMode,
    SDIOutputConfig,
    SDIOutputFormat,
    EdgeOverlapConfig,
    SDICaptureConfig,
    ScalingMode,
    VerticalSync,
    AntiAliasingMode,
    AnisotropicFiltering,
    ColorFormat,
    DynamicRange,
    VideoColorRange,
    DeinterlacingMode,
    HDRMode,
    TVFormat,
    VideoEnhancement,
    PhysXProcessor,
    PhysXConfiguration,
    PerformanceCounterType,
    PerformanceCounter,
    PerformanceCounterGroup,
    DisplayMode,
    VideoSettings,
    CustomResolution
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_initialization():
    """Test NVIDIA Control Panel initialization"""
    print("=" * 60)
    print("TESTING INITIALIZATION")
    print("=" * 60)
    
    try:
        nvidia = NVIDIAControlPanel()
        print(f"✓ NVAPI Available: {nvidia.nvapi_available}")
        print(f"✓ GPU Count: {nvidia.gpu_count}")
        print(f"✓ Driver Version: {nvidia.driver_version}")
        print(f"✓ Windows Platform: {nvidia.is_windows}")
        print(f"✓ NVAPI Handle: {nvidia.nvapi_handle is not None}")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_enum_values():
    """Test all enum values"""
    print("\n" + "=" * 60)
    print("TESTING ENUM VALUES")
    print("=" * 60)
    
    try:
        # Test PowerMode enum
        print("PowerMode values:")
        for mode in PowerMode:
            print(f"  {mode.name}: {mode.value}")
        
        # Test TextureFiltering enum
        print("\nTextureFiltering values:")
        for mode in TextureFiltering:
            print(f"  {mode.name}: {mode.value}")
        
        # Test FrameSyncMode enum
        print("\nFrameSyncMode values:")
        for mode in FrameSyncMode:
            print(f"  {mode.name}: {mode.value}")
        
        # Test SDIOutputFormat enum
        print("\nSDIOutputFormat values:")
        for mode in SDIOutputFormat:
            print(f"  {mode.name}: {mode.value}")
        
        print("✓ All enum values validated")
        return True
    except Exception as e:
        print(f"✗ Enum test failed: {e}")
        return False

def test_dataclass_creation():
    """Test dataclass instantiation"""
    print("\n" + "=" * 60)
    print("TESTING DATACLASS CREATION")
    print("=" * 60)
    
    try:
        # Test SDIOutputConfig
        sdi_config = SDIOutputConfig(enabled=True, format=SDIOutputFormat.SDI_10BIT, stream_count=2)
        print(f"✓ SDIOutputConfig: {sdi_config}")
        
        # Test EdgeOverlapConfig
        edge_config = EdgeOverlapConfig(enabled=True, overlap_pixels=5, display_index=1)
        print(f"✓ EdgeOverlapConfig: {edge_config}")
        
        # Test SDICaptureConfig
        capture_config = SDICaptureConfig(enabled=True, stream_count=1, buffer_size_mb=512)
        print(f"✓ SDICaptureConfig: {capture_config}")
        
        # Test VideoSettings with validation
        video_settings = VideoSettings(
            brightness=75,
            contrast=60,
            hue=10,
            saturation=70,
            gamma=1.2,
            edge_enhancement=VideoEnhancement.MEDIUM,
            noise_reduction=VideoEnhancement.LOW,
            dynamic_contrast=VideoEnhancement.HIGH,
            deinterlacing_mode=DeinterlacingMode.ADAPTIVE,
            hdr_mode=HDRMode.ENABLED,
            overscan_percentage=2,
            tv_format=TVFormat.NTSC_M,
            color_range=VideoColorRange.FULL,
            scaling_mode=ScalingMode.ASPECT_RATIO,
            gpu_scaling=True
        )
        print(f"✓ VideoSettings: {video_settings}")
        
        # Test CustomResolution with validation
        custom_res = CustomResolution(
            width=1920,
            height=1080,
            refresh_rate=144,
            color_depth=32,
            timing_standard="CVT",
            scaling="Aspect ratio",
            name="Custom 1080p@144Hz"
        )
        print(f"✓ CustomResolution: {custom_res}")
        
        # Test PhysXConfiguration
        physx_config = PhysXConfiguration(
            enabled=True,
            selected_processor=PhysXProcessor.GPU,
            available_gpus=["GPU0", "GPU1"]
        )
        print(f"✓ PhysXConfiguration: {physx_config}")
        
        # Test PerformanceCounter
        perf_counter = PerformanceCounter(
            name="GPU Utilization",
            type=PerformanceCounterType.GPU_UTILIZATION,
            value=45.5,
            unit="%",
            description="Current GPU utilization percentage"
        )
        print(f"✓ PerformanceCounter: {perf_counter}")
        
        print("✓ All dataclasses created successfully")
        return True
    except Exception as e:
        print(f"✗ Dataclass test failed: {e}")
        return False

def test_gpu_settings_retrieval():
    """Test GPU settings retrieval"""
    print("\n" + "=" * 60)
    print("TESTING GPU SETTINGS RETRIEVAL")
    print("=" * 60)
    
    try:
        nvidia = NVIDIAControlPanel()
        
        # Test getting settings for primary GPU
        settings = nvidia.get_gpu_settings(gpu_index=0)
        print("GPU Settings retrieved:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
        
        print("✓ GPU settings retrieval successful")
        return True
    except Exception as e:
        print(f"✗ GPU settings retrieval failed: {e}")
        return False

def test_settings_validation():
    """Test settings validation"""
    print("\n" + "=" * 60)
    print("TESTING SETTINGS VALIDATION")
    print("=" * 60)
    
    try:
        nvidia = NVIDIAControlPanel()
        
        # Test valid settings
        valid_settings = {
            "power_mode": PowerMode.PREFER_MAX_PERFORMANCE.value,
            "texture_filtering": TextureFiltering.HIGH_QUALITY.value,
            "vertical_sync": VerticalSync.ADAPTIVE.value,
            "anti_aliasing": AntiAliasingMode.MSAA_4X.value,
            "anisotropic_filtering": AnisotropicFiltering.X16.value
        }
        
        validated = nvidia._validate_settings(valid_settings)
        print(f"✓ Valid settings validated: {validated}")
        
        # Test invalid settings
        invalid_settings = {
            "power_mode": "InvalidMode",
            "texture_filtering": "InvalidFiltering"
        }
        
        try:
            nvidia._validate_settings(invalid_settings)
            print("✗ Invalid settings should have raised an error")
            return False
        except ValueError as e:
            print(f"✓ Invalid settings correctly rejected: {e}")
        
        print("✓ Settings validation working correctly")
        return True
    except Exception as e:
        print(f"✗ Settings validation failed: {e}")
        return False

def test_workstation_features():
    """Test workstation feature methods"""
    print("\n" + "=" * 60)
    print("TESTING WORKSTATION FEATURES")
    print("=" * 60)
    
    try:
        nvidia = NVIDIAControlPanel()
        
        # Test frame sync mode
        frame_sync = nvidia.get_frame_sync_mode(gpu_index=0)
        print(f"✓ Frame sync mode: {frame_sync}")
        
        # Test SDI output config
        sdi_config = nvidia.get_sdi_output_config(gpu_index=0)
        print(f"✓ SDI output config: {sdi_config}")
        
        # Test edge overlap config
        edge_config = nvidia.get_edge_overlap_config(display_index=0)
        print(f"✓ Edge overlap config: {edge_config}")
        
        # Test SDI capture config
        capture_config = nvidia.get_sdi_capture_config(gpu_index=0)
        print(f"✓ SDI capture config: {capture_config}")
        
        # Test Mosaic enable/disable
        mosaic_result = nvidia.enable_mosaic(enable=True)
        print(f"✓ Mosaic enable result: {mosaic_result}")
        
        print("✓ Workstation features tested successfully")
        return True
    except Exception as e:
        print(f"✗ Workstation features test failed: {e}")
        return False

def test_video_settings():
    """Test video settings functionality"""
    print("\n" + "=" * 60)
    print("TESTING VIDEO SETTINGS")
    print("=" * 60)
    
    try:
        # Test VideoSettings validation
        try:
            # This should work
            valid_video = VideoSettings(
                brightness=75,
                contrast=60,
                hue=10,
                saturation=70,
                gamma=1.2
            )
            print(f"✓ Valid video settings: {valid_video}")
        except Exception as e:
            print(f"✗ Valid video settings failed: {e}")
            return False
        
        # Test invalid VideoSettings
        try:
            # This should fail
            invalid_video = VideoSettings(brightness=150)  # Out of range
            print("✗ Invalid video settings should have raised an error")
            return False
        except ValueError as e:
            print(f"✓ Invalid video settings correctly rejected: {e}")
        
        print("✓ Video settings validation working correctly")
        return True
    except Exception as e:
        print(f"✗ Video settings test failed: {e}")
        return False

def test_custom_resolution():
    """Test custom resolution functionality"""
    print("\n" + "=" * 60)
    print("TESTING CUSTOM RESOLUTION")
    print("=" * 60)
    
    try:
        # Test valid custom resolution
        try:
            valid_res = CustomResolution(
                width=2560,
                height=1440,
                refresh_rate=165,
                color_depth=32,
                timing_standard="CVT-RB",
                scaling="Aspect ratio"
            )
            print(f"✓ Valid custom resolution: {valid_res}")
        except Exception as e:
            print(f"✗ Valid custom resolution failed: {e}")
            return False
        
        # Test invalid custom resolution
        try:
            invalid_res = CustomResolution(
                width=100,  # Too small
                height=100,  # Too small
                refresh_rate=500  # Too high
            )
            print("✗ Invalid custom resolution should have raised an error")
            return False
        except ValueError as e:
            print(f"✓ Invalid custom resolution correctly rejected: {e}")
        
        print("✓ Custom resolution validation working correctly")
        return True
    except Exception as e:
        print(f"✗ Custom resolution test failed: {e}")
        return False

def test_performance_counters():
    """Test performance counter functionality"""
    print("\n" + "=" * 60)
    print("TESTING PERFORMANCE COUNTERS")
    print("=" * 60)
    
    try:
        # Test PerformanceCounter creation
        counter = PerformanceCounter(
            name="GPU Temperature",
            type=PerformanceCounterType.TEMPERATURE_GPU,
            value=65.5,
            unit="°C",
            description="Current GPU temperature"
        )
        print(f"✓ Performance counter: {counter}")
        
        # Test PerformanceCounterGroup
        group = PerformanceCounterGroup(
            group_name="GPU Metrics",
            counters=[
                PerformanceCounter(
                    name="GPU Utilization",
                    type=PerformanceCounterType.GPU_UTILIZATION,
                    value=45.2,
                    unit="%"
                ),
                PerformanceCounter(
                    name="Memory Usage",
                    type=PerformanceCounterType.MEMORY_USED,
                    value=4096,
                    unit="MB"
                )
            ]
        )
        print(f"✓ Performance counter group: {group.group_name} with {len(group.counters)} counters")
        
        print("✓ Performance counters tested successfully")
        return True
    except Exception as e:
        print(f"✗ Performance counters test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all comprehensive tests"""
    print("STARTING COMPREHENSIVE NVIDIA CONTROL PANEL TEST")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Initialization", test_initialization()))
    test_results.append(("Enum Values", test_enum_values()))
    test_results.append(("Dataclass Creation", test_dataclass_creation()))
    test_results.append(("GPU Settings Retrieval", test_gpu_settings_retrieval()))
    test_results.append(("Settings Validation", test_settings_validation()))
    test_results.append(("Workstation Features", test_workstation_features()))
    test_results.append(("Video Settings", test_video_settings()))
    test_results.append(("Custom Resolution", test_custom_resolution()))
    test_results.append(("Performance Counters", test_performance_counters()))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        if result:
            passed += 1
        else:
            failed += 1
        print(f"{test_name:25} : {status}")
    
    print("-" * 80)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results))*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! NVIDIA Control Panel implementation is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review the implementation for issues.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
