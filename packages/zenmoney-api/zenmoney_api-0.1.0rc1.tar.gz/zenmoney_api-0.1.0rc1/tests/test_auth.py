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

    def test_authorization_url_state_management(self) -> None:
        """Test that authorization_url properly sets the _state attribute."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Initial state should not be a string (it's ClientState.UNOPENED)
        assert not isinstance(client._state, str)

        # Call authorization_url
        client.authorization_url()

        # State should be set to a string after calling authorization_url
        assert client._state is not None
        assert isinstance(client._state, str)  # type: ignore[unreachable]
        assert len(client._state) > 0

    def test_authorization_url_with_custom_response_type(self) -> None:
        """Test authorization URL with custom response_type."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        auth_url = client.authorization_url(response_type="token")
        assert "response_type=token" in auth_url

    def test_authorization_url_with_multiple_params(self) -> None:
        """Test authorization URL with multiple custom parameters."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        auth_url = client.authorization_url(
            response_type="code",
            scope="read write",
            state="test_state_123",
            prompt="consent",
        )
        assert "response_type=code" in auth_url
        assert "scope=read+write" in auth_url or "scope=read%20write" in auth_url
        assert "state=test_state_123" in auth_url
        assert "prompt=consent" in auth_url

    def test_authorization_url_mocked_create_authorization_url(
        self, mocker: MockerFixture
    ) -> None:
        """Test authorization_url with mocked create_authorization_url method."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Mock the create_authorization_url method
        mock_create_url = mocker.patch.object(client, "create_authorization_url")
        mock_create_url.return_value = ("https://test.url", "test_state_123")

        # Call authorization_url
        result = client.authorization_url(response_type="code", scope="read")

        # Verify create_authorization_url was called with correct parameters
        mock_create_url.assert_called_once_with(
            "https://api.zenmoney.ru/oauth2/authorize/",
            response_type="code",
            scope="read",
        )

        # Verify the result
        assert result == "https://test.url"

        # Verify state was set
        assert client._state == "test_state_123"

    def test_authorization_url_preserves_existing_state(self) -> None:
        """Test that authorization_url preserves existing state if provided."""
        client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Set initial state
        client._state = "existing_state"

        # Call authorization_url with custom state
        client.authorization_url(state="new_state")

        # State should be updated to the new state
        assert client._state == "new_state"

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

    def test_authorization_url_with_custom_params(self) -> None:
        """Test authorization URL generation with custom parameters."""
        client = ZenMoneyOAuth2Client(
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

    def test_authorization_url_state_management(self) -> None:
        """Test that authorization_url properly sets the _state attribute."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Initial state should not be a string (it's ClientState.UNOPENED)
        assert not isinstance(client._state, str)

        # Call authorization_url
        client.authorization_url()

        # State should be set to a string after calling authorization_url
        assert client._state is not None
        assert isinstance(client._state, str)  # type: ignore[unreachable]
        assert len(client._state) > 0

    def test_authorization_url_with_custom_response_type(self) -> None:
        """Test authorization URL with custom response_type."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        auth_url = client.authorization_url(response_type="token")
        assert "response_type=token" in auth_url

    def test_authorization_url_with_multiple_params(self) -> None:
        """Test authorization URL with multiple custom parameters."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        auth_url = client.authorization_url(
            response_type="code",
            scope="read write",
            state="test_state_123",
            prompt="consent",
        )
        assert "response_type=code" in auth_url
        assert "scope=read+write" in auth_url or "scope=read%20write" in auth_url
        assert "state=test_state_123" in auth_url
        assert "prompt=consent" in auth_url

    def test_authorization_url_mocked_create_authorization_url(
        self, mocker: MockerFixture
    ) -> None:
        """Test authorization_url with mocked create_authorization_url method."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Mock the create_authorization_url method
        mock_create_url = mocker.patch.object(client, "create_authorization_url")
        mock_create_url.return_value = ("https://test.url", "test_state_123")

        # Call authorization_url
        result = client.authorization_url(response_type="code", scope="read")

        # Verify create_authorization_url was called with correct parameters
        mock_create_url.assert_called_once_with(
            "https://api.zenmoney.ru/oauth2/authorize/",
            response_type="code",
            scope="read",
        )

        # Verify the result
        assert result == "https://test.url"

        # Verify state was set
        assert client._state == "test_state_123"

    def test_authorization_url_preserves_existing_state(self) -> None:
        """Test that authorization_url preserves existing state if provided."""
        client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        # Set initial state
        client._state = "existing_state"

        # Call authorization_url with custom state
        client.authorization_url(state="new_state")

        # State should be updated to the new state
        assert client._state == "new_state"

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
