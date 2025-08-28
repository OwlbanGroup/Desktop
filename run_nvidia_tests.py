#!/usr/bin/env python3
"""
Script to run NVIDIA integration tests and capture output to a file
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test(test_file):
    """Run a specific test file and capture output"""
    print(f"Running {test_file}...")
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=60)
        return {
            'file': test_file,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'file': test_file,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Test timed out after 60 seconds',
            'success': False
        }
    except Exception as e:
        return {
            'file': test_file,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }

def main():
    """Main function to run all NVIDIA tests"""
    test_files = [
        'test_nvidia_simple.py',
        'test_nvidia_comprehensive.py',
        'test_nvidia_edge_cases.py',
        'test_nvidia_performance.py',
        'test_nvidia_integration_scenarios.py',
        'test_deepseek_comprehensive.py',
        'test_llama_integration.py'
    ]
    
    results = []
    
    print("Starting NVIDIA integration test suite...")
    print("=" * 50)
    
    for test_file in test_files:
        if os.path.exists(test_file):
            result = run_test(test_file)
            results.append(result)
            
            if result['success']:
                print(f"✓ {test_file}: PASSED")
            else:
                print(f"✗ {test_file}: FAILED (return code: {result['returncode']})")
        else:
            print(f"⚠ {test_file}: NOT FOUND")
    
    # Write detailed results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"nvidia_test_results_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("NVIDIA Integration Test Results\n")
        f.write("=" * 40 + "\n")
        f.write(f"Test Run: {datetime.now().isoformat()}\n\n")
        
        passed = sum(1 for r in results if r.get('success', False))
        total = len(results)
        
        f.write(f"Summary: {passed}/{total} tests passed\n\n")
        
        for result in results:
            f.write(f"\n{'='*40}\n")
            f.write(f"Test File: {result['file']}\n")
            f.write(f"Status: {'PASSED' if result['success'] else 'FAILED'}\n")
            f.write(f"Return Code: {result['returncode']}\n")
            
            if result['stdout']:
                f.write(f"\nSTDOUT:\n{result['stdout']}\n")
            
            if result['stderr']:
                f.write(f"\nSTDERR:\n{result['stderr']}\n")
    
    print(f"\nTest results saved to: {output_file}")
    print(f"Summary: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
