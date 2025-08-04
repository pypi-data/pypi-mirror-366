"""Pytest configuration and fixtures for zenmoney-api tests."""

from collections.abc import Generator
from datetime import datetime

import pytest
from freezegun import freeze_time


@pytest.fixture
def _freeze_time_fixture() -> Generator[None, None, None]:
    with freeze_time("2025-01-01 12:00:00"):
        yield


@pytest.fixture
def sample_token() -> dict[str, object]:
    """Sample OAuth2 token for testing."""
    return {
        "access_token": "test_access_token_12345",
        "refresh_token": "test_refresh_token_67890",
        "expires_in": 86400,
        "token_type": "bearer",
    }


@pytest.fixture
def sample_diff_response(_freeze_time_fixture: None) -> dict[str, object]:
    """Sample diff response from ZenMoney API."""
    return {
        "serverTimestamp": int(datetime.now().timestamp()),
        "currentClientTimestamp": int(datetime.now().timestamp()),
        "instrument": [
            {
                "id": 1,
                "changed": int(datetime.now().timestamp()),
                "title": "Рубль",
                "shortTitle": "RUB",
                "symbol": "₽",
                "rate": 1.0,
            }
        ],
        "company": [
            {
                "id": 1,
                "changed": int(datetime.now().timestamp()),
                "title": "Сбербанк",
                "fullTitle": "ПАО Сбербанк",
                "www": "https://www.sberbank.ru",
                "country": "Россия",
            }
        ],
        "user": [
            {
                "id": 1,
                "changed": int(datetime.now().timestamp()),
                "login": "test_user",
                "currency": 1,
                "parent": None,
            }
        ],
        "account": [],
        "tag": [],
        "merchant": [],
        "reminder": [],
        "reminderMarker": [],
        "transaction": [],
        "budget": [],
        "deletion": [],
    }


@pytest.fixture
def sample_suggest_response() -> dict[str, object]:
    """Sample suggest response from ZenMoney API."""
    return {
        "payee": "МакДональдс",
        "merchant": "7BF5E890-2E2B-42FD-842A-B70B56620755",
        "tag": ["1B11D636-5250-4DDA-8157-3810A0319EC2"],
    }
