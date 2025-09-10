#!/usr/bin/env python3
"""
Improved runner for Chase integration tests with better error handling
"""

import subprocess
import time
import socket
import sys
import signal
import os

def wait_for_port(host, port, timeout=30, check_interval=0.5):
    """Wait for a port to become available with better error handling"""
    start_time = time.time()
    print(f"Waiting for server to start on {host}:{port}...")

    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"✅ Server is responding on {host}:{port}")
                return True
        except OSError as e:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"❌ Timeout: Server did not start within {timeout} seconds")
                print(f"   Error: {e}")
                return False

            # Show progress every 5 seconds
            if int(elapsed) % 5 == 0 and int(elapsed) > 0:
                print(f"   Still waiting... ({int(elapsed)}s elapsed)")

            time.sleep(check_interval)

def start_flask_app():
    """Start the Flask app and return the process"""
    print("🚀 Starting Flask app...")

    # Use the simple Flask test app instead of the complex one
    cmd = [sys.executable, "simple_flask_test_fixed.py"]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Use text mode for better encoding handling
            encoding='utf-8',
            errors='replace'  # Replace problematic characters
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        return None

def run_tests():
    """Run the improved Chase integration tests"""
    print("🧪 Running Chase integration tests...")

    cmd = [sys.executable, "chase_integration_test_improved.py"]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Wait for test completion with timeout
        try:
            stdout, stderr = process.communicate(timeout=60)  # 60 second timeout

            print("📄 Test Output:")
            print("-" * 40)
            if stdout:
                print(stdout)
            if stderr:
                print("⚠️  Test Errors:")
                print(stderr)

            return process.returncode == 0

        except subprocess.TimeoutExpired:
            print("❌ Test timed out after 60 seconds")
            process.kill()
            return False

    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def cleanup_process(process):
    """Clean up the Flask process"""
    if process:
        print("🧹 Cleaning up Flask process...")
        try:
            process.terminate()
            # Wait up to 5 seconds for graceful termination
            process.wait(timeout=5)
            print("✅ Flask process terminated gracefully")
        except subprocess.TimeoutExpired:
            print("⚠️  Flask process didn't terminate gracefully, forcing kill...")
            process.kill()
            process.wait()
            print("✅ Flask process killed")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")

def main():
    flask_process = None

    try:
        # Start Flask app
        flask_process = start_flask_app()
        if not flask_process:
            print("❌ Failed to start Flask app")
            sys.exit(1)

        # Wait for server to be ready
        if not wait_for_port("localhost", 5000, timeout=30):
            print("❌ Flask server failed to start properly")
            sys.exit(1)

        # Give server a moment to fully initialize
        time.sleep(2)

        # Run tests
        success = run_tests()

        if success:
            print("🎉 All tests passed successfully!")
            sys.exit(0)
        else:
            print("❌ Some tests failed")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        cleanup_process(flask_process)

if __name__ == "__main__":
    main()
