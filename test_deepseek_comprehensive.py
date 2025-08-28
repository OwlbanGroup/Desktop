#!/usr/bin/env python3
"""
Comprehensive test for the DeepSeek v3.1 model integration
"""

import unittest
from nvidia_integration import NvidiaIntegration

class TestDeepSeekIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.nvidia = NvidiaIntegration()
    
    def test_deepseek_model_connection(self):
        """Test connecting to the DeepSeek model"""
        result = self.nvidia.connect_to_deepseek_model()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        # In simulated mode, we expect a specific string
        if not self.nvidia.is_available:
            self.assertEqual(result, "Simulated DeepSeek v3.1 Model")
    
    def test_deepseek_prompt_response(self):
        """Test sending a prompt to the DeepSeek model"""
        prompt = "What are the advantages of the DeepSeek v3.1 model for financial analysis?"
        result = self.nvidia.send_prompt_to_deepseek(prompt)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        # In simulated mode, we expect the prompt to be included in the response
        if not self.nvidia.is_available:
            self.assertIn(prompt, result)
            self.assertIn("Simulated response to prompt:", result)
    
    def test_multiple_prompts(self):
        """Test sending multiple prompts to the DeepSeek model"""
        prompts = [
            "How can DeepSeek v3.1 improve risk assessment?",
            "What are the cost benefits of using DeepSeek v3.1 through NVIDIA NIM?"
        ]
        
        for prompt in prompts:
            result = self.nvidia.send_prompt_to_deepseek(prompt)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
            # In simulated mode, we expect the prompt to be included in the response
            if not self.nvidia.is_available:
                self.assertIn(prompt, result)
                self.assertIn("Simulated response to prompt:", result)

if __name__ == "__main__":
    print("Running comprehensive tests for DeepSeek v3.1 integration...")
    unittest.main(verbosity=2)
