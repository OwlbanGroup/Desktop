#!/usr/bin/env python3
"""
Demonstration script for NVIDIA NeMo-Agent-Toolkit Integration

This script showcases the advanced capabilities of the NVIDIA NeMo framework
integration, including multi-agent systems, tool calling, and real AI capabilities.
"""

import json
from nvidia_integration import NvidiaIntegration

def main():
    print("=" * 60)
    print("NVIDIA NeMo-Agent-Toolkit Integration Demo")
    print("=" * 60)
    
    # Initialize NVIDIA integration
    print("\n1. Initializing NVIDIA Integration...")
    nvidia = NvidiaIntegration()
    
    # Check system status
    print("\n2. Checking System Status...")
    status = nvidia.get_advanced_status()
    print(f"   NVIDIA Framework Available: {status['nvidia_available']}")
    print(f"   NeMo Framework Available: {status['nemo_framework_available']}")
    print(f"   NIM Services Available: {status['nim_services_available']}")
    print(f"   RAPIDS Available: {status['rapids_available']}")
    
    # Load NeMo models
    print("\n3. Loading NeMo Models...")
    models_to_load = ["gpt-3.5b", "bert-base", "financial-analyzer"]
    for model_name in models_to_load:
        result = nvidia.load_nemo_model(model_name)
        print(f"   {model_name}: {result}")
    
    # Create multi-agent system
    print("\n4. Creating Multi-Agent System...")
    agent_config = {
        "agents": [
            {
                "name": "financial_analyst",
                "role": "Analyze financial data and trends",
                "capabilities": ["data_analysis", "trend_prediction"]
            },
            {
                "name": "risk_manager", 
                "role": "Assess and mitigate risks",
                "capabilities": ["risk_assessment", "compliance_checking"]
            },
            {
                "name": "decision_maker",
                "role": "Make strategic decisions",
                "capabilities": ["strategy_planning", "resource_allocation"]
            }
        ],
        "orchestration": "hierarchical",
        "communication": "message_bus"
    }
    
    agent_result = nvidia.create_agent_system(agent_config)
    print(f"   Agent System: {agent_result}")
    
    # Demonstrate tool calling
    print("\n5. Demonstrating Tool Calling...")
    tools_to_test = [
        ("financial_analysis", {"period": "Q3-2024", "metrics": ["revenue", "expenses", "profit"]}),
        ("risk_assessment", {"portfolio_value": 1000000, "risk_tolerance": "moderate"}),
        ("market_prediction", {"sector": "technology", "timeframe": "6 months"})
    ]
    
    for tool_name, params in tools_to_test:
        result = nvidia.tool_calling(tool_name, params)
        print(f"   {tool_name}: {result}")
    
    # Stream responses
    print("\n6. Demonstrating Response Streaming...")
    prompts = [
        "Analyze the current market trends for technology stocks",
        "What are the key risk factors for our investment portfolio?",
        "Generate a strategic plan for Q4 revenue growth"
    ]
    
    for prompt in prompts:
        response = nvidia.stream_response(prompt)
        print(f"   Prompt: {prompt}")
        print(f"   Response: {response}")
        print()
    
    # Financial services AI capabilities
    print("\n7. Financial Services AI Demonstrations...")
    
    # Fraud detection
    print("   Fraud Detection:")
    transactions = [
        {"amount": 150, "merchant": "Coffee Shop", "location": "Local"},
        {"amount": 2500, "merchant": "Electronics Store", "location": "Online"},
        {"amount": 12000, "merchant": "Luxury Goods", "location": "International"}
    ]
    fraud_results = nvidia.perform_fraud_detection(transactions)
    print(f"   Results: {json.dumps(fraud_results, indent=2)}")
    
    # Risk management
    print("\n   Risk Management:")
    financial_data = [
        {"asset": "Stocks", "value": 500000, "volatility": "high"},
        {"asset": "Bonds", "value": 300000, "volatility": "low"},
        {"asset": "Real Estate", "value": 200000, "volatility": "medium"}
    ]
    risk_results = nvidia.perform_risk_management(financial_data)
    print(f"   Results: {json.dumps(risk_results, indent=2)}")
    
    # Data analytics
    print("\n   Data Analytics:")
    business_data = [
        {"quarter": "Q1", "revenue": 1200000, "expenses": 800000},
        {"quarter": "Q2", "revenue": 1350000, "expenses": 850000},
        {"quarter": "Q3", "revenue": 1500000, "expenses": 900000}
    ]
    analytics_results = nvidia.generate_data_analytics(business_data)
    print(f"   Results: {json.dumps(analytics_results, indent=2)}")
    
    # Batch processing
    print("\n8. Batch Processing Demonstration...")
    batch_prompts = [
        "Generate quarterly financial report",
        "Analyze customer satisfaction trends",
        "Predict next quarter's revenue",
        "Identify operational inefficiencies",
        "Suggest cost optimization strategies"
    ]
    
    batch_results = nvidia.batch_process_prompts(batch_prompts, model_type="colosseum")
    print(f"   Processed {len(batch_results)} prompts successfully")
    for i, result in enumerate(batch_results[:2]):  # Show first 2 results
        print(f"   Result {i+1}: {result[:100]}...")
    
    # Final status check
    print("\n9. Final System Status:")
    final_status = nvidia.get_advanced_status()
    print(f"   Loaded Models: {final_status['nemo_models_loaded']}")
    print(f"   Total Operations: Demo completed successfully!")
    
    print("\n" + "=" * 60)
    print("NVIDIA NeMo-Agent-Toolkit Demo Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
