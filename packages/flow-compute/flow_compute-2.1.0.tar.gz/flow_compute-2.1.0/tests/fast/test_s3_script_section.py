"""Test S3 script section for startup scripts."""

from flow.providers.fcp.runtime.startup.sections import S3Section, ScriptContext


class TestS3Section:
    """Test S3Section for startup script generation."""

    def test_should_include_with_s3_mounts(self):
        """Test S3 section is included when S3 mounts are present."""
        section = S3Section()

        context = ScriptContext(
            environment={
                "S3_MOUNT_0_BUCKET": "test-bucket",
                "S3_MOUNT_0_TARGET": "/data",
                "S3_MOUNTS_COUNT": "1"
            }
        )

        assert section.should_include(context) is True

    def test_should_not_include_without_s3(self):
        """Test S3 section is not included without S3 mounts."""
        section = S3Section()
        context = ScriptContext(environment={})

        assert section.should_include(context) is False

    def test_generate_single_mount(self):
        """Test generating script for single S3 mount."""
        section = S3Section()

        context = ScriptContext(
            environment={
                "AWS_ACCESS_KEY_ID": "test_key",
                "AWS_SECRET_ACCESS_KEY": "test_secret",
                "S3_MOUNT_0_BUCKET": "ml-datasets",
                "S3_MOUNT_0_PATH": "imagenet",
                "S3_MOUNT_0_TARGET": "/datasets",
                "S3_MOUNTS_COUNT": "1"
            }
        )

        script = section.generate(context)

        # Check key components
        assert "Setting up S3 mounts" in script
        assert "apt-get install -y -qq s3fs" in script
        assert "echo \"${AWS_ACCESS_KEY_ID}:${AWS_SECRET_ACCESS_KEY}\"" in script
        assert "s3fs ml-datasets:/imagenet /datasets" in script
        assert "-o passwd_file=/tmp/s3fs_passwd" in script
        assert "-o ro" in script  # readonly
        assert "mountpoint -q /datasets" in script

    def test_generate_multiple_mounts(self):
        """Test generating script for multiple S3 mounts."""
        section = S3Section()

        context = ScriptContext(
            environment={
                "AWS_ACCESS_KEY_ID": "test_key",
                "AWS_SECRET_ACCESS_KEY": "test_secret",
                "S3_MOUNT_0_BUCKET": "datasets",
                "S3_MOUNT_0_PATH": "train",
                "S3_MOUNT_0_TARGET": "/train",
                "S3_MOUNT_1_BUCKET": "models",
                "S3_MOUNT_1_PATH": "",
                "S3_MOUNT_1_TARGET": "/models",
                "S3_MOUNTS_COUNT": "2"
            }
        )

        script = section.generate(context)

        # Check both mounts
        assert "s3fs datasets:/train /train" in script
        assert "s3fs models /models" in script
        assert script.count("mountpoint -q") == 2

    def test_validate_missing_credentials(self):
        """Test validation fails without AWS credentials."""
        section = S3Section()

        context = ScriptContext(
            environment={
                "S3_MOUNT_0_BUCKET": "test",
                "S3_MOUNTS_COUNT": "1"
            }
        )

        errors = section.validate(context)

        assert len(errors) == 2
        assert "AWS_ACCESS_KEY_ID not set" in errors[0]
        assert "AWS_SECRET_ACCESS_KEY not set" in errors[1]

    def test_validate_with_credentials(self):
        """Test validation passes with credentials."""
        section = S3Section()

        context = ScriptContext(
            environment={
                "AWS_ACCESS_KEY_ID": "key",
                "AWS_SECRET_ACCESS_KEY": "secret",
                "S3_MOUNT_0_BUCKET": "test",
                "S3_MOUNTS_COUNT": "1"
            }
        )

        errors = section.validate(context)
        assert len(errors) == 0

    def test_priority(self):
        """Test S3 section priority."""
        section = S3Section()
        assert section.priority == 35  # After volumes, before docker

    def test_name(self):
        """Test S3 section name."""
        section = S3Section()
        assert section.name == "s3_mounts"
