# ZenMoney API Client

A Python client for the ZenMoney API with proper OAuth2 authentication support.

## Installation

```bash
pip install zenmoney-api
```

## Usage

### OAuth2 Authentication

The client supports OAuth2 authentication as described in the [ZenMoney API documentation](https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API).

#### Step 1: Create Authorization URL

```python
import asyncio
from zenmoney_api.auth import AsyncZenMoneyOAuth2Client

async def get_authorization_url():
    # Create OAuth2 client
    client = AsyncZenMoneyOAuth2Client(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="http://your-app.com/callback"
    )

    # Generate authorization URL
    auth_url = client.authorization_url()
    print(f"Authorization URL: {auth_url}")

    return client

# Run the function
client = asyncio.run(get_authorization_url())
```

#### Step 2: Exchange Authorization Code for Token

```python
import asyncio
from zenmoney_api.auth import AsyncZenMoneyOAuth2Client

async def exchange_code_for_token():
    # Use the client from step 1
    client = AsyncZenMoneyOAuth2Client(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="http://your-app.com/callback"
    )

    # Exchange authorization code for access token
    code = "authorization_code_from_callback"
    token = await client.fetch_token(code=code)

    print(f"Access Token: {token['access_token']}")
    print(f"Refresh Token: {token['refresh_token']}")

    return token

# Run the function
token = asyncio.run(exchange_code_for_token())
```

#### Step 3: Use the API with Token

```python
import asyncio
from zenmoney_api.client import ZenMoneyClient

async def use_api():
    # Create client with existing token
    client = ZenMoneyClient.create_with_token(
        client_id="your_client_id",
        client_secret="your_client_secret",
        token=token  # from step 2
    )

    # Get data from ZenMoney API
    diff_data = await client.get_diff()
    print(f"Diff data: {diff_data}")

    # Get suggestions for transaction
    suggestion = await client.suggest({"payee": "McDonalds"})
    print(f"Suggestion: {suggestion}")

# Run the function
asyncio.run(use_api())
```

### Complete Example

Here's a complete example showing the full OAuth2 flow:

```python
import asyncio
from zenmoney_api.auth import AsyncZenMoneyOAuth2Client
from zenmoney_api.client import ZenMoneyClient

async def complete_oauth2_flow():
    # Step 1: Create OAuth2 client
    auth_client = AsyncZenMoneyOAuth2Client(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="http://your-app.com/callback"
    )

    # Generate authorization URL
    auth_url = auth_client.authorization_url()
    print(f"Please visit: {auth_url}")

    # Step 2: After user authorizes, you'll get the code in your callback
    # This is just an example - in real app, you'd get this from your web server
    code = "authorization_code_from_callback"

    # Exchange code for token
    token = await auth_client.fetch_token(code=code)

    # Step 3: Create API client with token
    api_client = ZenMoneyClient(auth_client)

    # Use the API
    diff_data = await api_client.get_diff()
    print(f"Diff data: {diff_data}")

    # Get suggestions
    suggestion = await api_client.suggest({"payee": "McDonalds"})
    print(f"Suggestion: {suggestion}")

# Run the complete flow
asyncio.run(complete_oauth2_flow())
```

### Token Refresh

The client automatically handles token refresh when needed. You can also manually refresh a token:

```python
import asyncio
from zenmoney_api.auth import AsyncZenMoneyOAuth2Client

async def refresh_token():
    client = AsyncZenMoneyOAuth2Client(
        client_id="your_client_id",
        client_secret="your_client_secret"
    )

    # Refresh token
    new_token = await client.refresh_token()
    print(f"New access token: {new_token['access_token']}")

# Run the function
asyncio.run(refresh_token())
```

## API Endpoints

### Diff Endpoint

Synchronize data with ZenMoney:

```python
# Get all data
diff_data = await client.get_diff()

# Send local changes
local_changes = {
    "currentClientTimestamp": 1234567890,
    "transaction": [
        {
            "id": "transaction-uuid",
            "changed": 1234567890,
            "user": 1,
            "income": 1000,
            "outcome": 0,
            # ... other transaction fields
        }
    ]
}
diff_response = await client.get_diff(local_changes)
```

### Suggest Endpoint

Get suggestions for transaction categorization:

```python
# Single transaction
suggestion = await client.suggest({
    "payee": "McDonalds"
})

# Multiple transactions
suggestions = await client.suggest([
    {"payee": "McDonalds"},
    {"payee": "Starbucks"}
])
```

## Data Models

The library includes Pydantic models for all ZenMoney entities:

- `Instrument` - Currency information
- `Company` - Bank or payment organization
- `User` - User information
- `Account` - User accounts
- `Tag` - Transaction categories
- `Merchant` - Payees
- `Reminder` - Scheduled transactions
- `ReminderMarker` - Reminder instances
- `Transaction` - Financial transactions
- `Budget` - Budget information

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/zenmoney-api.git
cd zenmoney-api

# Install dependencies
uv sync --all-groups
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/zenmoney_api

# Run ruff linting
uv run ruff check src/

# Run pylint linting
uv run pylint src/

# Run type checking
uv run mypy src/
```

Also you can run all them just by running pre-commit tool:
```bash
uv run pre-commit --all-files
```

You can install pre-commit hooks to run on every commit:
```bash
uv run pre-commit install
```

## License

MIT License - see LICENSE file for details.
