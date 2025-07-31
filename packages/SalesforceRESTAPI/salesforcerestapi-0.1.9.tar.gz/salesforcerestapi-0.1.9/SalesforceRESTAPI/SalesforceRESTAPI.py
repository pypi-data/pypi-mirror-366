
import requests
from typing import Optional, Dict, Any

class SalesforceRESTAPI:
    instance_url = None
    access_token = None
    headers = None
    last_http_status = None  # Stores the last HTTP status code
    @classmethod
    def get_last_http_status(cls):
        """
        Return the last HTTP status code from any API call (get, post, patch, delete).
        """
        return cls.last_http_status

    @staticmethod
    def authenticate(client_id: str, client_secret: str, login_url: str = 'https://login.salesforce.com') -> Dict[str, Any]:
        """
        Authenticate with Salesforce using OAuth 2.0 Client Credentials Flow and set instance_url and access_token as class variables.
        Returns the full auth response (including access_token and instance_url).
        Note: Your Salesforce org must be configured to support this flow and the connected app must have the correct permissions.
        """
        url = f"{login_url}/services/oauth2/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        auth = response.json()
        SalesforceRESTAPI.instance_url = auth['instance_url'].rstrip('/')
        SalesforceRESTAPI.access_token = auth['access_token']
        SalesforceRESTAPI.headers = {
            'Authorization': f'Bearer {SalesforceRESTAPI.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        return auth

    def delete_record(self, sobject: str, record_id: str) -> requests.Response:
        """
        Delete a Salesforce record by sObject type and record ID.
        Example: delete_record('Account', '001XXXXXXXXXXXXXXX')
        """
        endpoint = f"/services/data/v64.0/sobjects/{sobject}/{record_id}"
        return self.delete(endpoint)

    def update_record(self, sobject: str, record_id: str, **data) -> requests.Response:
        """
        Update a Salesforce record by sObject type and record ID.
        Example: update_record('Account', '001XXXXXXXXXXXXXXX', Name="Updated Name")
        """
        endpoint = f"/services/data/v64.0/sobjects/{sobject}/{record_id}"
        return self.patch(endpoint, data)

    def get_record(self, sobject: str, record_id: str) -> Optional[dict]:
        """
        Retrieve a Salesforce record by sObject type and record ID.
        Returns the record as a dict, or None if not found or error.
        Example: get_record('Account', '001XXXXXXXXXXXXXXX')
        """
        endpoint = f"/services/data/v64.0/sobjects/{sobject}/{record_id}"
        response = self.get(endpoint)
        try:
            return response.json()
        except Exception as e:
            print(f"Failed to parse Salesforce get_record response: {e}")
            return None


    def create_record(self, sobject: str, **data) -> Optional[str]:
        """
        Create a new Salesforce record for the given sObject type and return the new record's ID.
        Example: create_record('Account', Name="Test Account", Industry="Technology")
        Returns the Salesforce object ID if successful, otherwise None.
        """
        endpoint = f"/services/data/v64.0/sobjects/{sobject}"
        response = self.post(endpoint, data)
        try:
            result = response.json()
            return result.get('id')
        except Exception as e:
            print(f"Failed to parse Salesforce create response: {e}")
            return None
        
    def verify_record(self, sobject: str, record_id: str, **data) -> bool:
        """
        Retrieve a Salesforce record and verify that each field in data matches the record's value.
        Raises AssertionError if any field does not match.
        Returns True if all fields match.
        Example: verify_record('Account', '001XXXXXXXXXXXXXXX', Name="Test Account", Industry="Technology")
        """
        record = self.get_record(sobject, record_id)
        if record is None:
            raise AssertionError(f"Record {sobject} with ID {record_id} not found.")
        for key, value in data.items():
            if record.get(key) != value:
                raise AssertionError(f"Field '{key}' mismatch: expected '{value}', got '{record.get(key)}'")
        return True
    
    def queryRecords(self, soql: str) -> dict:
        """
        Run a SOQL query and return the parsed JSON response body.
        Example: queryRecords('SELECT Id, Name FROM Account')
        Returns the response as a dict.
        """
        response = self.run_query(soql)
        try:
            return response.json()
        except Exception as e:
            print(f"Failed to parse Salesforce queryRecords response: {e}")
            return {}
    

    def run_query(self, soql: str) -> requests.Response:
        """
        Execute a SOQL query using the Salesforce REST API.
        Example: run_query('SELECT Id, Name FROM Account')
        """
        endpoint = f"/services/data/v64.0/query"
        params = {"q": soql}
        return self.get(endpoint, params=params)
    
    """
    Simple Salesforce REST API manager for authentication and basic CRUD operations.
    """
    def __init__(self):
        self.instance_url = None
        self.access_token = None
        self.headers = None

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        if not SalesforceRESTAPI.access_token:
            raise RuntimeError("ValueError: Token not set. Please authenticate first.")
        url = f"{SalesforceRESTAPI.instance_url}{endpoint}"
        response = requests.get(url, headers=SalesforceRESTAPI.headers, params=params)
        SalesforceRESTAPI.last_http_status = response.status_code
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"GET {url} failed: {e} - {response.text}")
            raise
        return response

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        if not SalesforceRESTAPI.access_token:
            raise RuntimeError("ValueError: Token not set. Please authenticate first.")
        url = f"{SalesforceRESTAPI.instance_url}{endpoint}"
        response = requests.post(url, headers=SalesforceRESTAPI.headers, json=data)
        SalesforceRESTAPI.last_http_status = response.status_code
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            errors = response.json()
            if isinstance(errors, list) and errors:
                error_message = errors[0].get("message", str(e))
                print("Salesforce error:", error_message)
                raise RuntimeError(error_message)
            raise
        return response

    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        if not SalesforceRESTAPI.access_token:
            raise RuntimeError("ValueError: Token not set. Please authenticate first.")
        url = f"{SalesforceRESTAPI.instance_url}{endpoint}"
        response = requests.patch(url, headers=SalesforceRESTAPI.headers, json=data)
        SalesforceRESTAPI.last_http_status = response.status_code
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            errors = response.json()
            if isinstance(errors, list) and errors:
                error_message = errors[0].get("message", str(e))
                print("Salesforce error:", error_message)
                raise RuntimeError(error_message)
            raise
        return response

    def delete(self, endpoint: str) -> requests.Response:
        if not SalesforceRESTAPI.access_token:
            raise RuntimeError("ValueError: Token not set. Please authenticate first.")
        url = f"{SalesforceRESTAPI.instance_url}{endpoint}"
        response = requests.delete(url, headers=SalesforceRESTAPI.headers)
        SalesforceRESTAPI.last_http_status = response.status_code
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"DELETE {url} failed: {e} - {response.text}")
            raise
        return response
    
    def execute_apex(self, apex_code: str) -> dict:
        """
        Execute an Apex script using the Salesforce Tooling API's executeAnonymous endpoint.
        Returns the parsed JSON response with execution results.
        Example: run_apex_script('System.debug("Hello World");')
        """
        if not SalesforceRESTAPI.access_token:
            raise RuntimeError("ValueError: Token not set. Please authenticate first.")
        endpoint = "/services/data/v64.0/tooling/executeAnonymous/"
        url = f"{SalesforceRESTAPI.instance_url}{endpoint}"
        params = {"anonymousBody": apex_code}
        response = requests.get(url, headers=SalesforceRESTAPI.headers, params=params)
        try:
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to execute Apex script: {e} - {getattr(response, 'text', '')}")
            return {}

    def revoke(self):
        """
        Clear authentication state (instance_url, access_token, headers) at the class level.
        Use this to de-authenticate the API client.
        """
        SalesforceRESTAPI.instance_url = None
        SalesforceRESTAPI.access_token = None
        SalesforceRESTAPI.headers = None