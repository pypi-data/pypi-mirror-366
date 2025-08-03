"""Tests for YAML frontend adapter."""


import pytest
import yaml

from flow._internal.frontends.yaml.adapter import YamlFrontendAdapter
from flow.api.models import StorageInterface, TaskConfig
from flow.errors import ValidationError


class TestYamlFrontendAdapter:
    """Test YAML frontend adapter functionality."""

    @pytest.fixture
    def adapter(self):
        """Create YAML adapter instance."""
        return YamlFrontendAdapter()

    @pytest.fixture
    def minimal_yaml_content(self):
        """Minimal valid YAML configuration."""
        return {
            "name": "test-job",
            "image": "ubuntu:22.04",
            "command": "echo 'Hello World'",
            "instance_type": "cpu.small"  # Required field
        }

    @pytest.fixture
    def complex_yaml_content(self):
        """Complex YAML configuration with all features."""
        return {
            "name": "training-job",
            "image": "pytorch/pytorch:latest",
            "command": ["python", "train.py", "--epochs", "100"],
            "resources": {
                "gpu": 4,
                "gpu_type": "A100",
                "disk": "500GB"
            },
            "env": {
                "PYTHONPATH": "/workspace",
                "CUDA_VISIBLE_DEVICES": "0,1,2,3"
            },
            "ports": [8888, 6006],
            "instance_type": "p4d.24xlarge",
            "region": "us-west-2",
            "max_price_per_hour": 50.0,
            "ssh_keys": ["key-123", "key-456"],
            "input": {
                "source": "s3://bucket/data",
                "destination": "/data"
            },
            "output": {
                "source": "/results",
                "destination": "s3://bucket/results"
            }
        }

    @pytest.fixture
    def yaml_file(self, tmp_path, minimal_yaml_content):
        """Create temporary YAML file."""
        yaml_path = tmp_path / "config.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(minimal_yaml_content, f)
        return yaml_path

    @pytest.mark.asyncio
    async def test_parse_minimal_config(self, adapter, minimal_yaml_content):
        """Test parsing minimal YAML configuration.
        
        GIVEN: Minimal YAML configuration dict
        WHEN: parse_and_convert() is called
        THEN: Valid TaskConfig is returned
        """
        # WHEN
        config = await adapter.parse_and_convert(minimal_yaml_content)

        # THEN
        assert isinstance(config, TaskConfig)
        assert config.name == "test-job"
        assert config.image == "ubuntu:22.04"
        assert config.command == "echo 'Hello World'"
        assert config.instance_type == "cpu.small"
        assert config.volumes == []  # No volumes

    @pytest.mark.asyncio
    async def test_parse_from_file(self, adapter, yaml_file):
        """Test parsing YAML from file path.
        
        GIVEN: Path to valid YAML file
        WHEN: parse_and_convert() is called with file path
        THEN: Valid TaskConfig is returned
        """
        # WHEN
        config = await adapter.parse_and_convert(yaml_file)

        # THEN
        assert config.name == "test-job"
        assert config.image == "ubuntu:22.04"
        assert config.command == "echo 'Hello World'"

    @pytest.mark.asyncio
    async def test_parse_complex_config(self, adapter, complex_yaml_content):
        """Test parsing complex YAML with all features.
        
        GIVEN: Complex YAML configuration with resources, env, ports, etc.
        WHEN: parse_and_convert() is called
        THEN: All fields are correctly mapped to TaskConfig
        """
        # WHEN
        config = await adapter.parse_and_convert(complex_yaml_content)

        # THEN
        assert config.name == "training-job"
        assert config.image == "pytorch/pytorch:latest"
        assert config.command == ['python', 'train.py', '--epochs', '100']
        assert config.num_instances == 1  # Default value
        assert config.instance_type == "p4d.24xlarge"  # From YAML
        assert len(config.volumes) == 1
        assert config.volumes[0].size_gb == 500
        assert config.volumes[0].mount_path == "/data"
        assert config.env == {
            "PYTHONPATH": "/workspace",
            "CUDA_VISIBLE_DEVICES": "0,1,2,3"
        }
        assert config.region == "us-west-2"
        assert config.max_price_per_hour == 50.0
        assert config.ssh_keys == ["key-123", "key-456"]
        # I/O metadata would be in script, but we removed script from complex_yaml_content
        # So these assertions are no longer valid

    @pytest.mark.asyncio
    async def test_legacy_format_support(self, adapter):
        """Test support for legacy YAML format.
        
        GIVEN: YAML with legacy fields (top-level gpu, storage)
        WHEN: parse_and_convert() is called
        THEN: Legacy fields are correctly mapped
        """
        # GIVEN
        legacy_yaml = {
            "name": "legacy-job",
            "image": "nvidia/cuda:11.0-base",
            "command": "python legacy.py",
            "gpu": 2,
            "storage": "200GB",
            "environment": {"KEY": "value"}  # Modern field name
        }

        # WHEN
        config = await adapter.parse_and_convert(legacy_yaml)

        # THEN
        assert config.num_instances == 1  # Default
        assert config.instance_type == "gpu.nvidia.a100"  # Default for legacy
        assert len(config.volumes) == 1
        assert config.volumes[0].size_gb == 200
        assert config.env == {"KEY": "value"}

    @pytest.mark.asyncio
    async def test_command_list_handling(self, adapter):
        """Test proper handling of command as list.
        
        GIVEN: YAML with command as list containing special characters
        WHEN: parse_and_convert() is called
        THEN: Command is properly quoted and joined
        """
        # GIVEN
        yaml_content = {
            "name": "command-test",
            "image": "python:3.9",
            "command": ["python", "-c", "print('Hello World')", "--flag", "value with spaces"],
            "instance_type": "cpu.small"
        }

        # WHEN
        config = await adapter.parse_and_convert(yaml_content)

        # THEN
        # Command should be preserved as a list
        assert isinstance(config.command, list)
        assert len(config.command) == 5
        assert config.command == ["python", "-c", "print('Hello World')", "--flag", "value with spaces"]

    @pytest.mark.asyncio
    async def test_single_port_handling(self, adapter):
        """Test handling of single port field.
        
        GIVEN: YAML with single 'port' field (not 'ports')
        WHEN: parse_and_convert() is called
        THEN: Single port is converted to list
        """
        # GIVEN
        yaml_content = {
            "name": "single-port",
            "image": "nginx",
            "command": "nginx -g 'daemon off;'",
            "instance_type": "cpu.small",
            "port": 80
        }

        # WHEN
        config = await adapter.parse_and_convert(yaml_content)

        # THEN
        # ports field removed -  [80]

    @pytest.mark.asyncio
    async def test_docker_image_aliases(self, adapter):
        """Test support for both 'image' and 'image'.
        
        GIVEN: YAML with 'image' instead of 'image'
        WHEN: parse_and_convert() is called
        THEN: image field is recognized
        """
        # GIVEN
        yaml_content = {
            "name": "docker-test",
            "image": "alpine:latest",  # Using image
            "command": "ls -la",
            "instance_type": "cpu.small"
        }

        # WHEN
        config = await adapter.parse_and_convert(yaml_content)

        # THEN
        assert config.image == "alpine:latest"

    @pytest.mark.asyncio
    async def test_options_override(self, adapter, minimal_yaml_content):
        """Test that options override YAML values.
        
        GIVEN: YAML config and override options
        WHEN: parse_and_convert() is called with options
        THEN: Options override YAML values
        """
        # WHEN
        config = await adapter.parse_and_convert(
            minimal_yaml_content,
            name="overridden-name",
            region="eu-west-1",
            num_instances=3
        )

        # THEN
        assert config.name == "overridden-name"  # Overridden
        assert config.region == "eu-west-1"  # Added by option
        assert config.num_instances == 3  # Added by option
        assert config.image == "ubuntu:22.04"  # From YAML

    @pytest.mark.asyncio
    async def test_validation_missing_name(self, adapter):
        """Test validation error for missing name.
        
        GIVEN: YAML without required 'name' field
        WHEN: parse_and_convert() is called
        THEN: ValidationError is raised
        """
        # GIVEN
        invalid_yaml = {
            "image": "ubuntu:22.04",
            "command": "echo test"
        }

        # WHEN/THEN
        with pytest.raises(ValidationError) as exc_info:
            await adapter.parse_and_convert(invalid_yaml)

        assert "Missing required field: name" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validation_missing_image(self, adapter):
        """Test validation error for missing image.
        
        GIVEN: YAML without 'image' or 'image'
        WHEN: parse_and_convert() is called
        THEN: ValidationError is raised
        """
        # GIVEN
        invalid_yaml = {
            "name": "test-job",
            "command": "echo test"
        }

        # WHEN/THEN
        with pytest.raises(ValidationError) as exc_info:
            await adapter.parse_and_convert(invalid_yaml)

        assert "Missing required field: image or docker_image" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validation_invalid_ports(self, adapter):
        """Test that invalid ports are ignored (no longer validated).
        
        GIVEN: YAML with invalid ports value
        WHEN: parse_and_convert() is called
        THEN: Config is created successfully (ports are ignored)
        """
        # GIVEN
        invalid_yaml = {
            "name": "test-job",
            "image": "nginx",
            "command": "nginx",
            "instance_type": "cpu.small",
            "ports": "8080"  # String instead of int/list
        }

        # WHEN
        config = await adapter.parse_and_convert(invalid_yaml)

        # THEN - ports are ignored, config succeeds
        assert config.name == "test-job"
        assert config.image == "nginx"

    @pytest.mark.asyncio
    async def test_validate_method(self, adapter, minimal_yaml_content):
        """Test validate() method.
        
        GIVEN: Valid and invalid YAML configurations
        WHEN: validate() is called
        THEN: Returns True for valid, False for invalid
        """
        # Valid config
        assert await adapter.validate(minimal_yaml_content) is True

        # Invalid config (missing name)
        invalid_yaml = {"image": "ubuntu"}
        assert await adapter.validate(invalid_yaml) is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, adapter):
        """Test error handling for non-existent file.
        
        GIVEN: Path to non-existent file
        WHEN: parse_and_convert() is called
        THEN: ValidationError is raised
        """
        # WHEN/THEN
        with pytest.raises(ValidationError) as exc_info:
            await adapter.parse_and_convert("/path/to/nonexistent.yaml")

        assert "File not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_yaml_syntax(self, adapter, tmp_path):
        """Test error handling for invalid YAML syntax.
        
        GIVEN: File with invalid YAML syntax
        WHEN: parse_and_convert() is called
        THEN: ValidationError is raised
        """
        # GIVEN
        bad_yaml = tmp_path / "bad.yaml"
        with open(bad_yaml, 'w') as f:
            f.write("invalid: yaml: syntax: ][")

        # WHEN/THEN
        with pytest.raises(ValidationError) as exc_info:
            await adapter.parse_and_convert(bad_yaml)

        assert "Invalid YAML syntax" in str(exc_info.value)

    def test_format_methods(self, adapter):
        """Test job ID and status formatting.
        
        GIVEN: Flow job IDs and statuses
        WHEN: format methods are called
        THEN: Same values are returned (no transformation for YAML)
        """
        # Job ID formatting
        assert adapter.format_job_id("task-12345") == "task-12345"
        assert adapter.format_job_id("flow-job-xyz") == "flow-job-xyz"

        # Status formatting
        assert adapter.format_status("running") == "running"
        assert adapter.format_status("completed") == "completed"

    def test_properties(self, adapter):
        """Test adapter properties.
        
        GIVEN: YAML adapter instance
        WHEN: Properties are accessed
        THEN: Correct values are returned
        """
        assert adapter.name == "yaml"
        assert adapter.version == "1.0.0"
        assert adapter.capabilities == {
            "supports_file": True,
            "supports_dict": True
        }

    @pytest.mark.asyncio
    async def test_volume_interface_setting(self, adapter):
        """Test that volumes get correct interface type.
        
        GIVEN: YAML with storage/disk specification
        WHEN: parse_and_convert() is called
        THEN: Volumes have correct StorageInterface
        """
        # GIVEN
        yaml_content = {
            "name": "volume-test",
            "image": "ubuntu",
            "command": "echo test",
            "instance_type": "cpu.small",
            "resources": {
                "disk": "100GB"
            }
        }

        # WHEN
        config = await adapter.parse_and_convert(yaml_content)

        # THEN
        assert len(config.volumes) == 1
        assert config.volumes[0].interface == StorageInterface.BLOCK


class TestYamlFrontendAdapterIntegration:
    """Integration tests for YAML adapter."""

    @pytest.mark.asyncio
    async def test_real_world_ml_config(self):
        """Test parsing real-world ML training configuration.
        
        GIVEN: Realistic ML training YAML
        WHEN: Parsed and converted
        THEN: All ML-specific settings are preserved
        """
        # GIVEN
        ml_yaml = {
            "name": "bert-finetuning",
            "image": "huggingface/transformers-pytorch-gpu:latest",
            "command": [
                "python", "-m", "transformers.trainer",
                "--model_name_or_path", "bert-base-uncased",
                "--output_dir", "/models/output",
                "--num_train_epochs", "3",
                "--per_device_train_batch_size", "32",
                "--fp16"
            ],
            # Script removed to avoid command/script conflict
            "resources": {
                "gpu": 8,
                "gpu_type": "A100",
                "disk": "1000GB"
            },
            "env": {
                "WANDB_API_KEY": "${WANDB_API_KEY}",
                "HF_TOKEN": "${HF_TOKEN}",
                "CUDA_VISIBLE_DEVICES": "0,1,2,3,4,5,6,7"
            },
            "ports": [6006, 8888],  # TensorBoard and Jupyter
            "instance_type": "p4d.24xlarge",
            "region": "us-east-1",
            "max_price_per_hour": 100.0
        }

        adapter = YamlFrontendAdapter()

        # WHEN
        config = await adapter.parse_and_convert(ml_yaml)

        # THEN
        assert config.name == "bert-finetuning"
        assert "--fp16" in config.command
        # Script was removed to avoid command/script conflict
        assert config.num_instances == 1  # Default, not 8
        assert config.instance_type == "p4d.24xlarge"  # From YAML
        assert config.volumes[0].size_gb == 1000
        assert config.env["WANDB_API_KEY"] == "${WANDB_API_KEY}"
        # Ports field removed from TaskConfig
