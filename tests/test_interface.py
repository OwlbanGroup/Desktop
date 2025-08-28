import unittest
from unittest.mock import patch, MagicMock
from interface import run_interface
from organizational_leadership import leadership
from revenue_tracking import RevenueTracker


class TestInterface(unittest.TestCase):
    @patch('interface.input')
    @patch('builtins.print')
    def test_run_interface(self, mock_print, mock_input):
        # Mock user inputs
        mock_input.side_effect = [
            "Test Leader",  # Leader name
            "DEMOCRATIC",   # Leadership style
            "Member1:Developer",  # First team member
            "",             # Finish adding members
            "Test decision" # Decision
        ]
        
        # Mock revenue tracker to avoid database operations
        with patch('interface.RevenueTracker') as mock_tracker_class:
            mock_tracker_instance = MagicMock()
            mock_tracker_class.return_value = mock_tracker_instance
            mock_tracker_instance.generate_report.return_value = "Test Revenue Report"
            
            # Run the interface function
            run_interface()
            
            # Check that print was called with expected outputs
            mock_print.assert_any_call("Welcome to the Organizational Leadership CLI Interface")
            mock_print.assert_any_call("Team led by Test Leader with members: Member1")
            mock_print.assert_any_call("Test Leader encourages team participation in decision making.")
            mock_print.assert_any_call("Test Leader consults the team before deciding: Test decision")
            mock_print.assert_any_call("\nRevenue Report:")
            mock_print.assert_any_call("Test Revenue Report")

    @patch('interface.input')
    @patch('builtins.print')
    def test_run_interface_invalid_style(self, mock_print, mock_input):
        # Mock user inputs with invalid leadership style
        mock_input.side_effect = [
            "Test Leader",  # Leader name
            "INVALID",      # Invalid leadership style
        ]
        
        with self.assertRaises(SystemExit):
            run_interface()
            
        # Check that error message was printed
        mock_print.assert_any_call("Invalid leadership style: INVALID")

    @patch('interface.input')
    @patch('builtins.print')
    def test_run_interface_empty_decision(self, mock_print, mock_input):
        # Mock user inputs with empty decision
        mock_input.side_effect = [
            "Test Leader",  # Leader name
            "DEMOCRATIC",   # Leadership style
            "",             # Finish adding members (no members)
            ""              # Empty decision
        ]
        
        # Mock revenue tracker to avoid database operations
        with patch('interface.RevenueTracker') as mock_tracker_class:
            mock_tracker_instance = MagicMock()
            mock_tracker_class.return_value = mock_tracker_instance
            mock_tracker_instance.generate_report.return_value = "Test Revenue Report"
            
            # Run the interface function
            run_interface()
            
            # Check that print was called with expected outputs
            mock_print.assert_any_call("Welcome to the Organizational Leadership CLI Interface")
            mock_print.assert_any_call("No decision entered.")
            mock_print.assert_any_call("\nRevenue Report:")
            mock_print.assert_any_call("Test Revenue Report")


if __name__ == "__main__":
    unittest.main()
