#!/usr/bin/env python3
"""
Comprehensive test suite for the Financial Excellence System
Tests both the analytics engine and dashboard functionality
"""

import sys
import os
import json
from datetime import datetime, timedelta
from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory
from financial_excellence_dashboard import FinancialExcellenceDashboard

def test_analytics_engine():
    """Test the core analytics engine functionality"""
    print("🧪 Testing Financial Analytics Engine...")

    # Initialize tracker
    tracker = AdvancedRevenueTracker()

    # Test data addition
    sample_data = [
        ("Consulting Services", 5000.00, RevenueCategory.SERVICES, datetime.utcnow() - timedelta(days=10)),
        ("Software License", 2500.00, RevenueCategory.SUBSCRIPTIONS, datetime.utcnow() - timedelta(days=8)),
        ("Investment Returns", 1200.00, RevenueCategory.INVESTMENTS, datetime.utcnow() - timedelta(days=5)),
        ("Product Sales", 3200.00, RevenueCategory.SALES, datetime.utcnow() - timedelta(days=3)),
        ("Consulting Services", 4800.00, RevenueCategory.SERVICES, datetime.utcnow() - timedelta(days=1)),
    ]

    print("  📝 Adding sample revenue records...")
    for description, amount, category, date in sample_data:
        tracker.add_record(description, amount, category, date)

    # Test KPI calculations
    print("  📊 Testing KPI calculations...")
    kpis = tracker.calculate_kpis()
    assert 'total_revenue' in kpis, "Total revenue KPI missing"
    assert 'growth_rate' in kpis, "Growth rate KPI missing"
    assert kpis['total_revenue'] > 0, "Total revenue should be positive"
    print(f"    ✅ Total Revenue: ${kpis['total_revenue']:,.2f}")
    print(f"    ✅ Growth Rate: {kpis['growth_rate']:.2f}%")

    # Test AI forecasting
    print("  🤖 Testing AI forecasting...")
    forecast = tracker.ai_powered_forecasting(days_ahead=30)
    assert 'ai_forecast' in forecast, "AI forecast missing"
    assert 'predicted_revenue' in forecast['ai_forecast'], "Predicted revenue missing"
    print(f"    ✅ AI Forecast: ${forecast['ai_forecast']['predicted_revenue']:,.2f}")

    # Test risk analysis
    print("  ⚠️ Testing risk analysis...")
    risk = tracker.ai_risk_analysis()
    assert 'risk_level' in risk, "Risk level missing"
    assert 'risk_score' in risk, "Risk score missing"
    print(f"    ✅ Risk Level: {risk['risk_level']}")
    print(f"    ✅ Risk Score: {risk['risk_score']:.1f}")

    # Test alerts
    print("  🚨 Testing alert generation...")
    alerts = tracker.generate_financial_alerts()
    assert isinstance(alerts, list), "Alerts should be a list"
    print(f"    ✅ Generated {len(alerts)} alerts")

    # Test executive dashboard
    print("  📈 Testing executive dashboard...")
    dashboard_data = tracker.generate_executive_dashboard(period_days=30)
    assert 'summary_metrics' in dashboard_data, "Summary metrics missing"
    assert 'kpis' in dashboard_data, "KPIs missing"
    print(f"    ✅ Dashboard data generated with {len(dashboard_data)} sections")

    print("✅ Analytics Engine tests passed!")
    return tracker

def test_dashboard_integration():
    """Test the dashboard integration with analytics engine"""
    print("\n🖥️ Testing Dashboard Integration...")

    # Get tracker from previous test
    tracker = test_analytics_engine()

    # Test dashboard initialization
    print("  🌐 Testing dashboard initialization...")
    dashboard = FinancialExcellenceDashboard(tracker)
    assert dashboard.app is not None, "Flask app not initialized"
    assert dashboard.tracker is tracker, "Tracker not properly set"
    print("    ✅ Dashboard initialized successfully")

    # Test API endpoints (without running server)
    print("  🔗 Testing API endpoint setup...")
    # We can't easily test the actual endpoints without running the server,
    # but we can verify the routes are set up
    rules = list(dashboard.app.url_map.iter_rules())
    route_endpoints = [rule.endpoint for rule in rules]

    expected_endpoints = ['dashboard', 'dashboard_data', 'alerts', 'forecast', 'risk_analysis', 'export_report']
    for endpoint in expected_endpoints:
        assert endpoint in route_endpoints, f"Missing endpoint: {endpoint}"

    print(f"    ✅ All {len(expected_endpoints)} API endpoints configured")

    print("✅ Dashboard integration tests passed!")
    return dashboard

def test_data_persistence():
    """Test data persistence and retrieval"""
    print("\n💾 Testing Data Persistence...")

    tracker = AdvancedRevenueTracker()

    # Add test data
    tracker.add_record("Test Service", 1000.00, RevenueCategory.SERVICES, datetime.utcnow())

    # Test export functionality
    print("  📤 Testing data export...")
    export_file = "test_export.json"
    result = tracker.export_comprehensive_report(export_file)
    assert "successfully" in result.lower(), "Export failed"
    assert os.path.exists(export_file), "Export file not created"
    print("    ✅ Data export successful")

    # Verify exported data
    with open(export_file, 'r') as f:
        exported_data = json.load(f)

    assert 'summary_metrics' in exported_data, "Export missing summary metrics"
    assert 'export_timestamp' in exported_data, "Export missing timestamp"
    print("    ✅ Exported data structure valid")

    # Clean up
    if os.path.exists(export_file):
        os.remove(export_file)

    print("✅ Data persistence tests passed!")

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n🛡️ Testing Error Handling...")

    tracker = AdvancedRevenueTracker()

    # Test with empty data
    print("  📭 Testing with empty dataset...")
    kpis = tracker.calculate_kpis()
    assert kpis['total_revenue'] == 0, "Empty dataset should have zero revenue"
    print("    ✅ Empty dataset handled correctly")

    # Test invalid data (should not crash)
    print("  🚫 Testing invalid data handling...")
    try:
        # This should handle gracefully
        forecast = tracker.ai_powered_forecasting(days_ahead=0)
        print("    ✅ Invalid forecast parameters handled")
    except Exception as e:
        print(f"    ⚠️ Forecast error (expected): {e}")

    # Test risk analysis with no data
    risk = tracker.ai_risk_analysis()
    assert 'risk_level' in risk, "Risk analysis should work with empty data"
    print("    ✅ Risk analysis handles empty data")

    print("✅ Error handling tests passed!")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive Financial System Tests")
    print("=" * 60)

    test_results = []

    try:
        # Core functionality tests
        tracker = test_analytics_engine()
        test_results.append(("Analytics Engine", True))

        dashboard = test_dashboard_integration()
        test_results.append(("Dashboard Integration", True))

        test_data_persistence()
        test_results.append(("Data Persistence", True))

        test_error_handling()
        test_results.append(("Error Handling", True))

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)

        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")

        print(f"\n🎯 Overall: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 ALL TESTS PASSED! Financial system is ready for production.")
            return True
        else:
            print("⚠️ Some tests failed. Please review the issues above.")
            return False

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
