import subprocess
import time
import socket
import sys

def wait_for_port(host, port, timeout=30):
    """Wait for a port to become available"""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                return False

def main():
    # Start simple Flask app
    flask_process = subprocess.Popen([sys.executable, "simple_flask_test.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print("Starting simple Flask app...")

    if not wait_for_port("localhost", 5000, timeout=30):
        print("Error: Simple Flask app did not start within timeout.")
        flask_process.terminate()
        sys.exit(1)

    print("Simple Flask app is running. Testing basic response...")

    # Run basic test
    test_process = subprocess.Popen([sys.executable, "test_flask_basic.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = test_process.communicate()

    print("Test output:")
    print(out.decode())
    if err:
        print("Test errors:", err.decode())

    # Terminate Flask app
    flask_process.terminate()
    flask_process.wait()

    print("Simple Flask app terminated.")

    sys.exit(test_process.returncode)

if __name__ == "__main__":
    main()
