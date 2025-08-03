"""FCP-specific startup script generation.

This module provides backward compatibility while using the new
implementation with better separation of concerns.

Key FCP compatibility features:
- Respects FCP's 10,000 character limit for startup scripts
- Automatically compresses scripts exceeding the limit
- Creates log symlinks at FCP-expected locations
"""

from flow.api.models import TaskConfig

from ...core.constants import STARTUP_SCRIPT_MAX_SIZE
from .builder import FCPStartupScriptBuilder as _NewBuilder


class FCPStartupScriptBuilder:
    """Builds startup scripts for FCP instances.

    This class provides backward compatibility while delegating to
    the new implementation with cleaner architecture.
    """

    # Maximum size before we need to compress
    MAX_UNCOMPRESSED_SIZE = STARTUP_SCRIPT_MAX_SIZE

    def __init__(self):
        """Initialize with new builder implementation."""
        self._builder = _NewBuilder()

    def build(self, config: TaskConfig) -> str:
        """Build a startup script from task configuration.

        Args:
            config: Task configuration

        Returns:
            Complete startup script as a string

        Raises:
            ValueError: If configuration validation fails
        """
        script = self._builder.build(config)

        if not script.is_valid:
            raise ValueError(f"Invalid configuration: {', '.join(script.validation_errors)}")

        return script.content
