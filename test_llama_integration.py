#!/usr/bin/env python3
"""
Test script for Llama 3.3 Nemotron Super 49B model integration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nvidia_integration import NvidiaIntegration

def test_llama_integration():
    """Test the Llama model integration functionality"""
    print("Starting Llama 3.3 Nemotron Super 49B model integration test...")
    
    # Initialize the NVIDIA integration
    nvidia = NvidiaIntegration()
    
    # Test connection to Llama model
    print("\n1. Connecting to Llama model...")
    connection_result = nvidia.connect_to_llama_model()
    print(f"Connection result: {connection_result}")
    
    # Test sending a prompt to Llama model
    print("\n2. Sending prompt to Llama model...")
    test_prompt = "Explain the concept of artificial intelligence in simple terms"
    response = nvidia.send_prompt_to_llama(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")
    
    # Test model status
    print("\n3. Checking model status...")
    status = nvidia.get_model_status()
    print("Model Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test advanced status
    print("\n4. Checking advanced status...")
    advanced_status = nvidia.get_advanced_status()
    print("Advanced Status:")
    for key, value in advanced_status.items():
        print(f"  {key}: {value}")
    
    print("\nLlama model integration test completed successfully!")

if __name__ == "__main__":
    test_llama_integration()
