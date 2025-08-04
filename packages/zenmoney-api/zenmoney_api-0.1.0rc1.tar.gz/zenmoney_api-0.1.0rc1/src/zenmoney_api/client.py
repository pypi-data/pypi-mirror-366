from __future__ import annotations

from datetime import datetime
from typing import Any, Self, cast

from authlib.oauth2.rfc6749 import OAuth2Token

from zenmoney_api.auth import AsyncZenMoneyOAuth2Client, ZenMoneyOAuth2Client
from zenmoney_api.models import DiffObject

__all__ = ["AsyncZenMoneyClient"]
_BASE_URL = "https://api.zenmoney.ru/v8"


class AsyncZenMoneyClient:
    def __init__(self, auth_client: AsyncZenMoneyOAuth2Client) -> None:
        self._client = auth_client

    @classmethod
    def create_with_token(
        cls,
        client_id: str,
        client_secret: str,
        *,
        redirect_uri: str | None = None,
        token: OAuth2Token | None = None,
        **extra: Any,
    ) -> Self:
        """
        Create a ZenMoney client with an existing token

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            redirect_uri: OAuth2 redirect URI
            token: Existing OAuth2 token (optional)
            **extra: Additional arguments for OAuth2 client

        Returns:
            ZenMoneyClient instance
        """
        auth_client = AsyncZenMoneyOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            **extra,
        )

        if token:
            auth_client.token = token

        return cls(auth_client)

    async def get_diff(self, payload: DiffObject | None = None) -> dict[str, object]:
        if payload is None:
            payload = DiffObject.model_construct(
                server_timestamp=0,
                current_client_timestamp=int(datetime.now().timestamp()),
            )
        response = await self._client.post(
            f"{_BASE_URL}/diff/", json=payload.model_dump(by_alias=True)
        )
        response.raise_for_status()
        return cast(dict[str, object], response.json())

    async def suggest(
        self, transaction: dict[str, object] | list[dict[str, object]]
    ) -> dict[str, object] | list[dict[str, object]]:
        """
        Get suggestions for transaction categorization and payee

        Args:
            transaction: Single transaction or list of transactions

        Returns:
            Suggested transaction(s) with filled fields
        """
        response = await self._client.post(f"{_BASE_URL}/suggest/", json=transaction)
        response.raise_for_status()
        return cast(dict[str, object] | list[dict[str, object]], response.json())


class ZenMoneyClient:
    def __init__(self, auth_client: ZenMoneyOAuth2Client) -> None:
        self._client = auth_client

    @classmethod
    def create_with_token(
        cls,
        client_id: str,
        client_secret: str,
        *,
        redirect_uri: str | None = None,
        token: OAuth2Token | None = None,
        **extra: Any,
    ) -> Self:
        """
        Create a ZenMoney client with an existing token

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            redirect_uri: OAuth2 redirect URI
            token: Existing OAuth2 token (optional)
            **extra: Additional arguments for OAuth2 client

        Returns:
            ZenMoneyClient instance
        """
        auth_client = ZenMoneyOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            **extra,
        )

        if token:
            auth_client.token = token

        return cls(auth_client)

    def get_diff(self, payload: DiffObject | None = None) -> dict[str, object]:
        if payload is None:
            payload = DiffObject.model_construct(
                server_timestamp=0,
                current_client_timestamp=int(datetime.now().timestamp()),
            )
        response = self._client.post(
            f"{_BASE_URL}/diff/", json=payload.model_dump(by_alias=True)
        )
        response.raise_for_status()
        return cast(dict[str, object], response.json())

    def suggest(
        self, transaction: dict[str, object] | list[dict[str, object]]
    ) -> dict[str, object] | list[dict[str, object]]:
        """
        Get suggestions for transaction categorization and payee

        Args:
            transaction: Single transaction or list of transactions

        Returns:
            Suggested transaction(s) with filled fields
        """
        response = self._client.post(f"{_BASE_URL}/suggest/", json=transaction)
        response.raise_for_status()
        return cast(dict[str, object] | list[dict[str, object]], response.json())
