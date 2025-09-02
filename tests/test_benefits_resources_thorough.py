import unittest
from unittest.mock import patch, Mock
from nvidia_integration import NvidiaIntegration

class TestBenefitsResourcesThorough(unittest.TestCase):
    def setUp(self):
        self.nvidia = NvidiaIntegration()

    @patch('nvidia_integration.requests.get')
    def test_successful_scrape(self, mock_get):
        # Mock a successful HTML response with expected structure
        html_content = """
        <html>
            <body>
                <main>
                    <ul class="benefits-list">
                        <li>Business Travel Accident Insurance</li>
                        <li>Personal Loans</li>
                        <li>Schwab Financial Concierge</li>
                    </ul>
                    <a href="https://www.nvidia.com/en-us/benefits/money/business-travel-accident-insurance/">Business Travel Accident Insurance Link</a>
                    <a href="https://www.nvidia.com/en-us/benefits/money/personal-loans/">Personal Loans Link</a>
                </main>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_get.return_value = mock_response

        result = self.nvidia.get_benefits_resources()
        self.assertIn("Business Travel Accident Insurance", result.get("benefits", []))
        self.assertIn("Personal Loans", result.get("benefits", []))
        self.assertIn("https://www.nvidia.com/en-us/benefits/money/business-travel-accident-insurance/", result.get("links", []))
        self.assertIn("https://www.nvidia.com/en-us/benefits/money/personal-loans/", result.get("links", []))

    @patch('nvidia_integration.requests.get')
    def test_network_failure(self, mock_get):
        # Simulate network failure
        mock_get.side_effect = Exception("Network error")
        result = self.nvidia.get_benefits_resources()
        self.assertIn("error", result)
        self.assertEqual(result["benefits"], [])
        self.assertEqual(result["links"], [])

    @patch('nvidia_integration.requests.get')
    def test_invalid_html_structure(self, mock_get):
        # Simulate HTML with missing benefits list
        html_content = "<html><body><div>No benefits here</div></body></html>"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_get.return_value = mock_response

        result = self.nvidia.get_benefits_resources()
        self.assertEqual(result.get("benefits", []), [])
        self.assertTrue(isinstance(result.get("links", []), list))

    @patch('nvidia_integration.requests.get')
    def test_missing_links(self, mock_get):
        # Simulate HTML with benefits but no links
        html_content = """
        <html>
            <body>
                <main>
                    <ul class="benefits-list">
                        <li>Business Travel Accident Insurance</li>
                    </ul>
                </main>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_get.return_value = mock_response

        result = self.nvidia.get_benefits_resources()
        self.assertIn("Business Travel Accident Insurance", result.get("benefits", []))
        self.assertEqual(result.get("links", []), [])

if __name__ == "__main__":
    unittest.main()
