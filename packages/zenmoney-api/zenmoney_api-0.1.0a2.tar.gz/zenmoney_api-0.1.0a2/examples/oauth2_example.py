#!/usr/bin/env python3
"""
Example demonstrating OAuth2 authentication flow for ZenMoney API.

This example shows how to:
1. Create an authorization URL
2. Exchange authorization code for access token
3. Use the API with the obtained token
4. Handle token refresh

Note: This is a demonstration. In a real application, you would:
- Handle the callback in a web server
- Store tokens securely
- Implement proper error handling
"""

import asyncio
import os

from zenmoney_api.auth import AsyncZenMoneyOAuth2Client
from zenmoney_api.client import ZenMoneyClient


async def demonstrate_oauth2_flow() -> None:
    """
    Demonstrate the complete OAuth2 flow for ZenMoney API.
    """
    client_id = os.getenv("ZENMONEY_CLIENT_ID", "your_client_id")
    client_secret = os.getenv("ZENMONEY_CLIENT_SECRET", "your_client_secret")
    redirect_uri = os.getenv("ZENMONEY_REDIRECT_URI", "http://localhost:8080/callback")

    print("=== ZenMoney OAuth2 Flow Demonstration ===\n")

    print("Step 1: Creating authorization URL...")
    auth_client = AsyncZenMoneyOAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )

    auth_url = auth_client.authorization_url()
    print(f"Authorization URL: {auth_url}")
    print("Please visit this URL in your browser to authorize the application.\n")

    print("Step 2: Simulating authorization code exchange...")
    print("In a real application, you would receive the authorization code")
    print("from your web server callback handler.\n")

    authorization_code = input(
        "Enter the authorization code from the callback: "
    ).strip()

    if not authorization_code:
        print("No authorization code provided. Exiting.")
        return

    try:
        token = await auth_client.fetch_token(code=authorization_code)
        print("Successfully obtained access token!")

        access_token = str(token.get("access_token", ""))
        refresh_token = str(token.get("refresh_token", ""))
        expires_in_raw = token.get("expires_in", 0)
        expires_in = (
            int(expires_in_raw)
            if expires_in_raw and isinstance(expires_in_raw, int | str)
            else 0
        )

        print(f"Access Token: {access_token[:20] if access_token else 'None'}...")
        print(f"Refresh Token: {refresh_token[:20] if refresh_token else 'None'}...")
        print(f"Expires In: {expires_in} seconds")
        print()

        print("Step 3: Using the API with the access token...")
        api_client = ZenMoneyClient(auth_client)

        print("Fetching data from ZenMoney API...")
        diff_data = await api_client.get_diff()
        print("Successfully retrieved data!")
        server_timestamp = str(diff_data.get("serverTimestamp", "N/A"))
        current_timestamp = str(diff_data.get("currentClientTimestamp", "N/A"))
        print(f"Server timestamp: {server_timestamp}")
        print(f"Current client timestamp: {current_timestamp}")
        print()

        print("Testing suggest endpoint...")
        suggestion = await api_client.suggest({"payee": "McDonalds"})
        print(f"Suggestion received: {suggestion}")
        print()

        print("Step 4: Demonstrating token refresh...")
        if refresh_token and refresh_token != "None":
            new_token = await auth_client.refresh_token()
            print("Successfully refreshed access token!")
            new_access_token = str(new_token.get("access_token", ""))
            print(
                f"New Access Token: {new_access_token[:20] if new_access_token else 'None'}..."
            )
        else:
            print("No refresh token available for demonstration.")

    except Exception as e:
        print(f"Error during OAuth2 flow: {e}")
        print("This might be due to:")
        print("- Invalid client credentials")
        print("- Invalid authorization code")
        print("- Network issues")
        print("- API server issues")


def main() -> None:
    """
    Main function to run the OAuth2 demonstration.
    """
    print("ZenMoney API OAuth2 Demonstration")
    print("==================================")
    print()

    client_id = os.getenv("ZENMONEY_CLIENT_ID")
    client_secret = os.getenv("ZENMONEY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Warning: ZENMONEY_CLIENT_ID or ZENMONEY_CLIENT_SECRET")
        print(" environment variables are not set. Using placeholder values.")
        print(" Set these variables to test with real credentials.\n")

    asyncio.run(demonstrate_oauth2_flow())


if __name__ == "__main__":
    main()
