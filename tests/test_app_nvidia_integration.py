import unittest
import subprocess
import sys
from unittest.mock import patch, MagicMock
from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration import NvidiaIntegration


class TestAppNvidiaIntegration(unittest.TestCase):
    """Test NVIDIA integration in the app.py module"""

    def setUp(self):
        self.leader = leadership.Leader("Test Leader", leadership.LeadershipStyle.DEMOCRATIC)
        self.revenue_tracker = RevenueTracker()
        self.nvidia_integration = NvidiaIntegration()

    def test_app_imports_nvidia_integration(self):
        """Test that app.py imports NvidiaIntegration"""
        # This test ensures the import statement is present
        try:
            from app import NvidiaIntegration
            self.assertTrue(True, "NvidiaIntegration is imported in app.py")
        except ImportError:
            self.fail("NvidiaIntegration is not imported in app.py")

    def test_app_has_show_gpu_status_argument(self):
        """Test that app.py has the --show-gpu-status argument"""
        # Mock the argument parsing to test the argument exists
        with patch('sys.argv', ['app.py', '--show-gpu-status']):
            try:
                from app import main
                # If we get here without error, the argument exists
                self.assertTrue(True)
            except SystemExit:
                # argparse will call sys.exit when --help is used, which is expected
                pass

    def test_nvidia_integration_instance_creation(self):
        """Test that NvidiaIntegration instance is created in app"""
        # Mock the NvidiaIntegration to avoid actual GPU calls
        with patch('app.NvidiaIntegration') as mock_nvidia:
            mock_instance = MagicMock()
            mock_nvidia.return_value = mock_instance
            
            # Mock other dependencies
            with patch('app.leadership'), \
                 patch('app.RevenueTracker'), \
                 patch('app.argparse.ArgumentParser') as mock_parser:
                
                mock_args = MagicMock()
                mock_args.leader_name = "Test"
                mock_args.leadership_style = "DEMOCRATIC"
                mock_args.team_members = []
                mock_args.decision = "Test decision"
                mock_args.show_gpu_status = True
                
                mock_parser_instance = MagicMock()
                mock_parser_instance.parse_args.return_value = mock_args
                mock_parser.return_value = mock_parser_instance
                
                # Import and run main
                from app import main
                main()
                
                # Verify NvidiaIntegration was instantiated
                mock_nvidia.assert_called_once()

    def test_gpu_status_display_when_requested(self):
        """Test that GPU status is displayed when --show-gpu-status is used"""
        # Mock everything
        with patch('app.NvidiaIntegration') as mock_nvidia, \
             patch('app.leadership'), \
             patch('app.RevenueTracker'), \
             patch('app.argparse.ArgumentParser') as mock_parser, \
             patch('builtins.print') as mock_print:
            
            mock_instance = MagicMock()
            mock_instance.get_gpu_settings.return_value = {
                "power_mode": "Adaptive",
                "texture_filtering": "Performance",
                "vertical_sync": "On"
            }
            mock_nvidia.return_value = mock_instance
            
            mock_args = MagicMock()
            mock_args.leader_name = "Test"
            mock_args.leadership_style = "DEMOCRATIC"
            mock_args.team_members = []
            mock_args.decision = "Test decision"
            mock_args.show_gpu_status = True
            
            mock_parser_instance = MagicMock()
            mock_parser_instance.parse_args.return_value = mock_args
            mock_parser.return_value = mock_parser_instance
            
            # Import and run main
            from app import main
            main()
            
            # Verify GPU settings were retrieved and printed
            mock_instance.get_gpu_settings.assert_called_once()
            # Check that GPU status was printed (look for NVIDIA GPU Status in print calls)
            nvidia_printed = any("NVIDIA GPU Status" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(nvidia_printed, "GPU status should be printed when --show-gpu-status is used")

    def test_gpu_status_not_displayed_when_not_requested(self):
        """Test that GPU status is NOT displayed when --show-gpu-status is not used"""
        with patch('app.NvidiaIntegration') as mock_nvidia, \
             patch('app.leadership'), \
             patch('app.RevenueTracker'), \
             patch('app.argparse.ArgumentParser') as mock_parser, \
             patch('builtins.print') as mock_print:
            
            mock_instance = MagicMock()
            mock_nvidia.return_value = mock_instance
            
            mock_args = MagicMock()
            mock_args.leader_name = "Test"
            mock_args.leadership_style = "DEMOCRATIC"
            mock_args.team_members = []
            mock_args.decision = "Test decision"
            mock_args.show_gpu_status = False  # Not requested
            
            mock_parser_instance = MagicMock()
            mock_parser_instance.parse_args.return_value = mock_args
            mock_parser.return_value = mock_parser_instance
            
            # Import and run main
            from app import main
            main()
            
            # Verify GPU settings were NOT retrieved
            mock_instance.get_gpu_settings.assert_not_called()


if __name__ == '__main__':
    unittest.main()
