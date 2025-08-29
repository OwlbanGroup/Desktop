#!/usr/bin/env python3
"""
Test script for NVIDIA Control Panel PhysX configuration functionality.
This script tests the newly added PhysX configuration methods.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_control_panel import NVIDIAControlPanel, PhysXConfiguration, PhysXProcessor

class TestPhysXConfiguration(unittest.TestCase):
    def setUp(self):
        self.ncp = NVIDIAControlPanel()

    def test_get_physx_configuration(self):
        config = self.ncp.get_physx_configuration()
        self.assertIsInstance(config, PhysXConfiguration, "Returned object is not PhysXConfiguration")
        self.assertIsInstance(config.enabled, bool, "Enabled flag is not boolean")
        self.assertIn(config.selected_processor, PhysXProcessor, "Selected processor invalid")
        self.assertIsInstance(config.available_gpus, list, "Available GPUs is not a list")

    def test_set_physx_configuration_valid(self):
        config = PhysXConfiguration(enabled=True, selected_processor=PhysXProcessor.GPU)
        result = self.ncp.set_physx_configuration(config)
        self.assertIn("successfully", result.lower(), "Failed to set PhysX configuration")

        config = PhysXConfiguration(enabled=False, selected_processor=PhysXProcessor.CPU)
        result = self.ncp.set_physx_configuration(config)
        self.assertIn("successfully", result.lower(), "Failed to set PhysX configuration")

    def test_set_physx_configuration_invalid(self):
        with self.assertRaises(Exception):
            self.ncp.set_physx_configuration("invalid")

if __name__ == "__main__":
    unittest.main()
