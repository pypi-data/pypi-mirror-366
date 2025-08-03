"""FCP Provider implementation.

The FCP (Foundry Cloud Platform) provider implements compute and storage
operations using the FCP API. It supports market-based resource allocation
through auctions.
"""

from flow.providers.registry import ProviderRegistry

from .manifest import FCP_MANIFEST
from .provider import FCPProvider

# Import from the direct module, not the setup subpackage
try:
    from .setup import FCPProviderSetup
except ImportError:
    # Fallback if setup module causes issues
    FCPProviderSetup = None

# Self-register with the provider registry
ProviderRegistry.register("fcp", FCPProvider)

__all__ = ["FCPProvider", "FCPProviderSetup", "FCP_MANIFEST"]
