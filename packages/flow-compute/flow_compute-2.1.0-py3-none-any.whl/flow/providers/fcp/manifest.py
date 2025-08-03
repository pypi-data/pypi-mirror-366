"""FCP Provider Manifest.

This module defines the complete specification for how the Flow SDK CLI
should interact with the FCP provider, eliminating hardcoded logic.
"""

from flow.providers.base import (
    CLIConfig,
    ConfigField,
    ConnectionMethod,
    EnvVarSpec,
    PricingModel,
    ProviderCapabilities,
    ProviderManifest,
    ValidationRules,
)
from .core.constants import DEFAULT_REGION, VALID_REGIONS

FCP_MANIFEST = ProviderManifest(
    name="fcp",
    display_name="Flow Compute Platform",
    capabilities=ProviderCapabilities(
        supports_spot_instances=True,
        supports_on_demand=False,
        supports_multi_node=True,
        supports_attached_storage=True,
        requires_ssh_keys=True,
        pricing_model=PricingModel.MARKET,
        supported_regions=VALID_REGIONS,
    ),
    cli_config=CLIConfig(
        env_vars=[
            EnvVarSpec(
                name="FCP_API_KEY",
                required=True,
                description="API key for authentication",
                validation_pattern=r"^fkey_[A-Za-z0-9]{20,}$",
                sensitive=True,
            ),
            EnvVarSpec(
                name="FCP_PROJECT",
                required=False,
                default="default",
                description="Default project name",
            ),
            EnvVarSpec(
                name="FCP_REGION",
                required=False,
                default=DEFAULT_REGION,
                description="Default region for instances",
            ),
            EnvVarSpec(
                name="FCP_API_URL",
                required=False,
                default="https://api.mlfoundry.com",
                description="API endpoint URL",
            ),
        ],
        mount_patterns={
            r"^s3://.*": "/data",
            r"^volume://.*": "/mnt",
            r"^gs://.*": "/gcs",
            r"^https?://.*": "/downloads",
        },
        connection_method=ConnectionMethod(
            type="ssh",
            command_template="ssh -p {port} {user}@{host}",
            supports_interactive=True,
            supports_exec=True,
        ),
        config_fields=[
            ConfigField(
                name="api_key",
                type="string",
                required=True,
                description="FCP API key",
                validation_pattern=r"^fkey_[A-Za-z0-9]{20,}$",
                env_var="FCP_API_KEY",
            ),
            ConfigField(
                name="project",
                type="string",
                required=True,
                default="default",
                description="FCP project name",
                env_var="FCP_PROJECT",
            ),
            ConfigField(
                name="region",
                type="string",
                required=False,
                default=DEFAULT_REGION,
                description="Default region",
                env_var="FCP_REGION",
            ),
        ],
        default_region=DEFAULT_REGION,
    ),
    validation=ValidationRules(
        api_key_pattern=r"^fkey_[A-Za-z0-9]{20,}$",
        region_pattern=r"^[a-z]+-[a-z]+\d+-[a-z]$",
        instance_name_pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$",
        project_name_pattern=r"^[a-z][a-z0-9-]{2,28}[a-z0-9]$",
    ),
)

# Export at module level
__all__ = ["FCP_MANIFEST"]
