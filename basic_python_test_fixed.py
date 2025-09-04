#!/usr/bin/env python3

import sys
import os

# Write to file immediately
with open('basic_python_output.txt', 'w', encoding='utf-8') as f:
    f.write("Testing basic Python functionality...\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Current working directory: {os.getcwd()}\n")

try:
    # Test basic imports
    import json
    with open('basic_python_output.txt', 'a', encoding='utf-8') as f:
        f.write("[PASS] json imported successfully\n")

    # Test basic operations
    data = {"test": "value", "number": 42}
    json_str = json.dumps(data)
    with open('basic_python_output.txt', 'a', encoding='utf-8') as f:
        f.write(f"[PASS] JSON serialization works: {json_str}\n")

    # Test file operations
    with open('test_file.txt', 'w', encoding='utf-8') as test_file:
        test_file.write("This is a test file")
    with open('basic_python_output.txt', 'a', encoding='utf-8') as f:
        f.write("[PASS] File operations work\n")

    # Test list comprehension
    numbers = [x for x in range(10)]
    with open('basic_python_output.txt', 'a', encoding='utf-8') as f:
        f.write(f"[PASS] List comprehension works: {numbers}\n")

    with open('basic_python_output.txt', 'a', encoding='utf-8') as f:
        f.write("[SUCCESS] All basic Python tests passed!\n")

except Exception as e:
    with open('basic_python_output.txt', 'a', encoding='utf-8') as f:
        f.write(f"[ERROR] Error: {e}\n")
        import traceback
        f.write(traceback.format_exc() + "\n")

print("Basic Python test completed. Check basic_python_output.txt for results.")
