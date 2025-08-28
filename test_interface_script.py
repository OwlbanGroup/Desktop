import sys
from unittest.mock import patch
from interface import run_interface

# Mock input values
input_values = [
    "Test Leader",    # Leader name
    "DEMOCRATIC",     # Leadership style
    "Member1:Developer",  # Team member
    "",               # Finish adding members
    "Test decision"   # Decision
]

# Run the interface with mocked inputs
with patch('builtins.input', side_effect=input_values):
    run_interface()
