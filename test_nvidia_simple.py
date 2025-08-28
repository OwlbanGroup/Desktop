#!/usr/bin/env python3

print("Testing NVIDIA integration...")

try:
    from nvidia_integration import NvidiaIntegration
    print("Import successful")
    
    # Create an instance
    nvidia = NvidiaIntegration()
    print("Instance created successfully")
    print(f"NVIDIA available: {nvidia.is_available}")
    
    # Test a few methods
    result = nvidia.setup_dali_pipeline()
    print(f"DALI pipeline result: {result}")
    
    result = nvidia.build_tensorrt_engine()
    print(f"TensorRT engine result: {result}")
    
    result = nvidia.connect_nim_services()
    print(f"NIM services result: {result}")
    
    # Test financial services methods
    fraud_data = [
        {"transaction_id": 1, "amount": 100.0, "currency": "USD"},
        {"transaction_id": 2, "amount": 250.0, "currency": "USD"}
    ]
    fraud_result = nvidia.perform_fraud_detection(fraud_data)
    print(f"Fraud detection result: {fraud_result}")
    
    risk_data = [
        {"portfolio_value": 100000, "market_volatility": 0.05},
        {"portfolio_value": 250000, "market_volatility": 0.03}
    ]
    risk_result = nvidia.perform_risk_management(risk_data)
    print(f"Risk management result: {risk_result}")
    
    analytics_data = [
        {"revenue": 1000000, "expenses": 800000, "quarter": "Q1"},
        {"revenue": 1200000, "expenses": 850000, "quarter": "Q2"}
    ]
    analytics_result = nvidia.generate_data_analytics(analytics_data)
    print(f"Data analytics result: {analytics_result}")
    
    # Test Colosseum model methods
    colosseum_result = nvidia.connect_to_colosseum_model()
    print(f"Colosseum model connection result: {colosseum_result}")
    
    prompt_result = nvidia.send_prompt_to_colosseum("What is the future of AI in finance?")
    print(f"Colosseum prompt result: {prompt_result}")
    
    # Test DeepSeek model methods
    deepseek_result = nvidia.connect_to_deepseek_model()
    print(f"DeepSeek model connection result: {deepseek_result}")
    
    prompt_result = nvidia.send_prompt_to_deepseek("What are the advantages of the DeepSeek v3.1 model?")
    print(f"DeepSeek prompt result: {prompt_result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
