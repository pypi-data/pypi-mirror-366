"""Production configuration for FCP provider."""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class FCPScriptSizeConfig:
    """Configuration for script size handling in FCP provider."""

    # Size limits
    max_script_size: int = 10_000
    safety_margin: int = 1_000

    # Feature flags
    enable_compression: bool = True
    enable_split_storage: bool = True
    enable_metrics: bool = True
    enable_health_checks: bool = True

    # Storage backend
    storage_backend: str = "local"  # "local" or "s3"
    storage_config: Optional[Dict[str, Any]] = None

    # Operational settings
    compression_level: int = 9
    max_retries: int = 3
    request_timeout_seconds: int = 30

    # Monitoring
    enable_detailed_logging: bool = False
    metrics_endpoint: Optional[str] = None

    @classmethod
    def from_env(cls) -> "FCPScriptSizeConfig":
        """Create configuration from environment variables."""
        return cls(
            # Size limits
            max_script_size=int(os.getenv("FCP_MAX_SCRIPT_SIZE", "10000")),
            safety_margin=int(os.getenv("FCP_SCRIPT_SAFETY_MARGIN", "1000")),
            # Feature flags
            enable_compression=os.getenv("FCP_ENABLE_COMPRESSION", "true").lower() == "true",
            enable_split_storage=os.getenv("FCP_ENABLE_SPLIT_STORAGE", "true").lower() == "true",
            enable_metrics=os.getenv("FCP_ENABLE_METRICS", "true").lower() == "true",
            enable_health_checks=os.getenv("FCP_ENABLE_HEALTH_CHECKS", "true").lower() == "true",
            # Storage backend
            storage_backend=os.getenv("FCP_STORAGE_BACKEND", "local"),
            # Operational settings
            compression_level=int(os.getenv("FCP_COMPRESSION_LEVEL", "9")),
            max_retries=int(os.getenv("FCP_MAX_RETRIES", "3")),
            request_timeout_seconds=int(os.getenv("FCP_REQUEST_TIMEOUT", "30")),
            # Monitoring
            enable_detailed_logging=os.getenv("FCP_DETAILED_LOGGING", "false").lower() == "true",
            metrics_endpoint=os.getenv("FCP_METRICS_ENDPOINT"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for passing to handlers."""
        return {
            "max_script_size": self.max_script_size,
            "safety_margin": self.safety_margin,
            "enable_compression": self.enable_compression,
            "enable_split": self.enable_split_storage,
            "compression_level": self.compression_level,
            "max_compression_attempts": 1,
            "enable_metrics": self.enable_metrics,
            "enable_detailed_logging": self.enable_detailed_logging,
        }


@dataclass
class FCPProviderConfig:
    """Complete configuration for FCP provider."""

    # Core settings
    api_url: str = "https://api.mlfoundry.com"
    project: Optional[str] = None
    region: Optional[str] = None

    # Script size handling
    script_size: FCPScriptSizeConfig = None

    # Operational settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    connection_pool_size: int = 50

    # Development settings
    debug_mode: bool = False
    dry_run: bool = False

    def __post_init__(self):
        if self.script_size is None:
            self.script_size = FCPScriptSizeConfig.from_env()

    @classmethod
    def from_env(cls) -> "FCPProviderConfig":
        """Create complete configuration from environment."""
        return cls(
            api_url=os.getenv("FCP_API_URL", "https://api.mlfoundry.com"),
            project=os.getenv("FCP_PROJECT"),
            region=os.getenv("FCP_REGION"),
            script_size=FCPScriptSizeConfig.from_env(),
            enable_caching=os.getenv("FCP_ENABLE_CACHING", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("FCP_CACHE_TTL", "300")),
            connection_pool_size=int(os.getenv("FCP_CONNECTION_POOL_SIZE", "50")),
            debug_mode=os.getenv("FCP_DEBUG", "false").lower() == "true",
            dry_run=os.getenv("FCP_DRY_RUN", "false").lower() == "true",
        )

    def validate(self):
        """Validate configuration."""
        if self.script_size.max_script_size <= 0:
            raise ValueError("max_script_size must be positive")

        if self.script_size.compression_level not in range(1, 10):
            raise ValueError("compression_level must be between 1 and 9")

        if self.cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds must be non-negative")

        if self.connection_pool_size <= 0:
            raise ValueError("connection_pool_size must be positive")


def get_fcp_config() -> FCPProviderConfig:
    """Get validated FCP configuration from environment."""
    config = FCPProviderConfig.from_env()
    config.validate()
    return config
