#!/usr/bin/env python3
"""
E2E Test Runner Script
Handles dependencies, server startup, and test execution
"""

import subprocess
import sys
import os
import importlib.util
import time

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['requests', 'psutil']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'psutil':
                import psutil
            else:
                importlib.import_module(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")

    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

    return True

def check_backend_ready():
    """Check if backend server files exist"""
    backend_files = [
        'backend/app_server.py',
        'backend/security_config.py'
    ]

    missing_files = []
    for file_path in backend_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing backend files: {', '.join(missing_files)}")
        return False

    print("✅ Backend files are present")
    return True

def run_tests():
    """Execute the E2E test suite"""
    try:
        print("\n🚀 Starting E2E Test Suite...")
        result = subprocess.run([sys.executable, 'e2e_test_suite.py'],
                              capture_output=True, text=True, timeout=300)

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ E2E Test Suite completed successfully!")
            return True
        else:
            print(f"❌ E2E Test Suite failed with return code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ E2E Test Suite timed out after 5 minutes")
        return False
    except FileNotFoundError:
        print("❌ e2e_test_suite.py not found")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main execution function"""
    print("🧪 Owlban Group E2E Test Runner")
    print("=" * 50)

    # Check dependencies
    print("\n📋 Checking dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)

    # Check backend files
    print("\n📁 Checking backend files...")
    if not check_backend_ready():
        print("❌ Backend check failed")
        sys.exit(1)

    # Run tests
    success = run_tests()

    # Display results
    if success:
        print("\n🎉 All checks passed! E2E tests completed successfully.")
        print("📊 Check e2e_test_report.txt for detailed results.")
        sys.exit(0)
    else:
        print("\n💥 E2E tests failed. Check output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
