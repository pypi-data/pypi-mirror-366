# Cymru Scout Python Wrapper

A Python wrapper for [Cymru Scout HTTP API](https://scout.cymru.com/).
For more information on API usage please visit the [official documentation](https://scout.cymru.com/docs/scout/ultimate).

# Installation

```bash
pip install cymru
```

# Quick Start

```python
from cymru import CymruScout

# Initialize with API key (recommended)
scout = CymruScout(api_key="your_api_key")

# Or initialize with username/password
scout = CymruScout(username="your_username", password="your_password")

# Search for data
results = scout.search('openports.banner = "*siemens*" openports.port = "102"')

# Get IP details
ip_info = scout.ip_details("8.8.8.8")

# Get foundation data for multiple IPs
foundation_data = scout.foundation(["8.8.8.8", "1.1.1.1"])

# Check usage statistics
usage_stats = scout.usage()
```

# Documentation

## CymruScout Class

The main class for interacting with the Cymru Scout API.

### Initialization

```python
CymruScout(api_key=None, username=None, password=None)
```

**Parameters:**
- `api_key` (str, optional): Your Cymru Scout API key
- `username` (str, optional): Your Cymru Scout username
- `password` (str, optional): Your Cymru Scout password

**Note:** Either an API key or username/password combination must be provided. If both are provided, the API key takes priority.

**Raises:**
- `ValueError`: If neither an API key nor username/password is provided

### Methods

#### search(query, start_date=None, end_date=None, days=None, size=None)

Search for data based on a query and optional date range.

**Parameters:**
- `query` (str): The search query
- `start_date` (str, optional): Start date in YYYY-MM-DD format in UTC time
- `end_date` (str, optional): End date in YYYY-MM-DD format in UTC time
- `days` (int, optional): Relative offset in days from current time in UTC. Cannot exceed the maximum range of days. Takes priority over start_date and end_date if all three are passed
- `size` (int, optional): Number of results to return

**Returns:**
- `dict`: Search results containing the data matching the query

**Raises:**
- `Exception`: If the request fails or returns an error status code

**Example:**
```python
# Basic search
results = scout.search('openports.banner = "*siemens*" openports.port = "102"')

# Search with date range
results = scout.search('x509.subject.cn = "*vigor router*" | pdns.count = "1"', start_date="2023-01-01", end_date="2023-01-31")

# Search with relative days
results = scout.search('openports.port = "9200" openports.banner = "*kibana*" | comms.port = "9200"', days=7, size=50)
```

#### ip_details(ip, start_date=None, end_date=None, days=None, size=None, sections=None)

Get details for a specific IP address.

**Parameters:**
- `ip` (str): The IP address to query
- `start_date` (str, optional): Start date in YYYY-MM-DD format in UTC time
- `end_date` (str, optional): End date in YYYY-MM-DD format in UTC time
- `days` (int, optional): Relative offset in days from current time in UTC. Cannot exceed the maximum range of days. Takes priority over start_date and end_date if all three are passed
- `size` (int, optional): Number of results to return
- `sections` (str, optional): Comma-separated list of sections to return

**Available sections:**
- `summary`: Basic IP information
- `proto_by_ip`: Protocol information
- `comms`: Communications data
- `comms:client_server`: Communications with client/server transformation
- `open_ports`: Open ports information
- `pdns`: Passive DNS data
- `x509`: X.509 certificate data
- `fingerprints`: Fingerprint data
- `whois`: WHOIS information

**Default sections:** `summary,comms,open_ports,pdns,x509,fingerprints,whois`

**Returns:**
- `dict`: Details of the IP address including various sections

**Raises:**
- `Exception`: If the request fails or returns an error status code

**Example:**
```python
# Basic IP details
details = scout.ip_details("8.8.8.8")

# IP details with specific sections
details = scout.ip_details("8.8.8.8", sections="summary,whois,pdns")

# IP details with date range
details = scout.ip_details("8.8.8.8", days=30, size=100)
```

#### foundation(ips)

Get foundation data for a list of IP addresses.

**Parameters:**
- `ips` (list): List of IP addresses to query

**Returns:**
- `dict`: Foundation data for the provided IP addresses

**Raises:**
- `ValueError`: If the provided IPs are not in a list format
- `Exception`: If the request fails or returns an error status code

**Example:**
```python
# Get foundation data for multiple IPs
ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
foundation_data = scout.foundation(ips)

# Single IP (still requires list format)
foundation_data = scout.foundation(["192.168.1.1"])
```

#### usage()

Get the usage statistics for the authenticated user.

**Returns:**
- `dict`: Usage statistics including the number of queries made and the remaining quota

**Raises:**
- `Exception`: If the request fails or returns an error status code

**Example:**
```python
# Check your API usage
stats = scout.usage()
print(f"Queries made: {stats.get('queries_made', 0)}")
print(f"Quota remaining: {stats.get('quota_remaining', 0)}")
```

## Authentication

The wrapper supports two authentication methods:

### API Key Authentication (Recommended)
```python
scout = CymruScout(api_key="your_api_key")
```

### Username/Password Authentication
```python
scout = CymruScout(username="your_username", password="your_password")
```

If both authentication methods are provided, the API key takes priority.

## Error Handling

All methods may raise exceptions for various error conditions:

- **ValueError**: For invalid input parameters (e.g., missing credentials, invalid IP list format)
- **Exception**: For HTTP errors, network issues, or API errors

It's recommended to wrap API calls in try-catch blocks:

```python
try:
    results = scout.search('openports.banner = "*siemens*" openports.port = "102"')
    print("Search successful:", results)
except ValueError as e:
    print("Invalid parameters:", e)
except Exception as e:
    print("API error:", e)
```

## Testing

Run the test suite:

```bash
# Using the test runner script
python run_tests.py

# Or using unittest directly
python -m unittest test.test_cymru -v
```

## Requirements

- Python 3.5+
- requests >= 2.32.4

## License

GNU GPL v3
