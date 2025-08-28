#!/usr/bin/env python3
"""
Debug test script to verify the Llama model integration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_integration import NvidiaIntegration

def debug_test():
    """Debug test function"""
    # Open a debug file to write output
    with open('debug_output.txt', 'w') as f:
        f.write("Starting debug test...\n")
        
        # Initialize the NVIDIA integration
        nvidia = NvidiaIntegration()
        f.write("NVIDIA integration initialized\n")
        
        # Test connection to Llama model
        f.write("Connecting to Llama model...\n")
        connection_result = nvidia.connect_to_llama_model()
        f.write(f"Connection result: {connection_result}\n")
        
        # Test sending a prompt to Llama model
        f.write("Sending prompt to Llama model...\n")
        test_prompt = "Explain the concept of artificial intelligence in simple terms"
        response = nvidia.send_prompt_to_llama(test_prompt)
        f.write(f"Prompt: {test_prompt}\n")
        f.write(f"Response: {response}\n")
        
        # Test model status
        f.write("Checking model status...\n")
        status = nvidia.get_model_status()
        f.write("Model Status:\n")
        for key, value in status.items():
            f.write(f"  {key}: {value}\n")
        
        f.write("Debug test completed successfully!\n")

if __name__ == "__main__":
    debug_test()
