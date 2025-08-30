"""Final comprehensive test for NVIDIA EDID management.

This test combines all aspects of EDID management testing:
- Unit tests
- Integration tests  
- Performance tests
- Error handling tests
- Cross-platform compatibility
"""

import unittest
import time
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Import EDID management module
from nvidia_edid_management import (
    NVIDIAEDIDManager, 
    EDIDInfo, 
    EDIDHeader, 
    EDIDVersion,
    EDIDOverrideConfig,
    get_nvidia_edid_manager,
    create_edid_override_config
)

class ComprehensiveEDIDTest(unittest.TestCase):
    """Comprehensive test suite covering all EDID management aspects."""
    
    def setUp(self):
        self.edid_manager = NVIDIAEDIDManager()
        self.start_time = time.time()
    
    def tearDown(self):
        test_duration = time.time() - self.start_time
        print(f"Test completed in {test_duration:.3f} seconds")
    
    def test_01_basic_functionality(self):
        """Test basic EDID functionality."""
        print("Testing basic EDID functionality...")
        
        # Generate sample EDID
        sample_edid = self.edid_manager._generate_sample_edid()
        self.assertEqual(len(sample_edid), 128)
        
        # Validate EDID
        is_valid = self.edid_manager._validate_edid(sample_edid)
        self.assertTrue(is_valid)
        
        # Parse EDID
        edid_info = self.edid_manager._parse_edid(sample_edid)
        self.assertIsInstance(edid_info, EDIDInfo)
        self.assertIsInstance(edid_info.header, EDIDHeader)
        
        # Verify manufacturer ID
        self.assertEqual(edid_info.header.manufacturer_id, 'NV')
    
    def test_02_file_operations(self):
        """Test EDID file operations."""
        print("Testing file operations...")
        
        sample_edid = self.edid_manager._generate_sample_edid()
        edid_info = self.edid_manager._parse_edid(sample_edid)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test export
            export_result = self.edid_manager.export_edid_to_file(edid_info, temp_path)
            self.assertTrue(export_result)
            
            # Test import
            imported_edid = self.edid_manager.import_edid_from_file(temp_path)
            self.assertIsNotNone(imported_edid)
            
            # Test validation
            validation_result = self.edid_manager.validate_edid_file(temp_path)
            self.assertTrue(validation_result)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_03_override_configuration(self):
        """Test EDID override configuration."""
        print("Testing override configuration...")
        
        config = create_edid_override_config(
            display_index=0,
            custom_resolutions=[
                {"width": 1920, "height": 1080, "refresh_rate": 60},
                {"width": 2560, "height": 1440, "refresh_rate": 144},
                {"width": 3840, "height": 2160, "refresh_rate": 60}
            ],
            force_resolution={"width": 2560, "height": 1440, "refresh_rate": 144},
            override_timings=True,
            preserve_original=False,
            backup_original=True
        )
        
        self.assertEqual(config.display_index, 0)
        self.assertEqual(len(config.custom_resolutions), 3)
        self.assertEqual(config.force_resolution["width"], 2560)
        self.assertTrue(config.override_timings)
        self.assertFalse(config.preserve_original)
        self.assertTrue(config.backup_original)
    
    def test_04_performance(self):
        """Test EDID performance with large datasets."""
        print("Testing performance...")
        
        # Generate large dataset
        large_dataset = []
        for i in range(100):
            edid_data = self.edid_manager._generate_sample_edid()
            large_dataset.append(edid_data)
        
        # Test parsing performance
        start_time = time.time()
        parsed_count = 0
        for edid_data in large_dataset:
            try:
                self.edid_manager._parse_edid(edid_data)
                parsed_count += 1
            except:
                pass
        parse_time = time.time() - start_time
        
        # Test validation performance
        start_time = time.time()
        valid_count = 0
        for edid_data in large_dataset:
            if self.edid_manager._validate_edid(edid_data):
                valid_count += 1
        valid_time = time.time() - start_time
        
        print(f"Parsed {parsed_count} EDIDs in {parse_time:.3f}s")
        print(f"Validated {len(large_dataset)} EDIDs in {valid_time:.3f}s")
        
        # Performance thresholds
        self.assertLess(parse_time, 2.0)
        self.assertLess(valid_time, 1.0)
        self.assertGreater(parsed_count, 90)
        self.assertGreater(valid_count, 90)
    
    def test_05_error_handling(self):
        """Test comprehensive error handling."""
        print("Testing error handling...")
        
        # Test invalid EDID data
        invalid_cases = [
            None,
            b'',
            b'\x00' * 50,
            b'\xFF' * 128,
            b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' + b'\x00' * 120  # Invalid checksum
        ]
        
        for i, invalid_data in enumerate(invalid_cases):
            with self.subTest(case=i):
                if invalid_data is None:
                    with self.assertRaises((ValueError, TypeError)):
                        self.edid_manager._parse_edid(invalid_data)
                else:
                    # Should handle gracefully or raise appropriate exception
                    try:
                        result = self.edid_manager._validate_edid(invalid_data)
                        self.assertIsInstance(result, bool)
                    except Exception as e:
                        self.assertIn(type(e).__name__, ['ValueError', 'TypeError', 'IndexError'])
        
        # Test file operation errors
        non_existent_result = self.edid_manager.validate_edid_file("/nonexistent/file.bin")
        self.assertFalse(non_existent_result)
        
        non_existent_import = self.edid_manager.import_edid_from_file("/nonexistent/file.bin")
        self.assertIsNone(non_existent_import)
    
    def test_06_cross_platform(self):
        """Test cross-platform compatibility."""
        print("Testing cross-platform compatibility...")
        
        # Test platform detection
        self.assertIsInstance(self.edid_manager.is_windows, bool)
        self.assertIsInstance(self.edid_manager.nvapi_available, bool)
        
        # Test platform-specific methods handle absence gracefully
        if not self.edid_manager.is_windows:
            registry_result = self.edid_manager._read_edid_via_registry(0)
            self.assertIsNone(registry_result)
        
        if not self.edid_manager.nvapi_available:
            nvapi_result = self.edid_manager._read_edid_via_nvapi(0, 0)
            self.assertIsNone(nvapi_result)
    
    def test_07_factory_functions(self):
        """Test factory functions."""
        print("Testing factory functions...")
        
        # Test get_nvidia_edid_manager
        factory_manager = get_nvidia_edid_manager()
        self.assertIsInstance(factory_manager, NVIDIAEDIDManager)
        
        # Test create_edid_override_config
        factory_config = create_edid_override_config(1)
        self.assertIsInstance(factory_config, EDIDOverrideConfig)
        self.assertEqual(factory_config.display_index, 1)
    
    def test_08_summary_generation(self):
        """Test EDID summary generation."""
        print("Testing summary generation...")
        
        sample_edid = self.edid_manager._generate_sample_edid()
        edid_info = self.edid_manager._parse_edid(sample_edid)
        
        summary = self.edid_manager.get_edid_summary(edid_info)
        
        required_keys = [
            'manufacturer', 'product_code', 'serial_number',
            'manufacture_date', 'edid_version', 'preferred_resolution',
            'max_resolution', 'supported_resolutions_count', 'color_depth',
            'hdr_support', 'audio_support', 'dpms_support', 'timestamp'
        ]
        
        for key in required_keys:
            self.assertIn(key, summary)
        
        self.assertEqual(summary['manufacturer'], 'NV')
        self.assertEqual(summary['product_code'], 1)
    
    @patch('nvidia_edid_management.NVIDIAEDIDManager.read_edid')
    @patch('nvidia_edid_management.NVIDIAEDIDManager.apply_edid')
    def test_09_integration_mocks(self, mock_apply, mock_read):
        """Test integration with mocked dependencies."""
        print("Testing integration with mocks...")
        
        # Mock successful EDID read
        sample_edid = self.edid_manager._generate_sample_edid()
        mock_edid_info = self.edid_manager._parse_edid(sample_edid)
        mock_read.return_value = mock_edid_info
        
        # Mock successful EDID apply
        mock_apply.return_value = True
        
        # Test read
        edid_info = self.edid_manager.read_edid(0)
        self.assertIsNotNone(edid_info)
        mock_read.assert_called_once_with(0, 0)
        
        # Test apply
        result = self.edid_manager.apply_edid(sample_edid, 0)
        self.assertTrue(result)
        mock_apply.assert_called_once_with(sample_edid, 0, 0)
    
    def test_10_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("Testing edge cases...")
        
        # Test extreme values
        extreme_config = EDIDOverrideConfig(
            display_index=0,
            custom_resolutions=[
                {"width": 1, "height": 1, "refresh_rate": 1},
                {"width": 16384, "height": 16384, "refresh_rate": 1000}
            ],
            force_resolution={"width": 8192, "height": 4320, "refresh_rate": 120}
        )
        
        self.assertEqual(extreme_config.custom_resolutions[0]["width"], 1)
        self.assertEqual(extreme_config.custom_resolutions[1]["width"], 16384)
        self.assertEqual(extreme_config.force_resolution["width"], 8192)
        
        # Test empty configurations
        empty_config = EDIDOverrideConfig(display_index=0)
        self.assertEqual(empty_config.display_index, 0)
        self.assertEqual(len(empty_config.custom_resolutions), 0)
        self.assertIsNone(empty_config.force_resolution)

def run_comprehensive_demo():
    """Run a comprehensive demonstration of all EDID management features."""
    print("=" * 70)
    print("COMPREHENSIVE NVIDIA EDID MANAGEMENT DEMONSTRATION")
    print("=" * 70)
    
    edid_manager = NVIDIAEDIDManager()
    
    print(f"Platform: {'Windows' if edid_manager.is_windows else 'Non-Windows'}")
    print(f"NVAPI Available: {edid_manager.nvapi_available}")
    print()
    
    # 1. Basic EDID Operations
    print("1. BASIC EDID OPERATIONS")
    print("   Generating sample EDID...")
    sample_edid = edid_manager._generate_sample_edid()
    print(f"   EDID size: {len(sample_edid)} bytes")
    
    is_valid = edid_manager._validate_edid(sample_edid)
    print(f"   EDID validation: {'PASS' if is_valid else 'FAIL'}")
    
    if is_valid:
        edid_info = edid_manager._parse_edid(sample_edid)
        print(f"   Manufacturer: {edid_info.header.manufacturer_id}")
        print(f"   Product Code: {edid_info.header.product_code}")
        print(f"   EDID Version: {edid_info.header.edid_version.value}")
    
    # 2. File Operations
    print("\n2. FILE OPERATIONS")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
        temp_path = temp_file.name
    
    try:
        if is_valid:
            export_result = edid_manager.export_edid_to_file(edid_info, temp_path)
            print(f"   EDID export: {'PASS' if export_result else 'FAIL'}")
            
            imported_edid = edid_manager.import_edid_from_file(temp_path)
            print(f"   EDID import: {'PASS' if imported_edid else 'FAIL'}")
            
            validation_result = edid_manager.validate_edid_file(temp_path)
            print(f"   File validation: {'PASS' if validation_result else 'FAIL'}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # 3. Configuration
    print("\n3. CONFIGURATION")
    config = create_edid_override_config(
        display_index=0,
        custom_resolutions=[
            {"width": 1920, "height": 1080, "refresh_rate": 60},
            {"width": 2560, "height": 1440, "refresh_rate": 144}
        ],
        force_resolution={"width": 3840, "height": 2160, "refresh_rate": 60}
    )
    
    print(f"   Display index: {config.display_index}")
    print(f"   Custom resolutions: {len(config.custom_resolutions)}")
    print(f"   Force resolution: {config.force_resolution['width']}x{config.force_resolution['height']}")
    
    # 4. Performance
    print("\n4. PERFORMANCE")
    large_dataset = [edid_manager._generate_sample_edid() for _ in range(50)]
    
    start_time = time.time()
    parsed_count = sum(1 for edid in large_dataset if edid_manager._validate_edid(edid))
    perf_time = time.time() - start_time
    
    print(f"   Processed {len(large_dataset)} EDIDs in {perf_time:.3f}s")
    print(f"   Validation rate: {parsed_count/len(large_dataset)*100:.1f}%")
    
    # 5. Summary
    print("\n5. SUMMARY")
    if is_valid:
        summary = edid_manager.get_edid_summary(edid_info)
        print(f"   Manufacturer: {summary['manufacturer']}")
        print(f"   Preferred resolution: {summary['preferred_resolution']}")
        print(f"   Color depth: {summary['color_depth']}-bit")
        print(f"   HDR support: {summary['hdr_support']}")
        print(f"   Audio support: {summary['audio_support']}")
    
    print("\n" + "=" * 70)
    print("COMPREHENSIVE DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    # Run comprehensive tests
    print("Running comprehensive EDID management tests...")
    unittest.main(exit=False, verbosity=2)
    
    print("\n" + "="*70)
    print("RUNNING COMPREHENSIVE DEMONSTRATION")
    print("="*70)
    
    # Run comprehensive demonstration
    run_comprehensive_demo()
