#!/usr/bin/env python3
"""
Test script for merger analytics module
"""

import sys
import os

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from merger_analytics import MergerAnalytics
    print("✓ Successfully imported MergerAnalytics")

    # Create instance and test basic functionality
    merger_analytics = MergerAnalytics()
    print("✓ Successfully created MergerAnalytics instance")

    # Test pre-merger performance
    pre_merger = merger_analytics.pre_merger_performance()
    print("✓ Pre-merger performance analysis:")
    for company, data in pre_merger.items():
        print(f"  {company}: Avg monthly revenue = ${data['average_monthly_revenue']:,.2f}")

    # Test synergy calculations
    synergies = merger_analytics.calculate_synergies()
    print("✓ Synergy estimates:")
    print(f"  Cost savings: ${synergies['cost_savings']:,.2f}")
    print(f"  Revenue enhancement: ${synergies['revenue_enhancement']:,.2f}")

    # Test risk assessment
    risks = merger_analytics.risk_assessment()
    print("✓ Risk assessment completed")
    print(f"  Integration risk: {risks['risks']['integration_risk']}")
    print(f"  Cultural risk: {risks['risks']['cultural_risk']}")

    # Test value realization timeline
    timeline = merger_analytics.value_realization_timeline()
    print("✓ Value realization timeline:")
    for item in timeline['timeline']:
        print(f"  Year {item['year']}: {item['expected_benefit_percentage']:.1f}% benefits realized")

    print("\n🎉 All merger analytics tests passed successfully!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during testing: {e}")
    sys.exit(1)
