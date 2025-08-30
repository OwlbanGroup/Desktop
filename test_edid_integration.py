"""Integration test for NVIDIA EDID management with existing control panel.

This test verifies that the EDID management module integrates properly
with the existing NVIDIA control panel functionality.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to Python path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from nvidia_edid_management import NVIDIAEDIDManager, EDIDInfo, EDIDOverrideConfig
    from nvidia_control_panel_enhanced import NVIDIAControlPanel, DisplayInfo
    EDID_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    EDID_AVAILABLE = False
    # Create mock classes for testing
    class NVIDIAEDIDManager:
        pass
    class EDIDInfo:
        pass
    class EDIDOverrideConfig:
        pass
    class NVIDIAControlPanel:
        pass
    class DisplayInfo:
        pass

class TestNVIDIAEDIDIntegration(unittest.TestCase):
    """Integration tests for NVIDIA EDID management."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not EDID_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.edid_manager = NVIDIAEDIDManager()
        
        # Mock the control panel since we can't instantiate it without NVIDIA hardware
        self.control_panel = MagicMock(spec=NVIDIAControlPanel)
        
    def test_edid_manager_initialization(self):
        """Test that EDID manager can be initialized alongside control panel."""
        # This test verifies basic compatibility
        self.assertIsInstance(self.edid_manager, NVIDIAEDIDManager)
        self.assertIsInstance(self.control_panel, MagicMock)
        
        # Verify EDID manager has expected methods
        self.assertTrue(hasattr(self.edid_manager, 'read_edid'))
        self.assertTrue(hasattr(self.edid_manager, 'apply_edid'))
        self.assertTrue(hasattr(self.edid_manager, 'override_edid'))
    
    @patch('nvidia_edid_management.NVIDIAEDIDManager.read_edid')
    def test_edid_read_integration(self, mock_read_edid):
        """Test EDID reading integration with mock display data."""
        # Mock a sample EDID response
        sample_edid = self.edid_manager._generate_sample_edid()
        mock_edid_info = self.edid_manager._parse_edid(sample_edid)
        mock_read_edid.return_value = mock_edid_info
        
        # Test reading EDID
        edid_info = self.edid_manager.read_edid(0)
        
        self.assertIsNotNone(edid_info)
        self.assertEqual(edid_info.header.manufacturer_id, 'NV')
        mock_read_edid.assert_called_once_with(0, 0)
    
    @patch('nvidia_edid_management.NVIDIAEDIDManager.apply_edid')
    def test_edid_apply_integration(self, mock_apply_edid):
        """Test EDID application integration."""
        mock_apply_edid.return_value = True
        
        sample_edid = self.edid_manager._generate_sample_edid()
        result = self.edid_manager.apply_edid(sample_edid, 0)
        
        self.assertTrue(result)
        mock_apply_edid.assert_called_once_with(sample_edid, 0, 0)
    
    def test_edid_override_config_compatibility(self):
        """Test that EDID override config works with expected parameters."""
        config = EDIDOverrideConfig(
            display_index=0,
            custom_resolutions=[
                {"width": 1920, "height": 1080, "refresh_rate": 60},
                {"width": 2560, "height": 1440, "refresh_rate": 144}
            ],
            force_resolution={"width": 3840, "height": 2160, "refresh_rate": 60},
            override_timings=True
        )
        
        self.assertEqual(config.display_index, 0)
        self.assertEqual(len(config.custom_resolutions), 2)
        self.assertEqual(config.force_resolution["width"], 3840)
        self.assertTrue(config.override_timings)
    
    @patch('nvidia_edid_management.NVIDIAEDIDManager.override_edid')
    def test_edid_override_integration(self, mock_override_edid):
        """Test EDID override integration."""
        mock_override_edid.return_value = True
        
        config = EDIDOverrideConfig(display_index=0)
        result = self.edid_manager.override_edid(config)
        
        self.assertTrue(result)
        mock_override_edid.assert_called_once_with(config, 0)
    
    def test_edid_file_operations(self):
        """Test EDID file operations work correctly."""
        import tempfile
        
        # Generate sample EDID
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
            self.assertEqual(len(imported_edid.raw_data), 128)
            
            # Test validation
            validation_result = self.edid_manager.validate_edid_file(temp_path)
            self.assertTrue(validation_result)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_edid_summary_generation(self):
        """Test EDID summary generation works correctly."""
        sample_edid = self.edid_manager._generate_sample_edid()
        edid_info = self.edid_manager._parse_edid(sample_edid)
        
        summary = self.edid_manager.get_edid_summary(edid_info)
        
        self.assertIsInstance(summary, dict)
        self.assertIn('manufacturer', summary)
        self.assertIn('product_code', summary)
        self.assertIn('edid_version', summary)
        self.assertIn('preferred_resolution', summary)
        self.assertIn('color_depth', summary)
    
    def test_error_handling(self):
        """Test error handling in EDID operations."""
        # Test with invalid EDID data
        invalid_edid = b'\x00' * 50  # Too short
        validation_result = self.edid_manager._validate_edid(invalid_edid)
        self.assertFalse(validation_result)
        
        # Test with None input
        with self.assertRaises((ValueError, TypeError)):
            self.edid_manager._parse_edid(None)

class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform compatibility of EDID management."""
    
    def setUp(self):
        if not EDID_AVAILABLE:
            self.skipTest("Required modules not available")
        self.edid_manager = NVIDIAEDIDManager()
    
    def test_platform_detection(self):
        """Test that platform detection works correctly."""
        self.assertIsInstance(self.edid_manager.is_windows, bool)
        self.assertIsInstance(self.edid_manager.nvapi_available, bool)
        
        # Platform detection should be consistent with actual platform
        import platform
        actual_platform = platform.system()
        if actual_platform == "Windows":
            self.assertTrue(self.edid_manager.is_windows)
        else:
            self.assertFalse(self.edid_manager.is_windows)
    
    def test_platform_specific_methods(self):
        """Test that platform-specific methods handle different scenarios."""
        # These methods should handle cases where platform-specific
        # functionality is not available gracefully
        
        if not self.edid_manager.is_windows:
            # On non-Windows, registry methods should return None
            result = self.edid_manager._read_edid_via_registry(0)
            self.assertIsNone(result)
        
        if not self.edid_manager.nvapi_available:
            # Without NVAPI, NVAPI methods should return None/False
            result = self.edid_manager._read_edid_via_nvapi(0, 0)
            self.assertIsNone(result)
            
            apply_result = self.edid_manager._apply_edid_via_nvapi(b'\x00' * 128, 0, 0)
            self.assertFalse(apply_result)

def run_integration_demo():
    """Run a comprehensive integration demo."""
    print("Running NVIDIA EDID Integration Demo")
    print("=" * 50)
    
    if not EDID_AVAILABLE:
        print("ERROR: Required modules not available")
        return
    
    edid_manager = NVIDIAEDIDManager()
    
    print(f"Platform: {'Windows' if edid_manager.is_windows else 'Non-Windows'}")
    print(f"NVAPI Available: {edid_manager.nvapi_available}")
    print()
    
    # Test EDID generation and parsing
    print("1. EDID Generation and Parsing:")
    sample_edid = edid_manager._generate_sample_edid()
    print(f"   Generated EDID size: {len(sample_edid)} bytes")
    
    is_valid = edid_manager._validate_edid(sample_edid)
    print(f"   EDID validation: {'PASS' if is_valid else 'FAIL'}")
    
    if is_valid:
        edid_info = edid_manager._parse_edid(sample_edid)
        print(f"   Manufacturer: {edid_info.header.manufacturer_id}")
        print(f"   Product Code: {edid_info.header.product_code}")
    
    # Test file operations
    print("\n2. File Operations:")
    import tempfile
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
    
    # Test override configuration
    print("\n3. Override Configuration:")
    config = EDIDOverrideConfig(
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
    
    print("\n4. Platform Compatibility:")
    print(f"   Windows detection: {edid_manager.is_windows}")
    print(f"   NVAPI detection: {edid_manager.nvapi_available}")
    
    if edid_manager.is_windows:
        print("   Windows-specific features available")
    else:
        print("   Non-Windows platform detected")
    
    print("\nIntegration demo completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    # Run unit tests
    print("Running integration tests...")
    unittest.main(exit=False, verbosity=2)
    
    print("\n" + "="*50)
    print("RUNNING INTEGRATION DEMO")
    print("="*50)
    
    # Run integration demo
    run_integration_demo()
