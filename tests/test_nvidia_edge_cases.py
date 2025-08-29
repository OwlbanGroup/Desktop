import unittest
from nvidia_control_panel import NVIDIAControlPanel, CustomResolution

class TestNvidiaEdgeCases(unittest.TestCase):
    def setUp(self):
        self.ncp = NVIDIAControlPanel()

    def test_invalid_resolution_too_small(self):
        with self.assertRaises(ValueError):
            CustomResolution(width=100, height=100, refresh_rate=10, name="Invalid_Small")

    def test_invalid_resolution_too_large(self):
        with self.assertRaises(ValueError):
            CustomResolution(width=10000, height=10000, refresh_rate=300, name="Invalid_Large")

    def test_add_custom_resolution(self):
        custom_res = CustomResolution(width=2560, height=1440, refresh_rate=75, name="Custom_1440p_75Hz")
        result = self.ncp.add_custom_resolution(custom_res)
        self.assertIn("added successfully", result.lower())

    def test_apply_custom_resolution(self):
        custom_res = CustomResolution(width=1920, height=1080, refresh_rate=120, name="Custom_1080p_120Hz")
        self.ncp.add_custom_resolution(custom_res)
        result = self.ncp.apply_custom_resolution(custom_res)
        self.assertIn("applied successfully", result.lower())

    def test_remove_custom_resolution(self):
        custom_res = CustomResolution(width=1920, height=1080, refresh_rate=120, name="Custom_1080p_120Hz")
        self.ncp.add_custom_resolution(custom_res)
        result = self.ncp.remove_custom_resolution(custom_res.name)
        self.assertIn("removed successfully", result.lower())

if __name__ == "__main__":
    unittest.main()
