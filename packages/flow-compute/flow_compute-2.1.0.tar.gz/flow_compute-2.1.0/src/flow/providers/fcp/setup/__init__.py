"""FCP provider setup module."""

# Only import the adapter to avoid circular imports
from .adapter import FCPSetupAdapter

__all__ = ["FCPSetupAdapter"]
