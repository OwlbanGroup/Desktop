#!/usr/bin/env python3
"""
Demonstration script for the DeepSeek v3.1 model integration
via NVIDIA NIM services.
"""

print("DeepSeek v3.1 Model Integration Demo")
print("=" * 40)

try:
    from nvidia_integration import NvidiaIntegration
    print("✓ Successfully imported NvidiaIntegration")
    
    # Create an instance
    nvidia = NvidiaIntegration()
    print(f"✓ Instance created successfully")
    print(f"✓ NVIDIA available: {nvidia.is_available}")
    
    # Connect to the DeepSeek model
    print("\nConnecting to DeepSeek v3.1 model...")
    connection_result = nvidia.connect_to_deepseek_model()
    print(f"✓ Connection result: {connection_result}")
    
    # Send a prompt to the DeepSeek model
    print("\nSending prompt to DeepSeek v3.1 model...")
    prompt = "What are the key advantages of the DeepSeek v3.1 model for financial services applications?"
    response = nvidia.send_prompt_to_deepseek(prompt)
    print(f"✓ Prompt: {prompt}")
    print(f"✓ Response: {response}")
    
    # Send another prompt
    print("\nSending another prompt to DeepSeek v3.1 model...")
    prompt = "How does DeepSeek v3.1 compare to other large language models in terms of efficiency?"
    response = nvidia.send_prompt_to_deepseek(prompt)
    print(f"✓ Prompt: {prompt}")
    print(f"✓ Response: {response}")
    
    print("\n" + "=" * 40)
    print("Demo completed successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    print("Run with: python demo_deepseek.py")
