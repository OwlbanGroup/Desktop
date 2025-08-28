#!/usr/bin/env python3
"""
Performance testing for NVIDIA integration
Tests response times and scalability under load
"""

import time
import statistics
from nvidia_integration import NvidiaIntegration

def performance_test():
    """Run comprehensive performance tests"""
    print("🧪 NVIDIA Integration Performance Test")
    print("=" * 50)
    
    nvidia = NvidiaIntegration()
    print(f"Running in {'SIMULATION' if not nvidia.is_available else 'REAL'} mode")
    print()
    
    # Test single prompt response time
    print("1. Single Prompt Response Time:")
    print("-" * 30)
    
    prompt = "Test prompt for performance measurement"
    times = []
    
    for i in range(5):  # Run 5 iterations for average
        start_time = time.time()
        result = nvidia.send_prompt_to_colosseum(prompt)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        times.append(response_time)
        print(f"  Iteration {i+1}: {response_time:.2f} ms")
    
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    print(f"  Average: {avg_time:.2f} ms (±{std_dev:.2f} ms)")
    print()
    
    # Test batch processing performance
    print("2. Batch Processing Performance:")
    print("-" * 30)
    
    prompts = [f"Prompt {i} for batch testing" for i in range(10)]
    batch_times = []
    
    for i in range(3):  # Run 3 iterations
        start_time = time.time()
        results = nvidia.batch_process_prompts(prompts, "colosseum")
        end_time = time.time()
        batch_time = (end_time - start_time) * 1000
        batch_times.append(batch_time)
        print(f"  Batch {i+1}: {batch_time:.2f} ms for {len(prompts)} prompts")
        print(f"    Avg per prompt: {batch_time/len(prompts):.2f} ms")
    
    avg_batch_time = statistics.mean(batch_times)
    print(f"  Average batch time: {avg_batch_time:.2f} ms")
    print()
    
    # Test financial services performance
    print("3. Financial Services Performance:")
    print("-" * 30)
    
    # Fraud detection performance
    transactions = [
        {"amount": i * 100, "transaction_id": f"txn_{i}", "merchant": "test"} 
        for i in range(20)
    ]
    
    fraud_times = []
    for i in range(3):
        start_time = time.time()
        result = nvidia.perform_fraud_detection(transactions)
        end_time = time.time()
        fraud_time = (end_time - start_time) * 1000
        fraud_times.append(fraud_time)
        print(f"  Fraud detection {i+1}: {fraud_time:.2f} ms for {len(transactions)} transactions")
    
    avg_fraud_time = statistics.mean(fraud_times)
    print(f"  Average fraud detection time: {avg_fraud_time:.2f} ms")
    print()
    
    # Test concurrent operations
    print("4. Concurrent Operations Test:")
    print("-" * 30)
    
    operations = []
    start_time = time.time()
    
    # Simulate concurrent operations
    operations.append(nvidia.connect_to_colosseum_model())
    operations.append(nvidia.connect_to_deepseek_model())
    operations.append(nvidia.setup_dali_pipeline())
    operations.append(nvidia.build_tensorrt_engine())
    
    end_time = time.time()
    concurrent_time = (end_time - start_time) * 1000
    print(f"  Concurrent initialization: {concurrent_time:.2f} ms")
    print(f"  Operations completed: {len(operations)}")
    print()
    
    # Memory usage estimation (simplified)
    print("5. Memory Usage Estimation:")
    print("-" * 30)
    
    # Get status to see what's loaded
    status = nvidia.get_model_status()
    loaded_models = sum([
        status['dali_pipeline'],
        status['tensorrt_engine'], 
        status['nim_services'],
        status['colosseum_model'],
        status['deepseek_model']
    ])
    
    print(f"  Models/Services loaded: {loaded_models}/5")
    print("  Memory usage: Estimated (simulation mode - actual would vary with real SDKs)")
    print()
    
    # Performance summary
    print("📊 Performance Summary:")
    print("=" * 30)
    print(f"Single prompt response: {avg_time:.2f} ms")
    print(f"Batch processing (10 prompts): {avg_batch_time:.2f} ms")
    print(f"Fraud detection (20 transactions): {avg_fraud_time:.2f} ms")
    print(f"Concurrent initialization: {concurrent_time:.2f} ms")
    print()
    
    if not nvidia.is_available:
        print("💡 Note: Running in simulation mode. Real NVIDIA SDKs would provide:")
        print("   - Faster response times with GPU acceleration")
        print("   - Higher throughput for batch processing")
        print("   - More accurate memory usage metrics")
        print("   - Better scalability for large datasets")

if __name__ == "__main__":
    performance_test()
