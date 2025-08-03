# Provider Manifest Guide

This guide explains how to use and create provider manifests in the Flow SDK.

## Overview

The Provider Manifest system allows each provider to declare its integration requirements as data, eliminating hardcoded provider-specific logic from the CLI. This makes the Flow SDK truly provider-agnostic.

## Architecture

### Core Components

1. **ProviderManifest**: Complete specification for a provider
2. **ProviderResolver**: Runtime resolver that loads and queries manifests
3. **CLI Integration**: Commands use resolver instead of hardcoded logic

### Key Benefits

- **No hardcoding**: All provider knowledge is data-driven
- **Type safety**: Pydantic models validate everything
- **Extensibility**: New providers just add a manifest
- **Discoverability**: Manifests are self-documenting

## Creating a Provider Manifest

### 1. Define the Manifest

Create a `manifest.py` file in your provider package:

```python
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

MY_MANIFEST = ProviderManifest(
    name="myprovider",
    display_name="My Cloud Provider",
    
    capabilities=ProviderCapabilities(
        supports_spot_instances=True,
        pricing_model=PricingModel.MARKET,
        supported_regions=["region-1", "region-2"],
        # ... other capabilities
    ),
    
    cli_config=CLIConfig(
        env_vars=[
            EnvVarSpec(
                name="MY_API_KEY",
                required=True,
                description="API key for authentication",
                validation_pattern=r"^key_[A-Za-z0-9]+$",
                sensitive=True
            ),
        ],
        
        mount_patterns={
            r"^s3://.*": "/data",
            r"^gs://.*": "/gcs",
        },
        
        connection_method=ConnectionMethod(
            type="ssh",
            command_template="ssh -p {port} {user}@{host}",
        ),
        
        config_fields=[
            ConfigField(
                name="api_key",
                type="string",
                required=True,
                description="API key",
                validation_pattern=r"^key_[A-Za-z0-9]+$",
                env_var="MY_API_KEY"
            ),
        ],
        
        default_region="region-1"
    ),
    
    validation=ValidationRules(
        api_key_pattern=r"^key_[A-Za-z0-9]+$",
        region_pattern=r"^region-\d+$",
    )
)
```

### 2. Export the Manifest

In your provider's `__init__.py`:

```python
from .manifest import MY_MANIFEST

__all__ = ["MyProvider", "MY_MANIFEST"]
```

### 3. Use in CLI Commands

The CLI automatically uses your manifest for:

#### Mount Resolution
```python
# User runs: flow run job.yaml --mount s3://bucket/data
# CLI resolves using your mount_patterns: /data
```

#### Validation
```python
# User runs: flow init --provider myprovider --api-key invalid
# CLI validates using your validation rules
```

#### Connection Commands
```python
# User runs: flow ssh task-123
# CLI generates: ssh -p 22 ubuntu@host.example.com
```

## Manifest Components

### ProviderCapabilities

Describes what your provider supports:

```python
capabilities=ProviderCapabilities(
    supports_spot_instances=True,      # Spot/preemptible instances
    supports_on_demand=False,          # Reserved instances
    supports_multi_node=True,          # Multi-node tasks
    supports_attached_storage=True,    # Volume attachment
    requires_ssh_keys=True,            # SSH key requirement
    pricing_model=PricingModel.MARKET, # MARKET, FIXED, or HYBRID
    supported_regions=["us-1", "eu-1"],
    max_instances_per_task=100,
)
```

### CLIConfig

Defines CLI integration points:

```python
cli_config=CLIConfig(
    # Environment variables
    env_vars=[
        EnvVarSpec(
            name="PROVIDER_API_KEY",
            required=True,
            default=None,
            description="API authentication key",
            validation_pattern=r"^[A-Za-z0-9_]+$",
            sensitive=True  # Mask in output
        ),
    ],
    
    # Mount path resolution
    mount_patterns={
        r"^s3://.*": "/data",      # S3 buckets → /data
        r"^volume://.*": "/mnt",   # Volumes → /mnt
        r"^https?://.*": "/downloads",
    },
    
    # Connection method
    connection_method=ConnectionMethod(
        type="ssh",  # ssh, docker, kubectl, web
        command_template="ssh -p {port} {user}@{host}",
        supports_interactive=True,
        supports_exec=True
    ),
    
    # Configuration fields
    config_fields=[
        ConfigField(
            name="project",
            type="string",
            required=True,
            default="default",
            description="Project name",
            env_var="PROVIDER_PROJECT"
        ),
    ],
    
    default_region="us-1"
)
```

### ValidationRules

Provider-specific validation patterns:

```python
validation=ValidationRules(
    api_key_pattern=r"^key_[A-Za-z0-9]{20,}$",
    region_pattern=r"^[a-z]+-[0-9]+$",
    instance_name_pattern=r"^[a-z0-9-]+$",
    project_name_pattern=r"^[a-z][a-z0-9-]{2,28}[a-z0-9]$"
)
```

## Using the Provider Resolver

### In CLI Commands

```python
from flow.cli.provider_resolver import ProviderResolver

# Resolve mount paths
target = ProviderResolver.resolve_mount_path("myprovider", "s3://bucket/data")
# Returns: "/data"

# Validate configuration
valid = ProviderResolver.validate_config_value("myprovider", "api_key", "key_abc123")
# Returns: True/False

# Get connection command
cmd = ProviderResolver.get_connection_command("myprovider", task)
# Returns: "ssh -p 22 ubuntu@1.2.3.4"

# Get environment variables
env_vars = ProviderResolver.get_env_vars("myprovider")
# Returns: {"api_key": "MY_API_KEY", "project": "MY_PROJECT"}
```

### In Tests

```python
def test_provider_manifest():
    manifest = ProviderResolver.get_manifest("myprovider")
    
    # Test capabilities
    assert manifest.capabilities.supports_spot_instances
    
    # Test mount patterns
    assert manifest.cli_config.mount_patterns[r"^s3://.*"] == "/data"
    
    # Test validation
    assert manifest.validation.api_key_pattern
```

## Examples

### FCP Provider Manifest

See `src/flow/providers/fcp/manifest.py` for a complete example:

- Environment variables: FCP_API_KEY, FCP_PROJECT, FCP_REGION
- Mount patterns: s3://, volume://, gs://, https://
- SSH connection with configurable port
- Validation for API keys, regions, and project names

### Local Provider Manifest

See `src/flow/providers/local/manifest.py` for a development provider:

- Docker-based execution
- Local path mounting
- No API key requirements
- Docker exec for connections

## Migration Guide

### For Provider Authors

1. Create a manifest.py in your provider package
2. Define your ProviderManifest with all requirements
3. Export it in __init__.py
4. Remove hardcoded logic from CLI integration

### For CLI Command Authors

1. Import ProviderResolver
2. Replace hardcoded logic with resolver calls:
   - Mount patterns → `resolve_mount_path()`
   - Validation → `validate_config_value()`
   - Connections → `get_connection_command()`
3. Remove provider-specific imports

## Best Practices

1. **Complete manifests**: Include all provider requirements
2. **Clear descriptions**: Help users understand each field
3. **Strict validation**: Catch errors early with patterns
4. **Sensible defaults**: Provide good default values
5. **Documentation**: Keep manifests self-documenting

## Troubleshooting

### Manifest not found

```
ProviderError: Provider 'myprovider' not found
```

Ensure your provider is registered and the manifest is exported.

### Validation failures

```
Invalid API key format for provider myprovider
```

Check your validation patterns match actual requirements.

### Mount resolution issues

Verify your mount patterns cover all expected URL formats.

## Future Enhancements

- Manifest versioning for backward compatibility
- Dynamic manifest updates from provider APIs
- Manifest inheritance for provider families
- UI generation from manifest specifications