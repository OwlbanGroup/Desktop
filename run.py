#!/usr/bin/env python3
"""
Owlban Group Integrated Application Runner

This script starts the integrated Flask web server that combines:
- Organizational Leadership Module
- Revenue Tracking
- NVIDIA AI Integration
- Earnings Dashboard Frontend

Usage:
    python run.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import organizational_leadership
        import revenue_tracking
        import nvidia_integration
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_server():
    """Start the Flask web server"""
    try:
        print("🚀 Starting Owlban Group Integrated Server...")
        print("📍 Server will be available at: http://localhost:5000")
        print("📊 Frontend: http://localhost:5000")
        print("🔗 API endpoints: http://localhost:5000/api/*")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)

        # Change to backend directory and run the server
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)

        # Run the Flask server
        subprocess.run([sys.executable, "app_server.py"], check=True)

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🐦 Owlban Group - Integrated Leadership & Revenue Platform")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("backend/app_server.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Start the server
    start_server()

if __name__ == "__main__":
    main()
