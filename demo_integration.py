#!/usr/bin/env python3
"""
Demo script for NVIDIA OSCAR-BROOME-REVENUE Integration Platform

This script demonstrates the key features of the integration platform.
"""

import sys
import os
import time
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_monitoring():
    """Demonstrate GPU monitoring functionality."""
    print("🚀 Starting NVIDIA GPU Monitoring Demo...")
    print("=" * 50)

    try:
        from nvidia_oscar_broome_integration import NVIDIAMonitor

        monitor = NVIDIAMonitor()
        print("✅ Monitor initialized")

        # Start monitoring
        monitor.start_monitoring()
        print("✅ Monitoring started")

        # Let it run for a few seconds
        print("📊 Collecting data for 3 seconds...")
        time.sleep(3)

        # Stop monitoring
        monitor.stop_monitoring()
        print("✅ Monitoring stopped")

        # Show collected data
        print("\n📈 Collected Data:")
        print(f"GPU Data: {monitor.gpu_data}")
        print(f"System Info: {monitor.system_info}")

        return True

    except Exception as e:
        print(f"❌ Monitoring demo failed: {e}")
        return False

def demo_flask_app():
    """Demonstrate Flask API functionality."""
    print("\n🌐 Starting Flask API Demo...")
    print("=" * 50)

    try:
        from nvidia_oscar_broome_integration import app

        # Test client
        client = app.test_client()
        client.testing = True

        # Test health endpoint
        print("Testing health endpoint...")
        response = client.get('/api/health')
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")

        # Test system info endpoint
        print("Testing system info endpoint...")
        response = client.get('/api/system/info')
        if response.status_code == 200:
            print("✅ System info endpoint working")
        else:
            print(f"❌ System info endpoint failed: {response.status_code}")

        # Test dashboard rendering
        print("Testing dashboard rendering...")
        response = client.get('/')
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            if 'NVIDIA OSCAR-BROOME-REVENUE' in html_content:
                print("✅ Dashboard rendering working")
            else:
                print("❌ Dashboard content missing")
        else:
            print(f"❌ Dashboard rendering failed: {response.status_code}")

        return True

    except Exception as e:
        print(f"❌ Flask demo failed: {e}")
        return False

def demo_requirements():
    """Demonstrate NVIDIA requirements display."""
    print("\n⚙️  NVIDIA Requirements Demo...")
    print("=" * 50)

    try:
        from nvidia_oscar_broome_integration import NVIDIA_REQUIREMENTS

        print("📋 NVIDIA System Requirements:")
        for key, value in NVIDIA_REQUIREMENTS.items():
            print(f"  {key}: {value}")

        return True

    except Exception as e:
        print(f"❌ Requirements demo failed: {e}")
        return False

def demo_global_state():
    """Demonstrate global state management."""
    print("\n🔄 Global State Management Demo...")
    print("=" * 50)

    try:
        from nvidia_oscar_broome_integration import (
            gpu_monitoring_data,
            system_metrics,
            NVIDIA_REQUIREMENTS
        )

        print("📊 Global GPU Monitoring Data:")
        print(f"  Type: {type(gpu_monitoring_data)}")
        print(f"  Keys: {list(gpu_monitoring_data.keys()) if gpu_monitoring_data else 'Empty'}")

        print("\n📊 Global System Metrics:")
        print(f"  Type: {type(system_metrics)}")
        print(f"  Keys: {list(system_metrics.keys()) if system_metrics else 'Empty'}")

        print("\n📋 NVIDIA Requirements:")
        print(f"  Total requirements: {len(NVIDIA_REQUIREMENTS)}")

        return True

    except Exception as e:
        print(f"❌ Global state demo failed: {e}")
        return False

def run_full_demo():
    """Run complete integration demo."""
    print("🎯 NVIDIA OSCAR-BROOME-REVENUE INTEGRATION PLATFORM DEMO")
    print("=" * 60)
    print("This demo showcases the comprehensive integration between:")
    print("• NVIDIA GPU monitoring and control")
    print("• OSCAR-BROOME-REVENUE financial platform")
    print("• Real-time dashboard and API endpoints")
    print("• Enterprise-grade monitoring and analytics")
    print("=" * 60)

    demos = [
        demo_global_state,
        demo_requirements,
        demo_monitoring,
        demo_flask_app
    ]

    results = []
    for demo in demos:
        try:
            result = demo()
            results.append(result)
        except Exception as e:
            print(f"❌ Demo {demo.__name__} crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)

    successful = sum(results)
    total = len(results)

    print(f"✅ Successful demos: {successful}/{total}")

    if successful == total:
        print("\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("\n🚀 The NVIDIA OSCAR-BROOME-REVENUE Integration Platform is ready!")
        print("\nTo start the full application:")
        print("  python nvidia_oscar_broome_integration.py")
        print("\nThen visit: http://localhost:5000")
    else:
        print(f"\n⚠️  {total - successful} demo(s) failed")

    return successful == total

if __name__ == '__main__':
    success = run_full_demo()
    sys.exit(0 if success else 1)
