"""Test S3 support in Flow SDK."""

import os
from unittest.mock import Mock, patch

import pytest

from flow._internal.data.loaders import AWSCredentialResolver, S3Loader
from flow._internal.data.resolver import DataError
from flow.core.provider_interfaces import IProvider
from tests.conftest import create_mock_config


class TestAWSCredentialResolver:
    """Test AWS credential resolution."""

    def test_env_vars_priority(self):
        """Test environment variables have highest priority."""
        resolver = AWSCredentialResolver()

        with patch.dict(os.environ, {
            "AWS_ACCESS_KEY_ID": "test_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret",
            "AWS_SESSION_TOKEN": "test_token"
        }):
            creds = resolver.get_credentials()
            assert creds == {
                "access_key": "test_key",
                "secret_key": "test_secret",
                "session_token": "test_token"
            }

    def test_credentials_file(self):
        """Test reading from ~/.aws/credentials."""
        resolver = AWSCredentialResolver()

        # Mock home directory and credentials file
        mock_creds_content = """
[default]
aws_access_key_id = file_key
aws_secret_access_key = file_secret
"""

        with patch.dict(os.environ, {}, clear=True):  # Clear env vars
            # Need to patch the method directly on the resolver
            with patch.object(resolver, '_read_credentials_file') as mock_read:
                mock_read.return_value = {
                    "access_key": "file_key",
                    "secret_key": "file_secret",
                    "session_token": None
                }
                creds = resolver.get_credentials()
                assert creds == {
                    "access_key": "file_key",
                    "secret_key": "file_secret",
                    "session_token": None
                }

    def test_no_credentials(self):
        """Test when no credentials are available."""
        resolver = AWSCredentialResolver()

        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.exists', return_value=False):
                with patch.object(resolver, '_is_ec2_instance', return_value=False):
                    creds = resolver.get_credentials()
                    assert creds is None


class TestS3Loader:
    """Test S3Loader functionality."""

    def setup_method(self):
        self.loader = S3Loader()
        self.mock_provider = Mock(spec=IProvider)

        # Mock credential resolver
        self.mock_creds = {
            "access_key": "test_key",
            "secret_key": "test_secret",
            "session_token": None
        }
        self.loader._credential_resolver.get_credentials = Mock(return_value=self.mock_creds)

    def test_valid_s3_url(self):
        """Test resolving valid S3 URL."""
        # Mock the validation method instead of boto3
        self.loader._validate_access = Mock(return_value=True)

        spec = self.loader.resolve("s3://test-bucket/data/train", self.mock_provider)

        assert spec.source == "s3://test-bucket/data/train"
        assert spec.mount_type == "s3fs"
        assert spec.options["bucket"] == "test-bucket"
        assert spec.options["path"] == "data/train"
        assert spec.options["readonly"] is True

    def test_bucket_only_url(self):
        """Test S3 URL with just bucket name."""
        self.loader._validate_access = Mock(return_value=True)

        spec = self.loader.resolve("s3://test-bucket", self.mock_provider)

        assert spec.source == "s3://test-bucket"
        assert spec.options["bucket"] == "test-bucket"
        assert spec.options["path"] == ""

    def test_invalid_s3_url(self):
        """Test error on invalid S3 URL."""
        with pytest.raises(DataError) as exc:
            self.loader.resolve("s3://", self.mock_provider)

        assert "Invalid S3 URL: missing bucket name" in str(exc.value)
        assert "Use format: s3://bucket/path" in exc.value.suggestions

    def test_no_credentials(self):
        """Test error when no AWS credentials available."""
        self.loader._credential_resolver.get_credentials = Mock(return_value=None)

        with pytest.raises(DataError) as exc:
            self.loader.resolve("s3://test-bucket/data", self.mock_provider)

        assert "Cannot access S3 bucket: test-bucket" in str(exc.value)
        assert "Check AWS credentials are configured" in exc.value.suggestions

    def test_bucket_not_found(self):
        """Test error when bucket doesn't exist."""
        # Mock the _validate_access method to raise the appropriate error
        from flow._internal.data.resolver import DataError

        def mock_validate(bucket):
            raise DataError(
                f"S3 bucket not found: {bucket}",
                suggestions=[
                    "Check bucket name is correct",
                    "Verify bucket exists in your AWS account",
                    f"Try: aws s3 ls s3://{bucket}"
                ]
            )

        self.loader._validate_access = mock_validate

        with pytest.raises(DataError) as exc:
            self.loader.resolve("s3://nonexistent-bucket", self.mock_provider)

        assert "S3 bucket not found: nonexistent-bucket" in str(exc.value)
        assert "Check bucket name is correct" in exc.value.suggestions

    def test_access_denied(self):
        """Test error when access is denied."""
        def mock_validate(bucket):
            raise DataError(
                f"Access denied to S3 bucket: {bucket}",
                suggestions=[
                    "Check IAM permissions for your AWS user",
                    "Verify bucket policy allows your access",
                    f"Try: aws s3 ls s3://{bucket}"
                ]
            )

        self.loader._validate_access = mock_validate

        with pytest.raises(DataError) as exc:
            self.loader.resolve("s3://private-bucket", self.mock_provider)

        assert "Access denied to S3 bucket: private-bucket" in str(exc.value)
        assert "Check IAM permissions" in exc.value.suggestions[0]

    def test_boto3_not_installed(self):
        """Test error when boto3 is not installed."""
        # Mock validation to raise the boto3 error
        def mock_validate(bucket):
            raise DataError(
                "boto3 is required for S3 support",
                suggestions=["Install with: pip install boto3"]
            )

        self.loader._validate_access = mock_validate

        with pytest.raises(DataError) as exc:
            self.loader.resolve("s3://test-bucket", self.mock_provider)

        assert "boto3 is required for S3 support" in str(exc.value)
        assert "Install with: pip install boto3" in exc.value.suggestions


class TestS3Integration:
    """Test S3 integration with Flow.submit()."""

    @pytest.mark.skip(reason="S3 data parameter removed - use data_mounts with MountSpec instead")
    def test_submit_with_s3_data(self):
        """Test submitting job with S3 data."""
        from flow import Flow
        from flow.api.models import Task, TaskConfig, TaskStatus

        # Create flow with mock config
        mock_config = create_mock_config(auth_token="test_key", project="test_project", api_url="https://api.test.com")

        flow = Flow(config=mock_config)
        mock_provider = Mock()
        flow._provider = mock_provider

        # Mock catalog
        from flow.api.models import AvailableInstance
        mock_provider.find_instances.return_value = [
            AvailableInstance(
                allocation_id="alloc_123",
                instance_type="a100.80gb.sxm4.1x",
                region="us-east-1",
                price_per_hour=5.0,
                gpu_count=1,
                status="available"
            )
        ]

        # Mock task submission
        mock_task = Task(
            task_id="task_123",
            name="test-task",
            status=TaskStatus.PENDING,
            created_at=1234567890,
            instance_type="a100.80gb.sxm4.1x",
            num_instances=1,
            region="us-east-1",
            cost_per_hour="$5.00",
            _provider=mock_provider
        )
        mock_provider.submit_task.return_value = mock_task
        mock_provider.prepare_task_config.side_effect = lambda x: x

        # Mock S3 validation
        with patch('flow.data.loaders.S3Loader._validate_access', return_value=True):

            # Set AWS credentials
            with patch.dict(os.environ, {
                "AWS_ACCESS_KEY_ID": "test_key",
                "AWS_SECRET_ACCESS_KEY": "test_secret"
            }):
                config = TaskConfig(
                    name="test-task",
                    instance_type="a100.80gb.sxm4.1x",
                    command="python train.py",
                    data="s3://ml-datasets/imagenet"
                )
                task = flow.run(config)

                # Check task was submitted
                assert task.task_id == "task_123"

                # Check environment was configured for S3
                submitted_config = mock_provider.submit_task.call_args.kwargs["config"]
                assert submitted_config.env["AWS_ACCESS_KEY_ID"] == "test_key"
                assert submitted_config.env["AWS_SECRET_ACCESS_KEY"] == "test_secret"
                assert submitted_config.env["S3_MOUNT_0_BUCKET"] == "ml-datasets"
                assert submitted_config.env["S3_MOUNT_0_PATH"] == "imagenet"
                assert submitted_config.env["S3_MOUNT_0_TARGET"] == "/data"
                assert submitted_config.env["S3_MOUNTS_COUNT"] == "1"

    @pytest.mark.skip(reason="S3 data parameter removed - use data_mounts with MountSpec instead")
    def test_submit_with_multiple_s3_sources(self):
        """Test submitting with multiple S3 sources."""
        from flow import Flow
        from flow.api.models import Task, TaskConfig, TaskStatus

        mock_config = create_mock_config(auth_token="test_key", project="test_project", api_url="https://api.test.com")

        flow = Flow(config=mock_config)
        mock_provider = Mock()
        flow._provider = mock_provider

        # Mock catalog and task
        from flow.api.models import AvailableInstance
        mock_provider.find_instances.return_value = [
            AvailableInstance(
                allocation_id="alloc_456",
                instance_type="a100.80gb.sxm4.1x",
                region="us-east-1",
                price_per_hour=5.0,
                gpu_count=1,
                status="available"
            )
        ]

        mock_task = Task(
            task_id="task_123",
            name="test-task",
            status=TaskStatus.PENDING,
            created_at=1234567890,
            instance_type="a100.80gb.sxm4.1x",
            num_instances=1,
            region="us-east-1",
            cost_per_hour="$5.00",
            _provider=mock_provider
        )
        mock_provider.submit_task.return_value = mock_task
        mock_provider.prepare_task_config.side_effect = lambda x: x

        # Mock S3 validation
        with patch('flow.data.loaders.S3Loader._validate_access', return_value=True):

            with patch.dict(os.environ, {
                "AWS_ACCESS_KEY_ID": "test_key",
                "AWS_SECRET_ACCESS_KEY": "test_secret"
            }):
                config = TaskConfig(
                    name="test-task",
                    instance_type="a100.80gb.sxm4.1x",
                    command="python train.py",
                    data={
                        "/datasets": "s3://ml-datasets/imagenet",
                        "/models": "s3://ml-models/pretrained"
                    }
                )
                task = flow.run(config)

                submitted_config = mock_provider.submit_task.call_args.kwargs["config"]

                # Check both S3 mounts were configured
                assert submitted_config.env["S3_MOUNT_0_BUCKET"] == "ml-datasets"
                assert submitted_config.env["S3_MOUNT_0_PATH"] == "imagenet"
                assert submitted_config.env["S3_MOUNT_0_TARGET"] == "/datasets"

                assert submitted_config.env["S3_MOUNT_1_BUCKET"] == "ml-models"
                assert submitted_config.env["S3_MOUNT_1_PATH"] == "pretrained"
                assert submitted_config.env["S3_MOUNT_1_TARGET"] == "/models"

                assert submitted_config.env["S3_MOUNTS_COUNT"] == "2"
