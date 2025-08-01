import base64
import requests

class CymruScout:
    def __init__(self, api_key=None, username=None, password=None):
        self.api_key  = api_key
        self.username = username
        self.password = password
        self.base_url = "https://scout.cymru.com/api/scout"
        
        self._check_credentials()
        
    def _check_credentials(self):
        """
        Ensure that either an API key or username/password is provided.
        Raises:
            ValueError: If neither an API key nor username/password is provided.
        """
        if not self.api_key and (not self.username or not self.password):
            raise ValueError("Either an API key or username/password must be provided.")
        
        
    def _build_auth_header(self):
        """
        Build the appropriate authorization header based on the provided credentials.
        Returns:
            dict: Authorization header for the request.
        """
        if self.api_key:
            return {'Authorization': f"Bearer {self.api_key}"}
        elif self.username and self.password:
            return {'Authorization': f"Basic {self._encode_credentials()}"}
        
        
    def _encode_credentials(self):
        """
        Encode the username and password for Basic Authentication.
        Returns:
            str: Base64 encoded credentials.
        """
        credentials = f"{self.username}:{self.password}"
        return base64.b64encode(credentials.encode()).decode()
        
        
    def search(self, query, start_date=None, end_date=None, days=None, size=None):
        """
        Search for data based on a query and optional date range.
        Args:
            query (str): The search query.
            start_date (str, optional): Start date in YYYY-MM-DD format in UTC time.
            end_date (str, optional): End date in YYYY-MM-DD format in UTC time.
            days (int, optional): Relative offset in days from current time in UTC. It cannot exceed the maximum range of days.
                    Note: this will take priority over start_date and end_date if all three are passed.
            size (int, optional): Number of results to return.
        Returns:
            dict: Search results containing the data matching the query.
        Raises:
            Exception: If the request fails or returns an error status code.  
        """
        headers = self._build_auth_header()
        
        params = {
            'query': query
        }
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if days:
            params['days'] = days
        if size:
            params['size'] = size

        response = requests.get(f"{self.base_url}/search", params=params, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        
        return response.json()
    
    
    def ip_details(self, ip, start_date=None, end_date=None, days=None, size=None, sections=None):
        """
        Get details for a specific IP address.
        Args:
            ip (str): The IP address to query.
            start_date (str, optional): Start date in YYYY-MM-DD format in UTC time.
            end_date (str, optional): End date in YYYY-MM-DD format in UTC time.
            days (int, optional): Relative offset in days from current time in UTC. It cannot exceed the maximum range of days.
                    Note: this will take priority over start_date and end_date if all three are passed.
            size (int, optional): Number of results to return.
            sections (str, optional): Comma-separated list of sections to return.
                    Possible sections: summary, proto_by_ip, comms, comms:client_server, open_ports, pdns, x509, fingerprints, whois.
                    Default sections: summary,comms,open_ports,pdns,x509,fingerprints,whois
                    A transformation can be applied to the comms section by sending in comms:client_server instead of comms.
                    This will replace "local" (the searched IP) and "peer" with the inferred client and server relationships.
        Returns:
            dict: Details of the IP address including various sections.
        Raises:
            Exception: If the request fails or returns an error status code.
        """
        headers = self._build_auth_header()
        
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if days:
            params['days'] = days
        if size:    
            params['size'] = size
        if sections:
            params['sections'] = sections

        response = requests.get(f"{self.base_url}/ip/{ip}/details", params=params, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        
        return response.json()
    
    
    def foundation(self, ips):
        """
        Get foundation data for a list of IP addresses.
        Args:
            ips (list): List of IP addresses to query.
        Returns:
            dict: Foundation data for the provided IP addresses.
        Raises:
            ValueError: If the provided IPs are not in a list format.
            Exception: If the request fails or returns an error status code.
        """
        headers = self._build_auth_header()
        
        if not isinstance(ips, list):
            raise ValueError("IPs must be provided as a list.")
        
        params = {'ips': ",".join(ips)}
        response = requests.get(f"{self.base_url}/ip/foundation", params=params, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        
        return response.json()
    
    
    def usage(self):
        """
        Get the usage statistics for the authenticated user.
        Returns:
            dict: Usage statistics including the number of queries made and the remaining quota.
        Raises:
            Exception: If the request fails or returns an error status code.
        """
        headers = self._build_auth_header()
        
        response = requests.get(f"{self.base_url}/usage", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        
        return response.json()

    