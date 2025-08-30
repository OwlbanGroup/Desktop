"""Test script for NVIDIA EDID Management functionality.

This script tests the EDID reading, parsing, and management capabilities
of the NVIDIA EDID management module.
"""

import unittest
import tempfile
import os
from nvidia_edid_management import (
    NVIDIAEDIDManager,
    EDIDInfo,
    EDIDHeader,
    EDIDVersion,
    EDIDOverrideConfig,
    get_nvidia_edid_manager,
    create_edid_override_config
)

class TestNVIDIAEDIDManager(unittest.TestCase):
    """Test cases for NVIDIA EDID Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.edid_manager = NVIDIAEDIDManager()
    
    def test_initialization(self):
        """Test that the EDID manager initializes correctly."""
        self.assertIsInstance(self.edid_manager, NVIDIAEDIDManager)
        self.assertIsInstance(self.edid_manager.is_windows, bool)
        self.assertIsInstance(self.edid_manager.nvapi_available, bool)
    
    def test_edid_validation_valid(self):
        """Test EDID validation with valid data."""
        # Create valid EDID data (header + checksum)
        valid_edid = b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' + b'\x00' * 119
        # Set checksum to make sum % 256 = 0
        valid_edid = valid_edid[:127] + bytes([256 - sum(valid_edid[:127]) % 256])
        
        self.assertTrue(self.edid_manager._validate_edid(valid_edid))
    
    def test_edid_validation_invalid_header(self):
        """Test EDID validation with invalid header."""
        invalid_edid = b'\x00\x00\x00\x00\x00\x00\x00\x00' + b'\x00' * 120
        self.assertFalse(self.edid_manager._validate_edid(invalid_edid))
    
    def test_edid_validation_invalid_checksum(self):
        """Test EDID validation with invalid checksum."""
        invalid_edid = b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' + b'\x01' * 120
        self.assertFalse(self.edid_manager._validate_edid(invalid_edid))
    
    def test_edid_validation_short_data(self):
        """Test EDID validation with data that's too short."""
        short_edid = b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' + b'\x00' * 50
        self.assertFalse(self.edid_manager._validate_edid(short_edid))
    
    def test_manufacturer_id_decoding(self):
        """Test manufacturer ID decoding."""
        # Test with known manufacturer codes
        test_cases = [
            (b'\x4E\x56', 'NV'),  # NVIDIA
            (b'\x41\x55', 'AU'),  # Apple
            (b'\x44\x45', 'DE'),  # Dell
        ]
        
        for manufacturer_bytes, expected_prefix in test_cases:
            result = self.edid_manager._decode_manufacturer_id(manufacturer_bytes)
            self.assertTrue(result.startswith(expected_prefix))
    
    def test_edid_parsing(self):
        """Test EDID parsing functionality."""
        # Generate sample EDID data
        sample_edid = self.edid_manager._generate_sample_edid()
        
        # Parse the EDID
        edid_info = self.edid_manager._parse_edid(sample_edid)
        
        # Verify the parsed structure
        self.assertIsInstance(edid_info, EDIDInfo)
        self.assertIsInstance(edid_info.header, EDIDHeader)
        self.assertEqual(len(edid_info.raw_data), 128)
        self.assertEqual(edid_info.header.manufacturer_id, 'NV')
        self.assertEqual(edid_info.header.product_code, 1)
    
    def test_edid_summary_generation(self):
        """Test EDID summary generation."""
        sample_edid = self.edid_manager._generate_sample_edid()
        edid_info = self.edid_manager._parse_edid(sample_edid)
        
        summary = self.edid_manager.get_edid_summary(edid_info)
        
        self.assertIsInstance(summary, dict)
        self.assertIn('manufacturer', summary)
        self.assertIn('product_code', summary)
        self.assertIn('edid_version', summary)
        self.assertIn('preferred_resolution', summary)
    
    def test_file_operations(self):
        """Test EDID file import/export operations."""
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
            self.assertIsInstance(imported_edid, EDIDInfo)
            self.assertEqual(len(imported_edid.raw_data), 128)
            
            # Test validation
            validation_result = self.edid_manager.validate_edid_file(temp_path)
            self.assertTrue(validation_result)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_override_config_creation(self):
        """Test EDID override configuration creation."""
        config = create_edid_override_config(
            display_index=0,
            custom_resolutions=[{"width": 1920, "height": 1080, "refresh_rate": 60}],
            force_resolution={"width": 2560, "height": 1440, "refresh_rate": 144},
            override_timings=True,
            preserve_original=False
        )
        
        self.assertIsInstance(config, EDIDOverrideConfig)
        self.assertEqual(config.display_index, 0)
        self.assertEqual(len(config.custom_resolutions), 1)
        self.assertEqual(config.force_resolution["width"], 2560)
        self.assertTrue(config.override_timings)
        self.assertFalse(config.preserve_original)
    
    def test_factory_functions(self):
        """Test factory functions."""
        # Test get_nvidia_edid_manager
        manager = get_nvidia_edid_manager()
        self.assertIsInstance(manager, NVIDIAEDIDManager)
        
        # Test create_edid_override_config
        config = create_edid_override_config(1)
        self.assertIsInstance(config, EDIDOverrideConfig)
        self.assertEqual(config.display_index, 1)

class TestEDIDDetailedTimingParsing(unittest.TestCase):
    """Test cases for detailed EDID timing parsing."""
    
    def setUp(self):
        self.edid_manager = NVIDIAEDIDManager()
    
    def test_detailed_timing_parsing(self):
        """Test parsing of detailed timing blocks."""
        # Create a sample detailed timing block
        timing_block = bytes([
            0x5A, 0x25,  # Pixel clock: 148.5 MHz
            0x80, 0x20,  # Horizontal active: 1920
            0x38, 0x40,  # Vertical active: 1080
            0x00, 0x30,  # Horizontal sync offset and pulse
            0x70, 0x13,  # Vertical sync offset and pulse
            0x00, 0x3E,  # Horizontal and vertical image size
            0x42, 0x00,  # Horizontal and vertical border
            0x00, 0x00   # Flags and stereo mode
        ])
        
        timing = self.edid_manager._parse_detailed_timing_block(timing_block)
        
        self.assertEqual(timing.pixel_clock, 148500)  # 148.5 MHz in kHz
        self.assertEqual(timing.horizontal_active, 1920)
        self.assertEqual(timing.vertical_active, 1080)
        self.assertFalse(timing.interlaced)

class TestPlatformSpecificMethods(unittest.TestCase):
    """Test platform-specific EDID methods."""
    
    def setUp(self):
        self.edid_manager = NVIDIAEDIDManager()
    
    def test_nvapi_methods(self):
        """Test NVAPI-related methods (will be stubs without NVAPI)."""
        # These should return None or False when NVAPI is not available
        if not self.edid_manager.nvapi_available:
            result = self.edid_manager._read_edid_via_nvapi(0, 0)
            self.assertIsNone(result)
            
            apply_result = self.edid_manager._apply_edid_via_nvapi(b'\x00' * 128, 0, 0)
            self.assertFalse(apply_result)
    
    def test_registry_methods(self):
        """Test registry methods (will be stubs for testing)."""
        # On Windows, these might return None if no displays are connected
        if self.edid_manager.is_windows:
            result = self.edid_manager._read_edid_via_registry(0)
            # Could be None if no EDID in registry, which is acceptable
    
    def test_system_methods(self):
        """Test system methods (will be stubs for non-Windows)."""
        if not self.edid_manager.is_windows:
            result = self.edid_manager._read_edid_via_system(0)
            self.assertIsNone(result)

def run_comprehensive_test():
    """Run comprehensive EDID management tests."""
    print("Running comprehensive EDID management tests...")
    print("=" * 50)
    
    # Create EDID manager
    edid_manager = NVIDIAEDIDManager()
    print(f"Platform: {platform.system()}")
    print(f"NVAPI Available: {edid_manager.nvapi_available}")
    print(f"Windows: {edid_manager.is_windows}")
    print()
    
    # Test EDID generation and parsing
    print("1. Testing EDID generation and parsing...")
    sample_edid = edid_manager._generate_sample_edid()
    print(f"Generated EDID size: {len(sample_edid)} bytes")
    
    # Validate EDID
    is_valid = edid_manager._validate_edid(sample_edid)
    print(f"EDID validation: {'PASS' if is_valid else 'FAIL'}")
    
    if is_valid:
        # Parse EDID
        edid_info = edid_manager._parse_edid(sample_edid)
        print(f"Manufacturer: {edid_info.header.manufacturer_id}")
        print(f"Product Code: {edid_info.header.product_code}")
        print(f"EDID Version: {edid_info.header.edid_version.value}")
        
        # Get summary
        summary = edid_manager.get_edid_summary(edid_info)
        print(f"Preferred Resolution: {summary['preferred_resolution']}")
        print(f"Color Depth: {summary['color_depth']}-bit")
        print(f"HDR Support: {summary['hdr_support']}")
        print(f"Audio Support: {summary['audio_support']}")
    
    print()
    print("2. Testing file operations...")
    
    # Test file operations
    with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
        temp_path = temp_file.name
    
    try:
        if is_valid:
            # Export to file
            export_result = edid_manager.export_edid_to_file(edid_info, temp_path)
            print(f"EDID export: {'PASS' if export_result else 'FAIL'}")
            
            # Import from file
            imported_edid = edid_manager.import_edid_from_file(temp_path)
            print(f"EDID import: {'PASS' if imported_edid else 'FAIL'}")
            
            # Validate file
            validation_result = edid_manager.validate_edid_file(temp_path)
            print(f"File validation: {'PASS' if validation_result else 'FAIL'}")
        else:
            print("Skipping file operations due to invalid EDID")
            
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    print()
    print("3. Testing override configuration...")
    
    # Test override configuration
    config = create_edid_override_config(
        display_index=0,
        custom_resolutions=[
            {"width": 1920, "height": 1080, "refresh_rate": 60},
            {"width": 2560, "height": 1440, "refresh_rate": 144}
        ],
        force_resolution={"width": 3840, "height": 2160, "refresh_rate": 60},
        override_timings=True
    )
    
    print(f"Override config created for display {config.display_index}")
    print(f"Custom resolutions: {len(config.custom_resolutions)}")
    print(f"Force resolution: {config.force_resolution['width']}x{config.force_resolution['height']}")
    print(f"Override timings: {config.override_timings}")
    
    print()
    print("4. Testing factory functions...")
    
    # Test factory functions
    factory_manager = get_nvidia_edid_manager()
    print(f"Factory manager created: {isinstance(factory_manager, NVIDIAEDIDManager)}")
    
    factory_config = create_edid_override_config(1)
    print(f"Factory config created for display {factory_config.display_index}")
    
    print()
    print("Comprehensive test completed!")
    print("=" * 50)

if __name__ == "__main__":
    # Run unit tests
    unittest.main(exit=False, verbosity=2)
    
    print("\n" + "="*50)
    print("RUNNING COMPREHENSIVE DEMO")
    print("="*50)
    
    # Run comprehensive demo
    run_comprehensive_test()
