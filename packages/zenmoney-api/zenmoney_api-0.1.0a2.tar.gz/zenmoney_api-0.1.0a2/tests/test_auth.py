"""Unit tests for the auth module."""

from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from zenmoney_api.auth import AsyncZenMoneyOAuth2Client, ZenMoneyOAuth2Client


class TestAsyncZenMoneyOAuth2Client:
    """Test AsyncZenMoneyOAuth2Client."""

    def test_init(self) -> None:
        """Test client initialization."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        assert client.client_id == "test_client_id"
        assert client.client_secret == "test_client_secret"
        assert client.redirect_uri == "http://localhost/callback"
        assert client.token_endpoint_auth_method == "client_secret_basic"

    def test_authorization_url(self) -> None:
        """Test authorization URL generation."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        auth_url = client.authorization_url()
        assert "api.zenmoney.ru/oauth2/authorize/" in auth_url
        assert "response_type=code" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "redirect_uri=" in auth_url

    def test_authorization_url_with_custom_params(self) -> None:
        """Test authorization URL generation with custom parameters."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        auth_url = client.authorization_url(
            response_type="code",
            scope="read",
            state="custom_state",
        )
        assert "api.zenmoney.ru/oauth2/authorize/" in auth_url
        assert "response_type=code" in auth_url
        assert "scope=read" in auth_url
        assert "state=custom_state" in auth_url

    @pytest.mark.asyncio
    async def test_fetch_token_with_code(
        self, mocker: MockerFixture, sample_token: dict[str, object]
    ) -> None:
        """Test token fetching with authorization code."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Mock the HTTP request at the AsyncOAuth2Client level
        mock_fetch = mocker.patch.object(
            client.__class__.__bases__[1], "fetch_token", new_callable=AsyncMock
        )
        mock_fetch.return_value = sample_token

        # Test the method
        token = await client.fetch_token(code="test_auth_code")

        # Verify the method was called correctly
        mock_fetch.assert_called_once()
        assert token == sample_token

    @pytest.mark.asyncio
    async def test_refresh_access_token(
        self, mocker: MockerFixture, sample_token: dict[str, object]
    ) -> None:
        """Test token refresh."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Mock the HTTP request at the AsyncOAuth2Client level
        mock_refresh = mocker.patch.object(
            client.__class__.__bases__[1], "refresh_token", new_callable=AsyncMock
        )
        mock_refresh.return_value = sample_token

        # Test the method
        token = await client.refresh_token(refresh_token="test_refresh_token")

        # Verify the method was called correctly
        mock_refresh.assert_called_once()
        assert token == sample_token


class TestZenMoneyOAuth2Client:
    """Test ZenMoneyOAuth2Client."""

    def test_init(self) -> None:
        """Test client initialization."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        assert client.client_id == "test_client_id"
        assert client.client_secret == "test_client_secret"
        assert client.redirect_uri == "http://localhost/callback"
        assert client.token_endpoint_auth_method == "client_secret_basic"

    def test_authorization_url(self) -> None:
        """Test authorization URL generation."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        auth_url = client.authorization_url()
        assert "api.zenmoney.ru/oauth2/authorize/" in auth_url
        assert "response_type=code" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "redirect_uri=" in auth_url

    def test_fetch_token_with_code(
        self, mocker: MockerFixture, sample_token: dict[str, object]
    ) -> None:
        """Test token fetching with authorization code."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Mock the HTTP request at the OAuth2Client level
        mock_fetch = mocker.patch.object(client.__class__.__bases__[1], "fetch_token")
        mock_fetch.return_value = sample_token

        # Test the method
        token = client.fetch_token(code="test_auth_code")

        # Verify the method was called correctly
        mock_fetch.assert_called_once()
        assert isinstance(token, dict)

    def test_refresh_access_token(
        self, mocker: MockerFixture, sample_token: dict[str, object]
    ) -> None:
        """Test token refresh."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Mock the HTTP request at the OAuth2Client level
        mock_refresh = mocker.patch.object(
            client.__class__.__bases__[1], "refresh_token"
        )
        mock_refresh.return_value = sample_token

        # Test the method
        token = client.refresh_token(refresh_token="test_refresh_token")

        # Verify the method was called correctly
        mock_refresh.assert_called_once()
        assert isinstance(token, dict)
