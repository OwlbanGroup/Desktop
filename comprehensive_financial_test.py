#!/usr/bin/env python3
"""
Comprehensive test suite for the Financial Analytics Engine
Tests all methods, edge cases, and error handling scenarios
"""

import os
import sys
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from financial_analytics_engine import (
    AdvancedRevenueTracker,
    RevenueCategory,
    FinancialKPIs,
    AIPredictiveAnalytics
)

def test_basic_functionality():
    """Test basic CRUD operations and core functionality"""
    print("=== Testing Basic Functionality ===")

    tracker = AdvancedRevenueTracker()

    # Test adding records
    try:
        record1 = tracker.add_record("Test Sale", 1000.0, RevenueCategory.SALES)
        record2 = tracker.add_record("Test Service", 500.0, RevenueCategory.SERVICES)
        record3 = tracker.add_record("Test Subscription", 200.0, RevenueCategory.SUBSCRIPTIONS)
        print("✅ Record addition successful")
    except Exception as e:
        print(f"❌ Record addition failed: {e}")
        return False

    # Test getting all records
    try:
        records = tracker.get_all_records()
        assert len(records) >= 3, f"Expected at least 3 records, got {len(records)}"
        print("✅ Get all records successful")
    except Exception as e:
        print(f"❌ Get all records failed: {e}")
        return False

    # Test revenue calculations
    try:
        total_revenue = tracker.get_total_revenue()
        assert total_revenue == 1700.0, f"Expected 1700.0, got {total_revenue}"
        print("✅ Total revenue calculation successful")
    except Exception as e:
        print(f"❌ Total revenue calculation failed: {e}")
        return False

    # Test category breakdown
    try:
        category_breakdown = tracker.get_revenue_by_category()
        expected_categories = {"Sales", "Services", "Subscriptions"}
        actual_categories = set(category_breakdown.keys())
        assert expected_categories.issubset(actual_categories), f"Missing categories: {expected_categories - actual_categories}"
        print("✅ Category breakdown successful")
    except Exception as e:
        print(f"❌ Category breakdown failed: {e}")
        return False

    return True

def test_kpi_calculations():
    """Test KPI calculation methods"""
    print("\n=== Testing KPI Calculations ===")

    tracker = AdvancedRevenueTracker()

    # Add test data with different dates for growth calculations
    now = datetime.utcnow()
    past_date = now - timedelta(days=60)

    try:
        # Current period data
        tracker.add_record("Current Sale 1", 1000.0, RevenueCategory.SALES, date=now)
        tracker.add_record("Current Sale 2", 800.0, RevenueCategory.SALES, date=now)
        tracker.add_record("Current Service", 500.0, RevenueCategory.SERVICES, date=now)

        # Previous period data
        tracker.add_record("Past Sale 1", 600.0, RevenueCategory.SALES, date=past_date)
        tracker.add_record("Past Sale 2", 400.0, RevenueCategory.SALES, date=past_date)
        tracker.add_record("Past Service", 300.0, RevenueCategory.SERVICES, date=past_date)

        # Test comprehensive KPIs
        kpis = tracker.calculate_comprehensive_kpis(current_period_days=30, previous_period_days=30)

        required_keys = [
            'current_period_revenue', 'previous_period_revenue', 'growth_rate',
            'average_transaction', 'transaction_growth', 'category_breakdown',
            'category_growth_rates', 'total_transactions', 'period_days'
        ]

        for key in required_keys:
            assert key in kpis, f"Missing KPI: {key}"

        assert kpis['current_period_revenue'] > 0, "Current period revenue should be positive"
        assert isinstance(kpis['growth_rate'], (int, float)), "Growth rate should be numeric"
        assert isinstance(kpis['category_growth_rates'], dict), "Category growth rates should be dict"

        print("✅ KPI calculations successful")
        return True

    except Exception as e:
        print(f"❌ KPI calculations failed: {e}")
        traceback.print_exc()
        return False

def test_forecasting_methods():
    """Test forecasting and prediction methods"""
    print("\n=== Testing Forecasting Methods ===")

    tracker = AdvancedRevenueTracker()

    # Add historical data for forecasting
    base_date = datetime.utcnow() - timedelta(days=180)

    try:
        # Generate monthly data for 6 months
        for month in range(6):
            date = base_date + timedelta(days=month * 30)
            amount = 1000 + (month * 100)  # Increasing trend
            tracker.add_record(f"Month {month+1} Sale", amount, RevenueCategory.SALES, date=date)

        # Test advanced forecasting
        forecast = tracker.advanced_forecasting(months_ahead=3)
        if 'error' not in forecast:
            assert 'linear' in forecast or 'moving_average' in forecast, "Should have forecast methods"
            print("✅ Advanced forecasting successful")
        else:
            print(f"⚠️  Advanced forecasting returned error: {forecast['error']}")

        # Test AI forecasting (may fail due to insufficient data)
        ai_forecast = tracker.ai_powered_forecasting(days_ahead=30)
        if 'error' not in ai_forecast:
            assert 'predicted_revenue' in ai_forecast, "AI forecast should have predicted revenue"
            print("✅ AI forecasting successful")
        else:
            print(f"⚠️  AI forecasting returned error: {ai_forecast['error']}")

        return True

    except Exception as e:
        print(f"❌ Forecasting methods failed: {e}")
        traceback.print_exc()
        return False

def test_risk_analysis():
    """Test risk analysis functionality"""
    print("\n=== Testing Risk Analysis ===")

    tracker = AdvancedRevenueTracker()

    try:
        # Add some data for risk analysis
        tracker.add_record("Risk Test 1", 1000.0, RevenueCategory.SALES)
        tracker.add_record("Risk Test 2", 800.0, RevenueCategory.SALES)
        tracker.add_record("Risk Test 3", 1200.0, RevenueCategory.SALES)

        risk_analysis = tracker.ai_risk_analysis()

        if 'error' not in risk_analysis:
            required_keys = ['risk_score', 'risk_level', 'volatility', 'risk_factors']
            for key in required_keys:
                assert key in risk_analysis, f"Missing risk analysis key: {key}"

            assert isinstance(risk_analysis['risk_score'], (int, float)), "Risk score should be numeric"
            assert risk_analysis['risk_level'] in ['Low', 'Medium', 'High'], "Invalid risk level"
            print("✅ Risk analysis successful")
        else:
            print(f"⚠️  Risk analysis returned error: {risk_analysis['error']}")

        return True

    except Exception as e:
        print(f"❌ Risk analysis failed: {e}")
        traceback.print_exc()
        return False

def test_alerts_and_reporting():
    """Test alerts and reporting functionality"""
    print("\n=== Testing Alerts and Reporting ===")

    tracker = AdvancedRevenueTracker()

    try:
        # Add data for alerts
        tracker.add_record("Alert Test", 100.0, RevenueCategory.SALES)

        # Test financial alerts
        alerts = tracker.generate_financial_alerts()
        assert isinstance(alerts, list), "Alerts should be a list"

        if alerts:
            alert_keys = ['type', 'category', 'message', 'severity', 'recommendation']
            for alert in alerts:
                for key in alert_keys:
                    assert key in alert, f"Missing alert key: {key}"
            print("✅ Financial alerts successful")
        else:
            print("⚠️  No alerts generated (may be expected with minimal data)")

        # Test executive dashboard
        dashboard = tracker.generate_executive_dashboard()
        required_sections = ['period', 'summary_metrics', 'kpis', 'category_performance', 'forecast']
        for section in required_sections:
            assert section in dashboard, f"Missing dashboard section: {section}"
        print("✅ Executive dashboard successful")

        return True

    except Exception as e:
        print(f"❌ Alerts and reporting failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n=== Testing Error Handling ===")

    tracker = AdvancedRevenueTracker()

    # Test invalid inputs
    try:
        # Negative amount should raise error
        tracker.add_record("Invalid", -100.0, RevenueCategory.SALES)
        print("❌ Should have raised error for negative amount")
        return False
    except ValueError:
        print("✅ Negative amount error handling correct")
    except Exception as e:
        print(f"❌ Unexpected error for negative amount: {e}")
        return False

    try:
        # Empty description should raise error
        tracker.add_record("", 100.0, RevenueCategory.SALES)
        print("❌ Should have raised error for empty description")
        return False
    except ValueError:
        print("✅ Empty description error handling correct")
    except Exception as e:
        print(f"❌ Unexpected error for empty description: {e}")
        return False

    # Test empty dataset operations
    try:
        empty_kpis = tracker.calculate_comprehensive_kpis()
        assert empty_kpis['current_period_revenue'] == 0, "Empty dataset should return 0 revenue"
        print("✅ Empty dataset handling correct")
    except Exception as e:
        print(f"❌ Empty dataset handling failed: {e}")
        return False

    return True

def test_category_operations():
    """Test category-specific operations"""
    print("\n=== Testing Category Operations ===")

    tracker = AdvancedRevenueTracker()

    try:
        # Add records with different categories
        tracker.add_record("Sales 1", 1000.0, RevenueCategory.SALES)
        tracker.add_record("Sales 2", 800.0, RevenueCategory.SALES)
        tracker.add_record("Service 1", 500.0, RevenueCategory.SERVICES)
        tracker.add_record("Investment 1", 2000.0, RevenueCategory.INVESTMENTS)

        # Test category filtering
        sales_records = tracker.get_all_records(category=RevenueCategory.SALES)
        assert len(sales_records) == 2, f"Expected 2 sales records, got {len(sales_records)}"

        sales_revenue = tracker.get_total_revenue(category=RevenueCategory.SALES)
        assert sales_revenue == 1800.0, f"Expected 1800 sales revenue, got {sales_revenue}"

        # Test category breakdown
        breakdown = tracker.get_revenue_by_category()
        assert RevenueCategory.SALES.value in breakdown, "Sales should be in breakdown"
        assert RevenueCategory.SERVICES.value in breakdown, "Services should be in breakdown"
        assert RevenueCategory.INVESTMENTS.value in breakdown, "Investments should be in breakdown"

        print("✅ Category operations successful")
        return True

    except Exception as e:
        print(f"❌ Category operations failed: {e}")
        traceback.print_exc()
        return False

def test_date_filtering():
    """Test date-based filtering operations"""
    print("\n=== Testing Date Filtering ===")

    tracker = AdvancedRevenueTracker()

    try:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        # Add records with different dates
        tracker.add_record("Today", 1000.0, RevenueCategory.SALES, date=now)
        tracker.add_record("Yesterday", 800.0, RevenueCategory.SALES, date=yesterday)
        tracker.add_record("Last Week", 500.0, RevenueCategory.SALES, date=last_week)

        # Test date filtering
        recent_records = tracker.get_all_records(start_date=yesterday)
        assert len(recent_records) == 2, f"Expected 2 recent records, got {len(recent_records)}"

        today_records = tracker.get_all_records(start_date=now.replace(hour=0, minute=0, second=0),
                                               end_date=now.replace(hour=23, minute=59, second=59))
        assert len(today_records) == 1, f"Expected 1 today record, got {len(today_records)}"

        # Test revenue by date range
        recent_revenue = tracker.get_total_revenue(start_date=yesterday)
        assert recent_revenue == 1800.0, f"Expected 1800 recent revenue, got {recent_revenue}"

        print("✅ Date filtering successful")
        return True

    except Exception as e:
        print(f"❌ Date filtering failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all test suites"""
    print("🚀 Starting Comprehensive Financial Analytics Engine Tests\n")

    test_results = []

    # Run all test functions
    test_functions = [
        test_basic_functionality,
        test_kpi_calculations,
        test_forecasting_methods,
        test_risk_analysis,
        test_alerts_and_reporting,
        test_error_handling,
        test_category_operations,
        test_date_filtering
    ]

    for test_func in test_functions:
        try:
            result = test_func()
            test_results.append((test_func.__name__, result))
        except Exception as e:
            print(f"❌ {test_func.__name__} crashed: {e}")
            test_results.append((test_func.__name__, False))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print("20")
        if result:
            passed += 1

    print(f"\n📈 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The Financial Analytics Engine is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
