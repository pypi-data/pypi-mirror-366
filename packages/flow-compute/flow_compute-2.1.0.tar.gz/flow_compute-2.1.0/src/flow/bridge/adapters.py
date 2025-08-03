"""Registry of available bridge adapters."""

from typing import Dict, Type

from .base import BridgeAdapter
from .config import ConfigBridge
from .fcp_api import FCPAPIBridge
from .formatter import FormatterBridge
from .http import HTTPBridge

# Registry of all available adapters
ADAPTERS: Dict[str, Type[BridgeAdapter]] = {
    "config": ConfigBridge,
    "http": HTTPBridge,
    "fcp": FCPAPIBridge,
    "formatter": FormatterBridge,
}

__all__ = ["ADAPTERS", "BridgeAdapter"]
