#!/usr/bin/env python3
"""
Comprehensive test for the enhanced NVIDIA integration
Demonstrates all the new functionality added to the NvidiaIntegration class
"""

import json
from nvidia_integration import NvidiaIntegration

def test_all_functionality():
    print("=== NVIDIA Integration Comprehensive Test ===")
    print()
    
    # Initialize the integration
    nvidia = NvidiaIntegration()
    print(f"NVIDIA SDKs available: {nvidia.is_available}")
    print()
    
    # Test model connections
    print("1. Testing Model Connections:")
    print("-" * 30)
    
    colosseum_result = nvidia.connect_to_colosseum_model()
    print(f"Colosseum connection: {colosseum_result}")
    
    deepseek_result = nvidia.connect_to_deepseek_model()
    print(f"DeepSeek connection: {deepseek_result}")
    
    nim_result = nvidia.connect_nim_services()
    print(f"NIM services: {nim_result}")
    print()
    
    # Test infrastructure setup
    print("2. Testing Infrastructure Setup:")
    print("-" * 30)
    
    dali_result = nvidia.setup_dali_pipeline()
    print(f"DALI pipeline: {dali_result}")
    
    tensorrt_result = nvidia.build_tensorrt_engine()
    print(f"TensorRT engine: {tensorrt_result}")
    print()
    
    # Test financial services
    print("3. Testing Financial Services:")
    print("-" * 30)
    
    # Fraud detection
    transactions = [
        {"transaction_id": 1, "amount": 150.0, "currency": "USD", "merchant": "Amazon"},
        {"transaction_id": 2, "amount": 2500.0, "currency": "USD", "merchant": "Best Buy"},
        {"transaction_id": 3, "amount": 7500.0, "currency": "USD", "merchant": "Apple Store"}
    ]
    fraud_result = nvidia.perform_fraud_detection(transactions)
    print("Fraud Detection Results:")
    print(json.dumps(fraud_result, indent=2))
    print()
    
    # Risk management
    risk_data = [
        {"portfolio_value": 100000, "market_volatility": 0.05, "sector": "Technology"},
        {"portfolio_value": 250000, "market_volatility": 0.08, "sector": "Healthcare"}
    ]
    risk_result = nvidia.perform_risk_management(risk_data)
    print("Risk Management Results:")
    print(json.dumps(risk_result, indent=2))
    print()
    
    # Data analytics
    analytics_data = [
        {"revenue": 1000000, "expenses": 800000, "quarter": "Q1", "year": 2024},
        {"revenue": 1200000, "expenses": 850000, "quarter": "Q2", "year": 2024},
        {"revenue": 1100000, "expenses": 820000, "quarter": "Q3", "year": 2024}
    ]
    analytics_result = nvidia.generate_data_analytics(analytics_data)
    print("Data Analytics Results:")
    print(json.dumps(analytics_result, indent=2))
    print()
    
    # Test model interactions
    print("4. Testing Model Interactions:")
    print("-" * 30)
    
    # Single prompts
    colosseum_prompt = "What are the key trends in AI-powered financial services for 2024?"
    colosseum_response = nvidia.send_prompt_to_colosseum(colosseum_prompt)
    print(f"Colosseum response: {colosseum_response[:100]}...")
    print()
    
    deepseek_prompt = "How can DeepSeek v3.1 help with financial data analysis and prediction?"
    deepseek_response = nvidia.send_prompt_to_deepseek(deepseek_prompt)
    print(f"DeepSeek response: {deepseek_response[:100]}...")
    print()
    
    # Batch processing
    prompts = [
        "Analyze market trends for Q4 2024",
        "Predict revenue growth for technology sector",
        "Identify potential investment opportunities"
    ]
    batch_results = nvidia.batch_process_prompts(prompts, model_type="colosseum")
    print("Batch Processing Results:")
    for i, result in enumerate(batch_results):
        print(f"  Prompt {i+1}: {result[:80]}...")
    print()
    
    # Test blueprint integration
    print("5. Testing Blueprint Integration:")
    print("-" * 30)
    
    blueprint_params = {
        "model_type": "financial_analysis",
        "data_source": "internal_database",
        "output_format": "json",
        "confidence_threshold": 0.85
    }
    blueprint_result = nvidia.integrate_blueprint("Financial Analytics Blueprint", blueprint_params)
    print(f"Blueprint integration: {blueprint_result}")
    print()
    
    # Test status monitoring
    print("6. Testing Status Monitoring:")
    print("-" * 30)
    
    status = nvidia.get_model_status()
    print("System Status:")
    print(json.dumps(status, indent=2))
    print()
    
    print("=== Test Completed Successfully ===")

if __name__ == "__main__":
    test_all_functionality()
