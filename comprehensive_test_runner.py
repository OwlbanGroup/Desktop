#!/usr/bin/env python3
"""
Comprehensive Test Runner for OWLban Group Integrated Application

This script runs all test suites including:
- Unit tests
- Integration tests
- Performance tests
- Security tests
- End-to-end tests

Usage:
    python comprehensive_test_runner.py run
    python comprehensive_test_runner.py report
    python comprehensive_test_runner.py coverage
"""

import subprocess
import sys
import logging
import json
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def run_command(command, check=True):
    logging.info(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        logging.info(f"Output: {result.stdout.strip()}")
    if result.stderr:
        logging.error(f"Error: {result.stderr.strip()}")
    if check and result.returncode != 0:
        logging.error(f"Command failed with exit code {result.returncode}")
        return False
    return True

def run_unit_tests():
    logging.info("Running unit tests...")
    return run_command("python -m pytest tests/ -v --tb=short")

def run_integration_tests():
    logging.info("Running integration tests...")
    return run_command("python test_integration.py")

def run_performance_tests():
    logging.info("Running performance tests...")
    return run_command("python test_performance.py")

def run_security_tests():
    logging.info("Running security tests...")
    return run_command("python -m pytest tests/test_security.py -v")

def run_e2e_tests():
    logging.info("Running end-to-end tests...")
    return run_command("python e2e_test_suite.py")

def run_nvidia_tests():
    logging.info("Running NVIDIA integration tests...")
    return run_command("python test_nvidia_integration_fixed.py")

def run_financial_tests():
    logging.info("Running financial system tests...")
    return run_command("python test_financial_system.py")

def generate_coverage_report():
    logging.info("Generating coverage report...")
    return run_command("python -m pytest --cov=. --cov-report=html --cov-report=term")

def generate_test_report():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"

    test_results = {
        "timestamp": timestamp,
        "test_suites": {
            "unit_tests": run_unit_tests(),
            "integration_tests": run_integration_tests(),
            "performance_tests": run_performance_tests(),
            "security_tests": run_security_tests(),
            "e2e_tests": run_e2e_tests(),
            "nvidia_tests": run_nvidia_tests(),
            "financial_tests": run_financial_tests()
        }
    }

    with open(report_file, 'w') as f:
        json.dump(test_results, f, indent=2)

    logging.info(f"Test report saved to {report_file}")
    return test_results

def main():
    if len(sys.argv) < 2:
        logging.error("No command provided. Use 'run', 'report', or 'coverage'.")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "run":
        logging.info("Starting comprehensive test suite...")
        results = generate_test_report()
        passed = sum(1 for result in results["test_suites"].values() if result)
        total = len(results["test_suites"])
        logging.info(f"Test Results: {passed}/{total} test suites passed")
    elif command == "report":
        results = generate_test_report()
        logging.info("Test report generated successfully.")
    elif command == "coverage":
        generate_coverage_report()
    else:
        logging.error(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
