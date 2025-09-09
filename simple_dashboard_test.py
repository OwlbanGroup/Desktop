#!/usr/bin/env python3
"""
Simple test to verify the Financial Excellence Dashboard is working
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    try:
        print("Testing imports...")
        from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory
        print("✓ AdvancedRevenueTracker imported successfully")

        from financial_excellence_dashboard import FinancialExcellenceDashboard
        print("✓ FinancialExcellenceDashboard imported successfully")

        import plotly.graph_objects as go
        print("✓ Plotly imported successfully")

        import pandas as pd
        print("✓ Pandas imported successfully")

        import numpy as np
        print("✓ NumPy imported successfully")

        from sklearn.linear_model import LinearRegression
        print("✓ Scikit-learn imported successfully")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_creation():
    """Test database creation and basic operations"""
    try:
        print("\nTesting database operations...")
        from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory

        # Create tracker (this will create the database)
        tracker = AdvancedRevenueTracker()
        print("✓ Database created successfully")

        # Add a test record
        record = tracker.add_record(
            description="Test Revenue",
            amount=1000.00,
            category=RevenueCategory.SERVICES
        )
        print(f"✓ Test record added: {record.description}")

        # Get total revenue
        total = tracker.get_total_revenue()
        print(f"✓ Total revenue: ${total:.2f}")

        print("✅ Database operations successful!")
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_dashboard_creation():
    """Test dashboard creation"""
    try:
        print("\nTesting dashboard creation...")
        from financial_analytics_engine import AdvancedRevenueTracker
        from financial_excellence_dashboard import FinancialExcellenceDashboard

        tracker = AdvancedRevenueTracker()
        dashboard = FinancialExcellenceDashboard(tracker)
        print("✓ Dashboard created successfully")

        # Test dashboard data generation
        data = dashboard.tracker.generate_executive_dashboard(30)
        print("✓ Dashboard data generated successfully")

        print("✅ Dashboard creation successful!")
        return True

    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Financial Excellence Dashboard - System Test")
    print("=" * 50)

    results = []

    # Test imports
    results.append(test_imports())

    # Test database
    results.append(test_database_creation())

    # Test dashboard
    results.append(test_dashboard_creation())

    print("\n" + "=" * 50)
    print("📊 Test Results:")

    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo start the dashboard, run:")
        print("python financial_excellence_dashboard.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
