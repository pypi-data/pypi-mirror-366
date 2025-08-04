import importlib.metadata as importlib_metadata

from .auth import AsyncZenMoneyOAuth2Client, ZenMoneyOAuth2Client
from .client import AsyncZenMoneyClient

try:
    __version__ = importlib_metadata.version("zenmoney-api")
except ImportError:
    __version__ = "unknown"

__all__ = [
    "__version__",
    "AsyncZenMoneyOAuth2Client",
    "ZenMoneyOAuth2Client",
    "AsyncZenMoneyClient",
]
