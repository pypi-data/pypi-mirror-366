"""Tests for CLI v2 natural language parsing.

Direct tests of parsing functions without base class complications.
"""

import re
from datetime import timedelta

import pytest

from flow.errors import ValidationError


def parse_deadline(time_str: str) -> timedelta:
    """Parse natural language time expressions."""
    time_str = time_str.lower().strip()

    # Simple patterns
    if match := re.match(r'(\d+)\s*hours?', time_str):
        return timedelta(hours=int(match.group(1)))
    elif match := re.match(r'(\d+)\s*minutes?', time_str):
        return timedelta(minutes=int(match.group(1)))
    elif match := re.match(r'(\d+)\s*days?', time_str):
        return timedelta(days=int(match.group(1)))
    else:
        raise ValidationError(f"Cannot parse deadline: {time_str}")


def parse_gpu(gpu_str: str) -> dict:
    """Parse GPU specifications."""
    gpu_str = gpu_str.lower().strip()

    if gpu_str == 'cheapest':
        return {'gpu_hint': 'cheapest'}
    elif ':' in gpu_str:
        gpu_type, count = gpu_str.split(':', 1)
        try:
            return {
                'gpu_type': gpu_type,
                'gpu_count': int(count)
            }
        except ValueError:
            raise ValidationError(f"Invalid GPU count: {count}")
    else:
        return {'gpu_type': gpu_str}


class TestCLIParsing:
    """Test natural language parsing for CLI v2."""

    def test_parse_deadline_hours(self):
        """Test parsing hours."""
        assert parse_deadline("1 hour") == timedelta(hours=1)
        assert parse_deadline("2 hours") == timedelta(hours=2)
        assert parse_deadline("24 HOURS") == timedelta(hours=24)

    def test_parse_deadline_minutes(self):
        """Test parsing minutes."""
        assert parse_deadline("1 minute") == timedelta(minutes=1)
        assert parse_deadline("30 minutes") == timedelta(minutes=30)
        assert parse_deadline("90 Minutes") == timedelta(minutes=90)

    def test_parse_deadline_days(self):
        """Test parsing days."""
        assert parse_deadline("1 day") == timedelta(days=1)
        assert parse_deadline("7 days") == timedelta(days=7)

    def test_parse_deadline_invalid(self):
        """Test invalid time expressions."""
        with pytest.raises(ValidationError, match="Cannot parse deadline"):
            parse_deadline("two hours")

        with pytest.raises(ValidationError, match="Cannot parse deadline"):
            parse_deadline("5 decades")

    def test_parse_gpu_cheapest(self):
        """Test cheapest GPU selection."""
        assert parse_gpu("cheapest") == {'gpu_hint': 'cheapest'}
        assert parse_gpu("CHEAPEST") == {'gpu_hint': 'cheapest'}

    def test_parse_gpu_with_count(self):
        """Test GPU with count."""
        assert parse_gpu("a100:4") == {'gpu_type': 'a100', 'gpu_count': 4}
        assert parse_gpu("h100:8") == {'gpu_type': 'h100', 'gpu_count': 8}

    def test_parse_gpu_type_only(self):
        """Test GPU type only."""
        assert parse_gpu("a100") == {'gpu_type': 'a100'}
        assert parse_gpu("v100") == {'gpu_type': 'v100'}

    def test_parse_gpu_invalid_count(self):
        """Test invalid GPU count."""
        with pytest.raises(ValidationError, match="Invalid GPU count"):
            parse_gpu("a100:abc")

        with pytest.raises(ValidationError, match="Invalid GPU count"):
            parse_gpu("h100:1.5")


class TestRequirementsDetection:
    """Test automatic requirements file detection."""

    def test_finds_requirements_in_script_dir(self, tmp_path):
        """Test finding requirements.txt next to script."""
        # Create script and requirements in same directory
        script_path = tmp_path / "train.py"
        script_path.write_text("print('hello')")

        req_path = tmp_path / "requirements.txt"
        req_path.write_text("torch>=2.0.0\nnumpy")

        # Import and test the adapter
        from flow._internal.frontends.cli.adapter import CLIFrontendAdapter
        adapter = CLIFrontendAdapter()

        result = adapter._find_requirements(script_path)
        assert result == req_path

    def test_finds_requirements_in_cwd(self, tmp_path, monkeypatch):
        """Test finding requirements.txt in current directory."""
        # Create subdirectory with script
        subdir = tmp_path / "scripts"
        subdir.mkdir()
        script_path = subdir / "train.py"
        script_path.write_text("print('hello')")

        # Create requirements in parent (which will be cwd)
        req_path = tmp_path / "requirements.txt"
        req_path.write_text("torch>=2.0.0")

        # Change to parent directory
        monkeypatch.chdir(tmp_path)

        from flow._internal.frontends.cli.adapter import CLIFrontendAdapter
        adapter = CLIFrontendAdapter()

        result = adapter._find_requirements(script_path)
        assert result == req_path

    def test_no_requirements_returns_none(self, tmp_path, monkeypatch):
        """Test returns None when no requirements found."""
        # Create isolated directory
        isolated_dir = tmp_path / "isolated"
        isolated_dir.mkdir()

        script_path = isolated_dir / "train.py"
        script_path.write_text("print('hello')")

        # Change to isolated directory to avoid finding project files
        monkeypatch.chdir(isolated_dir)

        from flow._internal.frontends.cli.adapter import CLIFrontendAdapter
        adapter = CLIFrontendAdapter()

        result = adapter._find_requirements(script_path)
        assert result is None


class TestCLIFullIntegration:
    """Test full CLI parsing integration."""

    def test_parse_full_command(self, tmp_path):
        """Test parsing complete command line."""
        # Create a script file
        script_path = tmp_path / "train.py"
        script_path.write_text("print('training')")

        from flow._internal.frontends.cli.adapter import CLIFrontendAdapter
        adapter = CLIFrontendAdapter()

        args = [
            str(script_path),
            "--deadline", "2 hours",
            "--gpu", "a100:4",
            "--name", "my-training"
        ]

        spec = adapter._parse_and_convert_sync(args)

        assert spec.command == " ".join(args)
        # Note: deadline is stored on spec but not part of TaskSpec dataclass
        assert hasattr(spec, 'deadline') and spec.deadline == timedelta(hours=2)
        assert spec.resources.instance_type == 'a100'
        assert spec.resources.gpu_count == 4
        assert spec.name == "my-training"

    def test_parse_minimal_command(self, tmp_path):
        """Test parsing just script name."""
        script_path = tmp_path / "train.py"
        script_path.write_text("print('hello')")

        from flow._internal.frontends.cli.adapter import CLIFrontendAdapter
        adapter = CLIFrontendAdapter()

        args = [str(script_path)]
        spec = adapter._parse_and_convert_sync(args)

        assert spec.command == str(script_path)
        assert not hasattr(spec, 'deadline') or spec.deadline is None
        assert spec.resources.instance_type is None
        assert spec.resources.gpu_count is None
        assert spec.name == "cli-task"  # Default name

    def test_parse_missing_script(self):
        """Test error on missing script."""
        from flow._internal.frontends.cli.adapter import CLIFrontendAdapter
        adapter = CLIFrontendAdapter()

        with pytest.raises(ValidationError, match="Script not found"):
            adapter._parse_and_convert_sync(["nonexistent.py"])
