"""FCP domain adaptation layer.

This package provides adapters between FCP and Flow domains:
- Model conversion between FCP and Flow models
- Storage interface mapping
- Mount specification adaptation
"""

from .models import FCPAdapter
from .mounts import FCPMountAdapter
from .storage import FCPStorageMapper

__all__ = [
    # Models adapter
    "FCPAdapter",
    # Mounts adapter
    "FCPMountAdapter",
    # Storage adapter
    "FCPStorageMapper",
]
