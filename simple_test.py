#!/usr/bin/env python3
"""
Simple test to verify the financial analytics engine fix
"""

from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory

def main():
    print("🚀 Testing Financial Analytics Engine Fix")

    try:
        # Create tracker
        tracker = AdvancedRevenueTracker()
        print("✅ Tracker created successfully")

        # Add test data
        tracker.add_record('Test Sale', 1000.0, RevenueCategory.SALES)
        tracker.add_record('Test Service', 500.0, RevenueCategory.SERVICES)
        tracker.add_record('Test Subscription', 200.0, RevenueCategory.SUBSCRIPTIONS)
        print("✅ Test data added successfully")

        # Test the fixed method
        kpis = tracker.calculate_comprehensive_kpis()
        print("✅ KPI calculation successful")
        print(f"   Total revenue: {kpis['current_period_revenue']}")
        print(f"   Categories: {list(kpis['category_breakdown'].keys())}")
        print(f"   Category growth rates: {kpis['category_growth_rates']}")

        print("\n🎉 All tests passed! The fix is working correctly.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
