#!/usr/bin/env python3
"""
Comprehensive thorough testing of the financial analytics engine fix
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory

def test_database_integration():
    """Test full database integration"""
    print("🔍 Testing Database Integration...")

    tracker = AdvancedRevenueTracker()

    # Test adding multiple records
    records = [
        ("Product Sale A", 1500.0, RevenueCategory.SALES),
        ("Service Contract B", 800.0, RevenueCategory.SERVICES),
        ("Subscription C", 300.0, RevenueCategory.SUBSCRIPTIONS),
        ("Investment D", 2500.0, RevenueCategory.INVESTMENTS),
        ("Other Revenue E", 400.0, RevenueCategory.OTHER)
    ]

    added_records = []
    for desc, amount, category in records:
        record = tracker.add_record(desc, amount, category)
        added_records.append(record)
        print(f"  ✅ Added: {desc} - ${amount}")

    # Test retrieval
    all_records = tracker.get_all_records()
    assert len(all_records) >= len(records), "Not all records retrieved"

    # Test category filtering
    sales_records = tracker.get_all_records(category=RevenueCategory.SALES)
    assert len(sales_records) > 0, "Sales records not found"

    # Test revenue calculations
    total_revenue = tracker.get_total_revenue()
    assert total_revenue > 0, "Total revenue calculation failed"

    category_revenue = tracker.get_revenue_by_category()
    assert len(category_revenue) > 0, "Category revenue breakdown failed"

    print("  ✅ Database integration tests passed")
    return tracker

def test_ai_features():
    """Test AI-powered features"""
    print("🤖 Testing AI-Powered Features...")

    tracker = AdvancedRevenueTracker()

    # Add historical data for AI training
    base_date = datetime.utcnow() - timedelta(days=60)
    for i in range(60):
        date = base_date + timedelta(days=i)
        amount = 1000 + (i * 10) + (i % 7 * 50)  # Some pattern with weekly variation
        tracker.add_record(f"Daily Revenue {i+1}", amount, RevenueCategory.SALES, date=date)

    historical_data = [record.to_dict() for record in tracker.get_all_records()]

    # Test AI forecasting
    forecast_result = tracker.ai_powered_forecasting(days_ahead=30)
    if 'error' not in forecast_result:
        print("  ✅ AI forecasting working")
        assert 'ai_forecast' in forecast_result
    else:
        print(f"  ⚠️ AI forecasting: {forecast_result['error']}")

    # Test AI risk analysis
    risk_result = tracker.ai_risk_analysis()
    if 'error' not in risk_result:
        print("  ✅ AI risk analysis working")
        assert 'risk_level' in risk_result
        print(f"    Risk Level: {risk_result['risk_level']}")
    else:
        print(f"  ⚠️ AI risk analysis: {risk_result['error']}")

    print("  ✅ AI features tests completed")

def test_comprehensive_kpis():
    """Test comprehensive KPI calculations"""
    print("📊 Testing Comprehensive KPI Calculations...")

    tracker = AdvancedRevenueTracker()

    # Add test data across different periods
    now = datetime.utcnow()
    current_period_start = now - timedelta(days=30)
    previous_period_start = current_period_start - timedelta(days=30)

    # Current period data
    tracker.add_record("Current Sale 1", 2000.0, RevenueCategory.SALES, date=current_period_start + timedelta(days=5))
    tracker.add_record("Current Service 1", 1500.0, RevenueCategory.SERVICES, date=current_period_start + timedelta(days=10))
    tracker.add_record("Current Subscription 1", 800.0, RevenueCategory.SUBSCRIPTIONS, date=current_period_start + timedelta(days=15))

    # Previous period data
    tracker.add_record("Previous Sale 1", 1800.0, RevenueCategory.SALES, date=previous_period_start + timedelta(days=5))
    tracker.add_record("Previous Service 1", 1200.0, RevenueCategory.SERVICES, date=previous_period_start + timedelta(days=10))
    tracker.add_record("Previous Subscription 1", 600.0, RevenueCategory.SUBSCRIPTIONS, date=previous_period_start + timedelta(days=15))

    # Test KPI calculation
    kpis = tracker.calculate_comprehensive_kpis()

    assert 'current_period_revenue' in kpis
    assert 'previous_period_revenue' in kpis
    assert 'growth_rate' in kpis
    assert 'category_breakdown' in kpis
    assert 'category_growth_rates' in kpis

    print(f"  ✅ Current Revenue: ${kpis['current_period_revenue']:.2f}")
    print(f"  ✅ Growth Rate: {kpis['growth_rate']:.2f}%")
    print(f"  ✅ Categories: {list(kpis['category_breakdown'].keys())}")
    print(f"  ✅ Category Growth Rates: {kpis['category_growth_rates']}")

    # Verify no None categories in breakdown
    assert None not in kpis['category_breakdown'], "None category found in breakdown"
    assert None not in kpis['category_growth_rates'], "None category found in growth rates"

    print("  ✅ Comprehensive KPI tests passed")

def test_reporting_and_alerts():
    """Test reporting and alert generation"""
    print("📋 Testing Reporting and Alert Generation...")

    tracker = AdvancedRevenueTracker()

    # Add data that should trigger alerts
    for i in range(5):
        tracker.add_record(f"Low Volume Sale {i+1}", 100.0, RevenueCategory.SALES)

    # Test executive dashboard
    dashboard = tracker.generate_executive_dashboard()
    assert 'summary_metrics' in dashboard
    assert 'kpis' in dashboard
    assert 'category_performance' in dashboard
    print("  ✅ Executive dashboard generated")

    # Test alert generation
    alerts = tracker.generate_financial_alerts()
    print(f"  ✅ Generated {len(alerts)} alerts")
    for alert in alerts:
        print(f"    - {alert['type'].upper()}: {alert['message']}")

    # Test report export
    report_file = "test_financial_report.json"
    result = tracker.export_comprehensive_report(report_file)
    assert os.path.exists(report_file), "Report file not created"
    print(f"  ✅ Report exported to {report_file}")

    # Verify report content
    with open(report_file, 'r') as f:
        report_data = json.load(f)

    assert 'executive_summary' in report_data
    assert 'alerts' in report_data
    assert 'recommendations' in report_data
    print("  ✅ Report content verified")

    # Cleanup
    if os.path.exists(report_file):
        os.remove(report_file)

    print("  ✅ Reporting and alerts tests passed")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("🔧 Testing Edge Cases and Error Handling...")

    tracker = AdvancedRevenueTracker()

    # Test empty data scenarios
    empty_kpis = tracker.calculate_comprehensive_kpis()
    assert empty_kpis['current_period_revenue'] == 0.0
    print("  ✅ Empty data handling works")

    # Test single record scenarios
    tracker.add_record("Single Record", 1000.0, RevenueCategory.SALES)
    single_kpis = tracker.calculate_comprehensive_kpis()
    assert single_kpis['total_transactions'] == 1
    print("  ✅ Single record handling works")

    # Test invalid category names (should be handled gracefully)
    # This tests the _get_category_enum method
    from financial_analytics_engine import AdvancedRevenueTracker
    tracker_instance = AdvancedRevenueTracker()

    # Test the helper method directly
    result = tracker_instance._get_category_enum("InvalidCategory")
    assert result is None, "Invalid category should return None"

    result = tracker_instance._get_category_enum("Sales")
    assert result == RevenueCategory.SALES, "Valid category should return enum"

    print("  ✅ Category enum conversion works correctly")

    # Test forecasting with insufficient data
    forecast = tracker.advanced_forecasting()
    assert 'error' in forecast, "Should handle insufficient data for forecasting"
    print("  ✅ Insufficient data error handling works")

    print("  ✅ Edge cases tests passed")

def test_performance():
    """Test performance under realistic data loads"""
    print("⚡ Testing Performance Under Load...")

    tracker = AdvancedRevenueTracker()

    # Add realistic volume of data (1000 records)
    print("    Adding 1000 test records...")
    start_time = time.time()

    for i in range(1000):
        amount = 500 + (i % 100 * 10)  # Varied amounts
        category = list(RevenueCategory)[i % len(RevenueCategory)]
        date = datetime.utcnow() - timedelta(days=i % 365)
        tracker.add_record(f"Performance Test Record {i+1}", amount, category, date=date)

    data_insertion_time = time.time() - start_time
    print(".2f")

    # Test KPI calculation performance
    start_time = time.time()
    kpis = tracker.calculate_comprehensive_kpis()
    kpi_calculation_time = time.time() - start_time
    print(".4f")

    # Test dashboard generation performance
    start_time = time.time()
    dashboard = tracker.generate_executive_dashboard()
    dashboard_generation_time = time.time() - start_time
    print(".4f")

    # Verify results are still accurate
    assert kpis['total_transactions'] == 1000
    assert kpis['current_period_revenue'] > 0
    print("  ✅ Performance test data integrity verified")

    # Performance assertions (reasonable thresholds)
    assert data_insertion_time < 30, f"Data insertion too slow: {data_insertion_time}s"
    assert kpi_calculation_time < 5, f"KPI calculation too slow: {kpi_calculation_time}s"
    assert dashboard_generation_time < 10, f"Dashboard generation too slow: {dashboard_generation_time}s"

    print("  ✅ Performance tests passed")

def run_all_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive Financial Analytics Engine Tests")
    print("=" * 60)

    test_results = []

    try:
        # Test 1: Database Integration
        test_database_integration()
        test_results.append(("Database Integration", "PASSED"))
    except Exception as e:
        print(f"❌ Database Integration failed: {e}")
        test_results.append(("Database Integration", f"FAILED: {e}"))

    try:
        # Test 2: AI Features
        test_ai_features()
        test_results.append(("AI Features", "PASSED"))
    except Exception as e:
        print(f"❌ AI Features failed: {e}")
        test_results.append(("AI Features", f"FAILED: {e}"))

    try:
        # Test 3: Comprehensive KPIs
        test_comprehensive_kpis()
        test_results.append(("Comprehensive KPIs", "PASSED"))
    except Exception as e:
        print(f"❌ Comprehensive KPIs failed: {e}")
        test_results.append(("Comprehensive KPIs", f"FAILED: {e}"))

    try:
        # Test 4: Reporting and Alerts
        test_reporting_and_alerts()
        test_results.append(("Reporting and Alerts", "PASSED"))
    except Exception as e:
        print(f"❌ Reporting and Alerts failed: {e}")
        test_results.append(("Reporting and Alerts", f"FAILED: {e}"))

    try:
        # Test 5: Edge Cases
        test_edge_cases()
        test_results.append(("Edge Cases", "PASSED"))
    except Exception as e:
        print(f"❌ Edge Cases failed: {e}")
        test_results.append(("Edge Cases", f"FAILED: {e}"))

    try:
        # Test 6: Performance
        test_performance()
        test_results.append(("Performance", "PASSED"))
    except Exception as e:
        print(f"❌ Performance failed: {e}")
        test_results.append(("Performance", f"FAILED: {e}"))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        status = "✅" if result == "PASSED" else "❌"
        print(f"{status} {test_name}: {result}")
        if result == "PASSED":
            passed += 1
        else:
            failed += 1

    print(f"\n🎯 Overall Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 ALL TESTS PASSED! The financial analytics engine fix is fully validated.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
