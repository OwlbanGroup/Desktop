try:
    from organizational_leadership import leadership
    print("organizational_leadership imported successfully")
except Exception as e:
    print(f"Error importing organizational_leadership: {e}")

try:
    from revenue_tracking import RevenueTracker
    print("revenue_tracking imported successfully")
except Exception as e:
    print(f"Error importing revenue_tracking: {e}")

try:
    from nvidia_integration import NvidiaIntegration
    print("nvidia_integration imported successfully")
except Exception as e:
    print(f"Error importing nvidia_integration: {e}")

try:
    from OSCAR_BROOME_REVENUE.earnings_dashboard import chase_mortgage
    print("chase_mortgage imported successfully")
    print(f"router: {chase_mortgage.router}")
except Exception as e:
    print(f"Error importing chase_mortgage: {e}")

try:
    from app_with_chase_integration import app
    print("app_with_chase_integration imported successfully")
    print(f"app: {app}")
except Exception as e:
    print(f"Error importing app_with_chase_integration: {e}")
