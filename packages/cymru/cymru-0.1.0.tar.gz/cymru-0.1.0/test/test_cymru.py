import unittest
import base64
import responses
import yaml
from unittest.mock import patch
from cymru.cymru import CymruScout


class TestCymruScout(unittest.TestCase):
    """Test suite for CymruScout class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.username = "test_user"
        self.password = "test_pass"
        self.base_url = "https://scout.cymru.com/api/scout"
        
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        scout = CymruScout(api_key=self.api_key)
        self.assertEqual(scout.api_key, self.api_key)
        self.assertIsNone(scout.username)
        self.assertIsNone(scout.password)
        self.assertEqual(scout.base_url, self.base_url)
        
    def test_init_with_username_password(self):
        """Test initialization with username and password"""
        scout = CymruScout(username=self.username, password=self.password)
        self.assertIsNone(scout.api_key)
        self.assertEqual(scout.username, self.username)
        self.assertEqual(scout.password, self.password)
        self.assertEqual(scout.base_url, self.base_url)
        
    def test_init_with_all_credentials(self):
        """Test initialization with all credentials provided"""
        scout = CymruScout(api_key=self.api_key, username=self.username, password=self.password)
        self.assertEqual(scout.api_key, self.api_key)
        self.assertEqual(scout.username, self.username)
        self.assertEqual(scout.password, self.password)
        
    def test_init_without_credentials(self):
        """Test initialization without any credentials raises ValueError"""
        with self.assertRaises(ValueError) as context:
            CymruScout()
        self.assertIn("Either an API key or username/password must be provided", str(context.exception))
        
    def test_init_with_incomplete_credentials(self):
        """Test initialization with incomplete username/password raises ValueError"""
        with self.assertRaises(ValueError):
            CymruScout(username=self.username)
        with self.assertRaises(ValueError):
            CymruScout(password=self.password)
            
    def test_build_auth_header_with_api_key(self):
        """Test building auth header with API key"""
        scout = CymruScout(api_key=self.api_key)
        header = scout._build_auth_header()
        expected = {'Authorization': f"Bearer {self.api_key}"}
        self.assertEqual(header, expected)
        
    def test_build_auth_header_with_username_password(self):
        """Test building auth header with username/password"""
        scout = CymruScout(username=self.username, password=self.password)
        header = scout._build_auth_header()
        expected_credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        expected = {'Authorization': f"Basic {expected_credentials}"}
        self.assertEqual(header, expected)
        
    def test_encode_credentials(self):
        """Test encoding credentials for Basic Auth"""
        scout = CymruScout(username=self.username, password=self.password)
        encoded = scout._encode_credentials()
        expected = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        self.assertEqual(encoded, expected)
        
    @responses.activate
    def test_search_basic(self):
        """Test basic search functionality"""
        responses._add_from_file(file_path="test/responses.yml")
        
        scout = CymruScout(api_key=self.api_key)
        result = scout.search('openports.banner = "*siemens*" openports.port = "102"')
        self.assertEqual(result["size"], 5000)
        
        # Verify the request was made correctly
        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertIn(
            "query=openports.banner+%3D+%22%2Asiemens%2A%22+openports.port+%3D+%22102%22",
            request.url
        )
        self.assertEqual(request.headers['Authorization'], f"Bearer {self.api_key}")
        
    @responses.activate
    def test_search_with_all_parameters(self):
        """Test search with all optional parameters"""
        scout = CymruScout(api_key=self.api_key)
        
        mock_response = {"results": []}
        responses.add(
            responses.GET,
            f"{self.base_url}/search",
            json=mock_response,
            status=200
        )
        
        result = scout.search(
            query="test",
            start_date="2023-01-01",
            end_date="2023-01-31",
            days=30,
            size=100
        )
        
        self.assertEqual(result, mock_response)
        request = responses.calls[0].request
        self.assertIn("query=test", request.url)
        self.assertIn("start_date=2023-01-01", request.url)
        self.assertIn("end_date=2023-01-31", request.url)
        self.assertIn("days=30", request.url)
        self.assertIn("size=100", request.url)
        
    @responses.activate
    def test_search_error_response(self):
        """Test search with error response"""
        scout = CymruScout(api_key=self.api_key)
        
        responses.add(
            responses.GET,
            f"{self.base_url}/search",
            json={"error": "Bad request"},
            status=400
        )
        
        with self.assertRaises(Exception) as context:
            scout.search("test")
        self.assertIn("Error: 400", str(context.exception))
        
    @responses.activate
    def test_ip_details_basic(self):
        """Test basic IP details functionality"""
        responses._add_from_file(file_path="test/responses.yml")
        
        scout = CymruScout(api_key=self.api_key)
        test_ip = "1.1.1.1"
        
        result = scout.ip_details(test_ip)
        self.assertEqual(result["whois"]["as_name"], "Cloudflare, Inc.")
        
        request = responses.calls[0].request
        self.assertEqual(request.headers['Authorization'], f"Bearer {self.api_key}")
        
    @responses.activate
    def test_ip_details_with_all_parameters(self):
        """Test IP details with all optional parameters"""
        scout = CymruScout(api_key=self.api_key)
        test_ip = "1.2.3.4"
        
        mock_response = {"ip": test_ip, "sections": ["summary", "comms"]}
        responses.add(
            responses.GET,
            f"{self.base_url}/ip/{test_ip}/details",
            json=mock_response,
            status=200
        )
        
        result = scout.ip_details(
            ip=test_ip,
            start_date="2023-01-01",
            end_date="2023-01-31",
            days=30,
            size=50,
            sections="summary,comms"
        )
        
        self.assertEqual(result, mock_response)
        request = responses.calls[0].request
        self.assertIn("start_date=2023-01-01", request.url)
        self.assertIn("end_date=2023-01-31", request.url)
        self.assertIn("days=30", request.url)
        self.assertIn("size=50", request.url)
        self.assertIn("sections=summary%2Ccomms", request.url)
        
    @responses.activate
    def test_ip_details_error_response(self):
        """Test IP details with error response"""
        scout = CymruScout(api_key=self.api_key)
        test_ip = "1.2.3.4"
        
        responses.add(
            responses.GET,
            f"{self.base_url}/ip/{test_ip}/details",
            json={"error": "Not found"},
            status=404
        )
        
        with self.assertRaises(Exception) as context:
            scout.ip_details(test_ip)
        self.assertIn("Error: 404", str(context.exception))
        
    @responses.activate
    def test_foundation_basic(self):
        """Test basic foundation functionality"""
        responses._add_from_file(file_path="test/responses.yml")
        
        scout = CymruScout(api_key=self.api_key)
        test_ips = ["104.18.213.12", "93.184.216.34"]
        
        result = scout.foundation(test_ips)
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["ip"], "104.18.213.12")
        self.assertEqual(result["data"][1]["ip"], "93.184.216.34")
        self.assertEqual(result["data"][0]["country_code"], "US")
        
        request = responses.calls[0].request
        self.assertEqual(request.headers['Authorization'], f"Bearer {self.api_key}")
        
    def test_foundation_invalid_input(self):
        """Test foundation with invalid input type"""
        scout = CymruScout(api_key=self.api_key)
        
        with self.assertRaises(ValueError) as context:
            scout.foundation("1.2.3.4")  # String instead of list
        self.assertIn("IPs must be provided as a list", str(context.exception))
        
        with self.assertRaises(ValueError):
            scout.foundation({"ip": "1.2.3.4"})  # Dict instead of list
            
    @responses.activate
    def test_foundation_error_response(self):
        """Test foundation with error response"""
        scout = CymruScout(api_key=self.api_key)
        test_ips = ["1.2.3.4"]
        
        responses.add(
            responses.GET,
            f"{self.base_url}/ip/foundation",
            json={"error": "Server error"},
            status=500
        )
        
        with self.assertRaises(Exception) as context:
            scout.foundation(test_ips)
        self.assertIn("Error: 500", str(context.exception))
        
    @responses.activate
    def test_usage_basic(self):
        """Test basic usage functionality"""
        responses._add_from_file(file_path="test/responses.yml")
        scout = CymruScout(api_key=self.api_key)
        
        result = scout.usage()
        self.assertEqual(result["used_queries"], 61)
        
        request = responses.calls[0].request
        self.assertEqual(request.headers['Authorization'], f"Bearer {self.api_key}")
        
    @responses.activate
    def test_usage_error_response(self):
        """Test usage with error response"""
        scout = CymruScout(api_key=self.api_key)
        
        responses.add(
            responses.GET,
            f"{self.base_url}/usage",
            json={"error": "Unauthorized"},
            status=401
        )
        
        with self.assertRaises(Exception) as context:
            scout.usage()
        self.assertIn("Error: 401", str(context.exception))
        
    @responses.activate
    def test_auth_with_username_password(self):
        """Test authentication using username/password for all methods"""
        scout = CymruScout(username=self.username, password=self.password)
        expected_credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        expected_auth = f"Basic {expected_credentials}"
        
        # Test search with basic auth
        responses.add(
            responses.GET,
            f"{self.base_url}/search",
            json={"results": []},
            status=200
        )
        
        scout.search("test")
        request = responses.calls[0].request
        self.assertEqual(request.headers['Authorization'], expected_auth)
        
        # Test ip_details with basic auth
        responses.add(
            responses.GET,
            f"{self.base_url}/ip/1.2.3.4/details",
            json={"ip": "1.2.3.4"},
            status=200
        )
        
        scout.ip_details("1.2.3.4")
        request = responses.calls[1].request
        self.assertEqual(request.headers['Authorization'], expected_auth)
        
        # Test foundation with basic auth
        responses.add(
            responses.GET,
            f"{self.base_url}/ip/foundation",
            json={"foundation_data": {}},
            status=200
        )
        
        scout.foundation(["1.2.3.4"])
        request = responses.calls[2].request
        self.assertEqual(request.headers['Authorization'], expected_auth)
        
        # Test usage with basic auth
        responses.add(
            responses.GET,
            f"{self.base_url}/usage",
            json={"queries_made": 0},
            status=200
        )
        
        scout.usage()
        request = responses.calls[3].request
        self.assertEqual(request.headers['Authorization'], expected_auth)
        
    @responses.activate
    def test_api_key_priority_over_username_password(self):
        """Test that API key takes priority when both API key and username/password are provided"""
        scout = CymruScout(api_key=self.api_key, username=self.username, password=self.password)
        
        responses.add(
            responses.GET,
            f"{self.base_url}/search",
            json={"results": []},
            status=200
        )
        
        scout.search("test")
        request = responses.calls[0].request
        self.assertEqual(request.headers['Authorization'], f"Bearer {self.api_key}")
        
    def test_empty_ip_list_foundation(self):
        """Test foundation with empty IP list"""
        scout = CymruScout(api_key=self.api_key)
        
        # Empty list should still be valid input
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{self.base_url}/ip/foundation",
                json={"foundation_data": {}},
                status=200
            )
            
            result = scout.foundation([])
            self.assertEqual(result, {"foundation_data": {}})


if __name__ == '__main__':
    unittest.main()
