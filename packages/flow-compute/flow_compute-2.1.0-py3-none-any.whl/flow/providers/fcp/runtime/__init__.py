"""FCP runtime configuration and scripts.

This package handles runtime aspects:
- Startup script generation
- Quota awareness and management
"""

from .startup.builder import FCPStartupScriptBuilder

__all__ = [
    # Startup script builder
    "FCPStartupScriptBuilder",
]
