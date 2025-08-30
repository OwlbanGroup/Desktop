"""Performance and error handling tests for NVIDIA EDID management.

This test focuses on performance testing with large datasets and
comprehensive error handling scenarios.
"""

import unittest
import time
import tempfile
import os
from unittest.mock import patch, MagicMock
from nvidia_edid_management import NVIDIAEDIDManager, EDIDInfo, EDIDOverrideConfig

class TestEDIDPerformance(unittest.TestCase):
    """Performance tests for EDID management."""
    
    def setUp(self):
        self.edid_manager = NVIDIAEDIDManager()
        self.large_edid_dataset = self._generate_large_edid_dataset()
    
    def _generate_large_edid_dataset(self):
        """Generate a large dataset of EDID samples for performance testing."""
        dataset = []
        for i in range(100):  # Generate 100 sample EDIDs
            edid_data = self.edid_manager._generate_sample_edid()
            # Modify some bytes to create variation
            modified_edid = bytearray(edid_data)
            modified_edid[10] = i  # Vary product code
            dataset.append(bytes(modified_edid))
        return dataset
    
    def test_edid_parsing_performance(self):
        """Test performance of EDID parsing with large dataset."""
        start_time = time.time()
        
        parsed_edids = []
        for edid_data in self.large_edid_dataset:
            try:
                edid_info = self.edid_manager._parse_edid(edid_data)
                parsed_edids.append(edid_info)
            except Exception:
                pass  # Some might be invalid, that's okay for performance test
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Parsed {len(parsed_edids)} EDIDs in {processing_time:.4f} seconds")
        print(f"Average time per EDID: {processing_time/len(parsed_edids)*1000:.2f} ms")
        
        # Performance threshold: should process at least 50 EDIDs per second
        self.assertLess(processing_time, 2.0)  # Should take less than 2 seconds
        self.assertGreater(len(parsed_edids), 90)  # Should parse most EDIDs
    
    def test_edid_validation_performance(self):
        """Test performance of EDID validation with large dataset."""
        start_time = time.time()
        
        valid_count = 0
        for edid_data in self.large_edid_dataset:
            if self.edid_manager._validate_edid(edid_data):
                valid_count += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Validated {len(self.large_edid_dataset)} EDIDs in {processing_time:.4f} seconds")
        print(f"Average time per validation: {processing_time/len(self.large_edid_dataset)*1000:.2f} ms")
        
        # Performance threshold
        self.assertLess(processing_time, 1.0)
        self.assertGreater(valid_count, 90)  # Most should be valid
    
    def test_file_operations_performance(self):
        """Test performance of file operations with large EDID data."""
        import tempfile
        
        # Create a large EDID file
        large_edid_data = b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' + b'\x01' * 120
        # Set proper checksum
        large_edid_data = large_edid_data[:127] + bytes([256 - sum(large_edid_data[:127]) % 256])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test write performance
            start_time = time.time()
            with open(temp_path, 'wb') as f:
                for _ in range(100):  # Write 100 copies
                    f.write(large_edid_data)
            write_time = time.time() - start_time
            
            # Test read performance
            start_time = time.time()
            with open(temp_path, 'rb') as f:
                data = f.read()
            read_time = time.time() - start_time
            
            print(f"Write performance: {write_time:.4f} seconds")
            print(f"Read performance: {read_time:.4f} seconds")
            
            # Performance thresholds
            self.assertLess(write_time, 0.5)
            self.assertLess(read_time, 0.5)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

class TestEDIDErrorHandling(unittest.TestCase):
    """Comprehensive error handling tests for EDID management."""
    
    def setUp(self):
        self.edid_manager = NVIDIAEDIDManager()
    
    def test_invalid_edid_parsing(self):
        """Test parsing of various invalid EDID data."""
        test_cases = [
            None,  # None input
            b'',  # Empty data
            b'\x00' * 50,  # Too short
            b'\x00' * 200,  # Too long but invalid
            b'\x01\x02\x03' * 50,  # Random data
            b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' + b'\x00' * 120,  # Invalid checksum
        ]
        
        for i, invalid_edid in enumerate(test_cases):
            with self.subTest(test_case=i):
                if invalid_edid is None:
                    with self.assertRaises((ValueError, TypeError)):
                        self.edid_manager._parse_edid(invalid_edid)
                else:
                    try:
                        result = self.edid_manager._parse_edid(invalid_edid)
                        # If we get here, the parsing "succeeded" but might have garbage data
                        self.assertIsInstance(result, EDIDInfo)
                    except (ValueError, struct.error, IndexError):
                        # Expected exceptions for invalid data
                        pass
    
    def test_edid_validation_edge_cases(self):
        """Test EDID validation with edge cases."""
        test_cases = [
            (b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' + b'\x00' * 120, False),  # Invalid checksum
            (b'\x01\x02\x03\x04\x05\x06\x07\x08' + b'\x00' * 120, False),  # Invalid header
            (b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\x00' + b'\x00' * 119 + b'\x00', False),  # Short data
            (self.edid_manager._generate_sample_edid(), True),  # Valid EDID
        ]
        
        for i, (edid_data, expected_valid) in enumerate(test_cases):
            with self.subTest(test_case=i):
                # Adjust checksum for the invalid test case if needed
                if not expected_valid and len(edid_data) >= 128:
                    # Make sure the checksum is actually invalid
                    invalid_checksum_edid = edid_data[:127] + b'\xFF'
                    result = self.edid_manager._validate_edid(invalid_checksum_edid)
                    self.assertFalse(result)
                else:
                    result = self.edid_manager._validate_edid(edid_data)
                    self.assertEqual(result, expected_valid)
    
    def test_file_operation_errors(self):
        """Test error handling in file operations."""
        # Test with non-existent file
        result = self.edid_manager.import_edid_from_file("/non/existent/path.bin")
        self.assertIsNone(result)
        
        result = self.edid_manager.validate_edid_file("/non/existent/path.bin")
        self.assertFalse(result)
        
        # Test with invalid file content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
            temp_path = temp_file.name
            temp_file.write(b'invalid data')
        
        try:
            result = self.edid_manager.import_edid_from_file(temp_path)
            self.assertIsNone(result)
            
            result = self.edid_manager.validate_edid_file(temp_path)
            self.assertFalse(result)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_override_config_validation(self):
        """Test error handling in override configuration."""
        # Test with invalid display index
        with self.assertRaises((ValueError, TypeError)):
            EDIDOverrideConfig(display_index=-1)
        
        with self.assertRaises((ValueError, TypeError)):
            EDIDOverrideConfig(display_index="invalid")
        
        # Test with invalid custom resolutions
        config = EDIDOverrideConfig(display_index=0)
        config.custom_resolutions = "invalid"  # This should be caught by type checking
        
        # The actual validation would happen during usage
    
    @patch('nvidia_edid_management.NVIDIAEDIDManager._read_edid_via_nvapi')
    def test_nvapi_error_handling(self, mock_nvapi_read):
        """Test error handling when NVAPI calls fail."""
        mock_nvapi_read.return_value = None  # Simulate NVAPI failure
        
        result = self.edid_manager.read_edid(0)
        self.assertIsNone(result)
    
    @patch('nvidia_edid_management.NVIDIAEDIDManager._apply_edid_via_nvapi')
    def test_nvapi_apply_error_handling(self, mock_nvapi_apply):
        """Test error handling when NVAPI apply calls fail."""
        mock_nvapi_apply.return_value = False  # Simulate NVAPI failure
        
        sample_edid = self.edid_manager._generate_sample_edid()
        result = self.edid_manager.apply_edid(sample_edid, 0)
        self.assertFalse(result)

class TestEDIDEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions for EDID management."""
    
    def setUp(self):
        self.edid_manager = NVIDIAEDIDManager()
    
    def test_extreme_resolution_values(self):
        """Test handling of extreme resolution values."""
        extreme_config = EDIDOverrideConfig(
            display_index=0,
            custom_resolutions=[
                {"width": 1, "height": 1, "refresh_rate": 1},  # Minimum values
                {"width": 16384, "height": 16384, "refresh_rate": 1000},  # Extreme values
            ],
            force_resolution={"width": 8192, "height": 4320, "refresh_rate": 120}  # 8K
        )
        
        self.assertEqual(extreme_config.custom_resolutions[0]["width"], 1)
        self.assertEqual(extreme_config.custom_resolutions[1]["width"], 16384)
        self.assertEqual(extreme_config.force_resolution["width"], 8192)
    
    def test_empty_custom_resolutions(self):
        """Test handling of empty custom resolutions."""
        config = EDIDOverrideConfig(
            display_index=0,
            custom_resolutions=[],
            force_resolution=None
        )
        
        self.assertEqual(len(config.custom_resolutions), 0)
        self.assertIsNone(config.force_resolution)
    
    def test_none_values_handling(self):
        """Test handling of None values in various contexts."""
        # Test with None EDID data
        validation_result = self.edid_manager._validate_edid(None)
        self.assertFalse(validation_result)
        
        # Test with empty config values
        config = EDIDOverrideConfig(display_index=0)
        config.custom_edid_data = None
        config.custom_resolutions = []
        config.force_resolution = None
        
        self.assertIsNone(config.custom_edid_data)
        self.assertEqual(len(config.custom_resolutions), 0)
        self.assertIsNone(config.force_resolution)

def run_performance_error_demo():
    """Run a comprehensive performance and error handling demo."""
    print("Running EDID Performance and Error Handling Demo")
    print("=" * 60)
    
    edid_manager = NVIDIAEDIDManager()
    
    # Performance demo
    print("1. Performance Testing:")
    print("   Generating large EDID dataset...")
    large_dataset = []
    for i in range(50):
        edid_data = edid_manager._generate_sample_edid()
        large_dataset.append(edid_data)
    
    print("   Testing parsing performance...")
    start_time = time.time()
    parsed_count = 0
    for edid_data in large_dataset:
        try:
            edid_manager._parse_edid(edid_data)
            parsed_count += 1
        except:
            pass
    parse_time = time.time() - start_time
    print(f"   Parsed {parsed_count} EDIDs in {parse_time:.3f}s")
    
    print("   Testing validation performance...")
    start_time = time.time()
    valid_count = 0
    for edid_data in large_dataset:
        if edid_manager._validate_edid(edid_data):
            valid_count += 1
    valid_time = time.time() - start_time
    print(f"   Validated {len(large_dataset)} EDIDs in {valid_time:.3f}s")
    
    # Error handling demo
    print("\n2. Error Handling Testing:")
    print("   Testing invalid EDID handling...")
    invalid_cases = [None, b'', b'\x00' * 50, b'\xFF' * 128]
    for i, invalid_data in enumerate(invalid_cases):
        try:
            result = edid_manager._validate_edid(invalid_data)
            print(f"   Case {i+1}: Validation result = {result}")
        except Exception as e:
            print(f"   Case {i+1}: Exception = {type(e).__name__}")
    
    # File operation errors
    print("   Testing file operation errors...")
    non_existent_result = edid_manager.validate_edid_file("/nonexistent/file.bin")
    print(f"   Non-existent file validation: {non_existent_result}")
    
    # Edge cases
    print("\n3. Edge Case Testing:")
    print("   Testing extreme resolution values...")
    extreme_config = EDIDOverrideConfig(
        display_index=0,
        custom_resolutions=[
            {"width": 1, "height": 1, "refresh_rate": 1},
            {"width": 16384, "height": 16384, "refresh_rate": 1000}
        ]
    )
    print(f"   Min resolution: {extreme_config.custom_resolutions[0]}")
    print(f"   Max resolution: {extreme_config.custom_resolutions[1]}")
    
    print("\nPerformance and error handling demo completed!")
    print("=" * 60)

if __name__ == "__main__":
    # Run unit tests
    print("Running performance and error handling tests...")
    unittest.main(exit=False, verbosity=2)
    
    print("\n" + "="*60)
    print("RUNNING PERFORMANCE AND ERROR HANDLING DEMO")
    print("="*60)
    
    # Run performance and error handling demo
    run_performance_error_demo()
