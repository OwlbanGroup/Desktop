#!/usr/bin/env python3

import sys
import os

# Write to file immediately
with open('flask_test_output.txt', 'w') as f:
    f.write("Testing Flask import...\n")

try:
    from flask import Flask
    with open('flask_test_output.txt', 'a') as f:
        f.write("✅ Flask imported successfully\n")
        f.write(f"Flask version: {Flask.__version__}\n")
except ImportError as e:
    with open('flask_test_output.txt', 'a') as f:
        f.write(f"❌ Flask import failed: {e}\n")
except Exception as e:
    with open('flask_test_output.txt', 'a') as f:
        f.write(f"❌ Flask error: {e}\n")

print("Flask test completed. Check flask_test_output.txt for results.")
