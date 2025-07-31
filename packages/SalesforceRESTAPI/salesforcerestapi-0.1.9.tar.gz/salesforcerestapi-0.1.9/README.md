# SalesforceRESTAPI

A simple Python library to interact with the Salesforce REST API using OAuth 2.0 Client Credentials Flow.

## Features
- Authenticate with Salesforce using OAuth 2.0 Client Credentials
- Basic CRUD operations (create, read, update, delete) for Salesforce objects
- SOQL query support
- Apex script execution via Tooling API
- Record verification utilities

## Installation

```bash
pip install SalesforceRESTAPI
```

## Usage

> **Note:** As of version 0.1.3, authentication state (`instance_url`, `access_token`, `headers`) is stored as class variables. You must call `SalesforceRESTAPI.authenticate(...)` before using any instance methods. All instances share the same authentication state.

```python
from SalesforceRESTAPI import SalesforceRESTAPI

# Authenticate (call this once before using any instance methods)
SalesforceRESTAPI.authenticate(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET', login_url='https://login.salesforce.com')

# Now you can use instance methods
sf = SalesforceRESTAPI()

# Create a record
account_id = sf.create_record('Account', Name='Test Account', Industry='Technology')

# Get a record
account = sf.get_record('Account', account_id)

# Update a record
sf.update_record('Account', account_id, Name='Updated Name')

# Delete a record
sf.delete_record('Account', account_id)

# Run a SOQL query
results = sf.queryRecords('SELECT Id, Name FROM Account')

# Execute anonymous Apex
apex_result = sf.execute_apex('System.debug("Hello World");')

# Revoke authentication (clears class-level state)
sf.revoke()
```

## Requirements
- Python 3.6+
- requests
- python-dotenv (for loading .env files in tests)

## License
MIT License. See [LICENSE](LICENSE) for details.
