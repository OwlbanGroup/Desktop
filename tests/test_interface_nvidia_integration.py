import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration import NvidiaIntegration


class TestInterfaceNvidiaIntegration(unittest.TestCase):
    """Test NVIDIA integration in the interface.py module"""

    def setUp(self):
        self.leader = leadership.Leader("Test Leader", leadership.LeadershipStyle.DEMOCRATIC)
        self.revenue_tracker = RevenueTracker()
        self.nvidia_integration = NvidiaIntegration()

    def test_interface_imports_nvidia_integration(self):
        """Test that interface.py imports NvidiaIntegration"""
        try:
            from interface import NvidiaIntegration
            self.assertTrue(True, "NvidiaIntegration is imported in interface.py")
        except ImportError:
            self.fail("NvidiaIntegration is not imported in interface.py")

    def test_nvidia_integration_instance_creation_in_interface(self):
        """Test that NvidiaIntegration instance is created in interface"""
        with patch('interface.NvidiaIntegration') as mock_nvidia, \
             patch('interface.leadership'), \
             patch('interface.RevenueTracker'), \
             patch('builtins.input', side_effect=['Test Leader', 'DEMOCRATIC', '']), \
             patch('builtins.print'):
            
            mock_instance = MagicMock()
            mock_nvidia.return_value = mock_instance
            
            # Import and run the interface
            from interface import run_interface
            run_interface()
            
            # Verify NvidiaIntegration was instantiated
            mock_nvidia.assert_called_once()

    def test_gpu_status_prompt_and_display(self):
        """Test that GPU status prompt is shown and status is displayed when requested"""
        with patch('interface.NvidiaIntegration') as mock_nvidia, \
             patch('interface.leadership'), \
             patch('interface.RevenueTracker'), \
             patch('builtins.input', side_effect=['Test Leader', 'DEMOCRATIC', '', 'Test decision', 'y']), \
             patch('builtins.print') as mock_print:
            
            mock_instance = MagicMock()
            mock_instance.get_gpu_settings.return_value = {
                "power_mode": "Adaptive",
                "texture_filtering": "Performance",
                "vertical_sync": "On",
                "temperature": "65°C",
                "utilization": "45%"
            }
            mock_nvidia.return_value = mock_instance
            
            # Import and run the interface
            from interface import run_interface
            run_interface()
            
            # Verify GPU settings were retrieved
            mock_instance.get_gpu_settings.assert_called_once()
            
            # Check that GPU status was printed (look for NVIDIA GPU Status in print calls)
            nvidia_printed = any("NVIDIA GPU Status" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(nvidia_printed, "GPU status should be printed when user responds 'y'")

    def test_gpu_status_not_displayed_when_declined(self):
        """Test that GPU status is NOT displayed when user responds 'n'"""
        with patch('interface.NvidiaIntegration') as mock_nvidia, \
             patch('interface.leadership'), \
             patch('interface.RevenueTracker'), \
             patch('builtins.input', side_effect=['Test Leader', 'DEMOCRATIC', '', 'Test decision', 'n']), \
             patch('builtins.print') as mock_print:
            
            mock_instance = MagicMock()
            mock_nvidia.return_value = mock_instance
            
            # Import and run the interface
            from interface import run_interface
            run_interface()
            
            # Verify GPU settings were NOT retrieved
            mock_instance.get_gpu_settings.assert_not_called()
            
            # Check that GPU status was NOT printed
            nvidia_printed = any("NVIDIA GPU Status" in str(call) for call in mock_print.call_args_list)
            self.assertFalse(nvidia_printed, "GPU status should NOT be printed when user responds 'n'")

    def test_gpu_status_display_format(self):
        """Test that GPU status is displayed in proper format"""
        with patch('interface.NvidiaIntegration') as mock_nvidia, \
             patch('interface.leadership'), \
             patch('interface.RevenueTracker'), \
             patch('builtins.input', side_effect=['Test Leader', 'DEMOCRATIC', '', 'Test decision', 'y']), \
             patch('builtins.print') as mock_print:
            
            mock_instance = MagicMock()
            test_settings = {
                "power_mode": "Adaptive",
                "texture_filtering": "Performance",
                "vertical_sync": "On",
                "temperature": "65°C",
                "utilization": "45%"
            }
            mock_instance.get_gpu_settings.return_value = test_settings
            mock_nvidia.return_value = mock_instance
            
            # Import and run the interface
            from interface import run_interface
            run_interface()
            
            # Check that each setting key-value pair is printed
            settings_printed = []
            for call in mock_print.call_args_list:
                call_str = str(call)
                for key, value in test_settings.items():
                    if key in call_str and str(value) in call_str:
                        settings_printed.append(key)
            
            # Verify at least some settings were printed
            self.assertGreater(len(settings_printed), 0, 
                             "At least some GPU settings should be printed in the format 'key: value'")

    def test_interface_handles_nvidia_errors_gracefully(self):
        """Test that interface handles NVIDIA integration errors gracefully"""
        with patch('interface.NvidiaIntegration') as mock_nvidia, \
             patch('interface.leadership'), \
             patch('interface.RevenueTracker'), \
             patch('builtins.input', side_effect=['Test Leader', 'DEMOCRATIC', '', 'Test decision', 'y']), \
             patch('builtins.print') as mock_print:
            
            mock_instance = MagicMock()
            mock_instance.get_gpu_settings.side_effect = Exception("NVIDIA API error")
            mock_nvidia.return_value = mock_instance
            
            # Import and run the interface - should not crash
            from interface import run_interface
            try:
                run_interface()
                # If we get here, the interface handled the error gracefully
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"Interface should handle NVIDIA errors gracefully, but got: {e}")


if __name__ == '__main__':
    unittest.main()
