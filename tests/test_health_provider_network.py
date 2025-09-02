import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nvidia_integration import NvidiaIntegration

def test_health_provider_network():
    """Test the get_health_provider_network method."""
    print("Testing get_health_provider_network method...")

    nvidia = NvidiaIntegration()

    try:
        result = nvidia.get_health_provider_network()

        print("✅ Method executed successfully!")
        print(f"Source: {result.get('source', 'N/A')}")
        print(f"Last updated: {result.get('last_updated', 'N/A')}")
        print(f"Number of providers: {len(result.get('providers', []))}")
        print(f"Number of resources: {len(result.get('resources', []))}")
        print(f"Number of links: {len(result.get('links', []))}")

        print("\n🏥 Providers:")
        for provider in result.get('providers', []):
            print(f"  • {provider}")

        print("\n🔗 Links:")
        for link in result.get('links', []):
            print(f"  • {link}")

        # Basic sanity checks
        assert isinstance(result.get('providers'), list), "Providers should be a list"
        assert isinstance(result.get('links'), list), "Links should be a list"

        return True

    except Exception as e:
        print(f"❌ Error testing method: {e}")
        return False

if __name__ == "__main__":
    success = test_health_provider_network()
    sys.exit(0 if success else 1)
