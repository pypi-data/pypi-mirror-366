"""Unit tests for the client module."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from authlib.oauth2.rfc6749 import OAuth2Token

from zenmoney_api.auth import AsyncZenMoneyOAuth2Client, ZenMoneyOAuth2Client
from zenmoney_api.client import AsyncZenMoneyClient, ZenMoneyClient
from zenmoney_api.models import DiffObject, Transaction


class TestZenMoneyClient:
    """Test AsyncZenMoneyClient."""

    def test_init(self) -> None:
        """Test client initialization."""
        auth_client = AsyncZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )
        client = AsyncZenMoneyClient(auth_client)

        assert client._client == auth_client

    def test_create_with_token(self, sample_token: dict[str, object]) -> None:
        """Test creating client with existing token."""
        token = OAuth2Token(sample_token)

        client = AsyncZenMoneyClient.create_with_token(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
            token=token,
        )

        assert isinstance(client, AsyncZenMoneyClient)
        assert isinstance(client._client, AsyncZenMoneyOAuth2Client)
        assert client._client.client_id == "test_client_id"
        assert client._client.client_secret == "test_client_secret"
        assert client._client.redirect_uri == "http://localhost/callback"
        assert client._client.token == sample_token

    def test_create_with_token_without_token(self) -> None:
        """Test creating client without token."""
        client = AsyncZenMoneyClient.create_with_token(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        assert isinstance(client, AsyncZenMoneyClient)
        assert isinstance(client._client, AsyncZenMoneyOAuth2Client)
        assert client._client.client_id == "test_client_id"
        assert client._client.client_secret == "test_client_secret"
        assert client._client.redirect_uri == "http://localhost/callback"
        assert client._client.token is None

    @pytest.mark.asyncio
    async def test_get_diff_empty_payload(
        self,
        sample_diff_response: dict[str, object],
        _freeze_time_fixture: None,
    ) -> None:
        """Test get_diff with empty payload."""
        now = datetime.now()
        # Create mock auth client
        mock_auth_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_diff_response
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = AsyncZenMoneyClient(mock_auth_client)
        result = await client.get_diff()

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/diff/",
            json={
                "serverTimestamp": 0,
                "currentClientTimestamp": int(now.timestamp()),
                "instrument": None,
                "company": None,
                "user": None,
                "account": None,
                "tag": None,
                "merchant": None,
                "reminder": None,
                "reminderMarker": None,
                "transaction": None,
                "budget": None,
                "deletion": None,
            },
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == sample_diff_response

    @pytest.mark.asyncio
    async def test_get_diff_with_payload(
        self, sample_diff_response: dict[str, object]
    ) -> None:
        """Test get_diff with payload."""
        # Create mock auth client
        mock_auth_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_diff_response
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = AsyncZenMoneyClient(mock_auth_client)

        payload = DiffObject.model_construct(
            current_client_timestamp=int(datetime.now().timestamp()),
            server_timestamp=0,
            transaction=[
                Transaction.model_construct(
                    id_="test-transaction-id",
                    changed=datetime.now(),
                    user=1,
                    income=1000,
                    outcome=0,
                    created=datetime.now(),
                    income_instrument=1,
                    income_account="1",
                    outcome_instrument=1,
                    outcome_account="1",
                    date=datetime.now().isoformat(),
                    comment="test-comment",
                    payee="test-payee",
                    original_payee="test-original-payee",
                ),
            ],
        )

        result = await client.get_diff(payload)

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/diff/",
            json=payload.model_dump(by_alias=True),
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == sample_diff_response

    @pytest.mark.asyncio
    async def test_get_diff_with_none_payload(
        self, sample_diff_response: dict[str, object], _freeze_time_fixture: None
    ) -> None:
        """Test get_diff with None payload."""
        # Create mock auth client
        mock_auth_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_diff_response
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = AsyncZenMoneyClient(mock_auth_client)

        result = await client.get_diff(None)

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/diff/",
            json={
                "serverTimestamp": 0,
                "currentClientTimestamp": int(datetime.now().timestamp()),
                "instrument": None,
                "company": None,
                "user": None,
                "account": None,
                "tag": None,
                "merchant": None,
                "reminder": None,
                "reminderMarker": None,
                "transaction": None,
                "budget": None,
                "deletion": None,
            },
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == sample_diff_response

    @pytest.mark.asyncio
    async def test_suggest_single_transaction(
        self, sample_suggest_response: dict[str, object]
    ) -> None:
        """Test suggest with single transaction."""
        # Create mock auth client
        mock_auth_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_suggest_response
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = AsyncZenMoneyClient(mock_auth_client)

        transaction: dict[str, object] = {"payee": "McDonalds"}

        result = await client.suggest(transaction)

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/suggest/",
            json=transaction,
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == sample_suggest_response

    @pytest.mark.asyncio
    async def test_suggest_multiple_transactions(
        self, sample_suggest_response: dict[str, object]
    ) -> None:
        """Test suggest with multiple transactions."""
        # Create mock auth client
        mock_auth_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [
            sample_suggest_response,
            sample_suggest_response,
        ]
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = AsyncZenMoneyClient(mock_auth_client)

        transactions: list[dict[str, object]] = [
            {"payee": "McDonalds"},
            {"payee": "Starbucks"},
        ]

        result = await client.suggest(transactions)

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/suggest/",
            json=transactions,
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == [sample_suggest_response, sample_suggest_response]

    @pytest.mark.asyncio
    async def test_get_diff_http_error(self) -> None:
        """Test get_diff with HTTP error."""
        # Create mock auth client
        mock_auth_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_auth_client.post.return_value = mock_response

        client = AsyncZenMoneyClient(mock_auth_client)

        with pytest.raises(Exception, match="HTTP Error"):
            await client.get_diff()

    @pytest.mark.asyncio
    async def test_suggest_http_error(self) -> None:
        """Test suggest with HTTP error."""
        # Create mock auth client
        mock_auth_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_auth_client.post.return_value = mock_response

        client = AsyncZenMoneyClient(mock_auth_client)

        transaction: dict[str, object] = {"payee": "McDonalds"}

        with pytest.raises(Exception, match="HTTP Error"):
            await client.suggest(transaction)


class TestSyncZenMoneyClient:
    """Test ZenMoneyClient."""

    def test_init(self) -> None:
        """Test client initialization."""
        auth_client = ZenMoneyOAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )
        client = ZenMoneyClient(auth_client)

        assert client._client == auth_client

    def test_create_with_token(self, sample_token: dict[str, object]) -> None:
        """Test creating client with existing token."""
        token = OAuth2Token(sample_token)

        client = ZenMoneyClient.create_with_token(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
            token=token,
        )

        assert isinstance(client, ZenMoneyClient)
        assert isinstance(client._client, ZenMoneyOAuth2Client)
        assert client._client.client_id == "test_client_id"
        assert client._client.client_secret == "test_client_secret"
        assert client._client.redirect_uri == "http://localhost/callback"
        assert client._client.token == sample_token

    def test_create_with_token_without_token(self) -> None:
        """Test creating client without token."""
        client = ZenMoneyClient.create_with_token(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback",
        )

        assert isinstance(client, ZenMoneyClient)
        assert isinstance(client._client, ZenMoneyOAuth2Client)
        assert client._client.client_id == "test_client_id"
        assert client._client.client_secret == "test_client_secret"
        assert client._client.redirect_uri == "http://localhost/callback"
        assert client._client.token is None

    def test_get_diff_empty_payload(
        self,
        sample_diff_response: dict[str, object],
        _freeze_time_fixture: None,
    ) -> None:
        """Test get_diff with empty payload."""
        now = datetime.now()
        # Create mock auth client
        mock_auth_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_diff_response
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = ZenMoneyClient(mock_auth_client)
        result = client.get_diff()

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/diff/",
            json={
                "serverTimestamp": 0,
                "currentClientTimestamp": int(now.timestamp()),
                "instrument": None,
                "company": None,
                "user": None,
                "account": None,
                "tag": None,
                "merchant": None,
                "reminder": None,
                "reminderMarker": None,
                "transaction": None,
                "budget": None,
                "deletion": None,
            },
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == sample_diff_response

    def test_get_diff_with_payload(
        self, sample_diff_response: dict[str, object]
    ) -> None:
        """Test get_diff with payload."""
        # Create mock auth client
        mock_auth_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_diff_response
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = ZenMoneyClient(mock_auth_client)

        payload = DiffObject.model_construct(
            current_client_timestamp=int(datetime.now().timestamp()),
            server_timestamp=0,
            transaction=[
                Transaction.model_construct(
                    id_="test-transaction-id",
                    changed=datetime.now(),
                    user=1,
                    income=1000,
                    outcome=0,
                    created=datetime.now(),
                    income_instrument=1,
                    income_account="1",
                    outcome_instrument=1,
                    outcome_account="1",
                    date=datetime.now().isoformat(),
                    comment="test-comment",
                    payee="test-payee",
                    original_payee="test-original-payee",
                ),
            ],
        )

        result = client.get_diff(payload)

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/diff/",
            json=payload.model_dump(by_alias=True),
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == sample_diff_response

    def test_get_diff_with_none_payload(
        self, sample_diff_response: dict[str, object], _freeze_time_fixture: None
    ) -> None:
        """Test get_diff with None payload."""
        # Create mock auth client
        mock_auth_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_diff_response
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = ZenMoneyClient(mock_auth_client)

        result = client.get_diff(None)

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/diff/",
            json={
                "serverTimestamp": 0,
                "currentClientTimestamp": int(datetime.now().timestamp()),
                "instrument": None,
                "company": None,
                "user": None,
                "account": None,
                "tag": None,
                "merchant": None,
                "reminder": None,
                "reminderMarker": None,
                "transaction": None,
                "budget": None,
                "deletion": None,
            },
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == sample_diff_response

    def test_suggest_single_transaction(
        self, sample_suggest_response: dict[str, object]
    ) -> None:
        """Test suggest with single transaction."""
        # Create mock auth client
        mock_auth_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = sample_suggest_response
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = ZenMoneyClient(mock_auth_client)

        transaction: dict[str, object] = {"payee": "McDonalds"}

        result = client.suggest(transaction)

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/suggest/",
            json=transaction,
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == sample_suggest_response

    def test_suggest_multiple_transactions(
        self, sample_suggest_response: dict[str, object]
    ) -> None:
        """Test suggest with multiple transactions."""
        # Create mock auth client
        mock_auth_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [
            sample_suggest_response,
            sample_suggest_response,
        ]
        mock_response.raise_for_status.return_value = None
        mock_auth_client.post.return_value = mock_response

        client = ZenMoneyClient(mock_auth_client)

        transactions: list[dict[str, object]] = [
            {"payee": "McDonalds"},
            {"payee": "Starbucks"},
        ]

        result = client.suggest(transactions)

        # Verify the request was made correctly
        mock_auth_client.post.assert_called_once_with(
            "https://api.zenmoney.ru/v8/suggest/",
            json=transactions,
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        # Verify the result
        assert result == [sample_suggest_response, sample_suggest_response]

    def test_get_diff_http_error(self) -> None:
        """Test get_diff with HTTP error."""
        # Create mock auth client
        mock_auth_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_auth_client.post.return_value = mock_response

        client = ZenMoneyClient(mock_auth_client)

        with pytest.raises(Exception, match="HTTP Error"):
            client.get_diff()

    def test_suggest_http_error(self) -> None:
        """Test suggest with HTTP error."""
        # Create mock auth client
        mock_auth_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_auth_client.post.return_value = mock_response

        client = ZenMoneyClient(mock_auth_client)

        transaction: dict[str, object] = {"payee": "McDonalds"}

        with pytest.raises(Exception, match="HTTP Error"):
            client.suggest(transaction)
