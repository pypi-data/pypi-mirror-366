from __future__ import annotations

from typing import Any, Protocol, TypedDict

from authlib.integrations.httpx_client import AsyncOAuth2Client, OAuth2Client


class TokenRequestParams(TypedDict):
    client_id: str | None
    client_secret: str | None
    redirect_uri: str | None


__all__ = [
    "AsyncZenMoneyOAuth2Client",
    "ZenMoneyOAuth2Client",
]


class _AuthClientProtocol(Protocol):
    client_id: str | None
    client_secret: str | None
    redirect_uri: str | None

    _state: str | None
    _AUTHORIZE_ENDPOINT: str

    def create_authorization_url(self, url: str, **params: Any) -> tuple[str, str]: ...


class _ZenMoneyOAuth2Mixin:
    _BASE = "https://api.zenmoney.ru/oauth2"
    _AUTHORIZE_ENDPOINT: str = f"{_BASE}/authorize/"
    _TOKEN_ENDPOINT: str = f"{_BASE}/token/"

    _state: str | None = None

    def authorization_url(
        self: _AuthClientProtocol, *, response_type: str = "code", **params: str
    ) -> str:
        url, state = self.create_authorization_url(
            self._AUTHORIZE_ENDPOINT, response_type=response_type, **params
        )
        self._state = state
        return url


class AsyncZenMoneyOAuth2Client(_ZenMoneyOAuth2Mixin, AsyncOAuth2Client):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        redirect_uri: str | None = None,
        **extra: Any,
    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            # Use client_secret_basic as per ZenMoney API documentation
            token_endpoint_auth_method="client_secret_basic",
            token_endpoint=self._TOKEN_ENDPOINT,
            grant_type="authorization_code",
            **extra,
        )


class ZenMoneyOAuth2Client(_ZenMoneyOAuth2Mixin, OAuth2Client):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        redirect_uri: str | None = None,
        **extra: Any,
    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            # Use client_secret_basic as per ZenMoney API documentation
            token_endpoint_auth_method="client_secret_basic",
            token_endpoint=self._TOKEN_ENDPOINT,
            grant_type="authorization_code",
            **extra,
        )
