"""Test code packaging for remote execution."""

import os
import tarfile
import tempfile
import time
from pathlib import Path

import pytest

from flow.core.code_packager import CodePackager


class TestCodePackaging:
    """Test the CodePackager functionality."""

    @pytest.fixture
    def project_dir(self):
        """Create a test project directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create directory structure
            (root / "src").mkdir()
            (root / "src" / "models").mkdir()
            (root / "tests").mkdir()
            (root / "data").mkdir()
            (root / ".git").mkdir()
            (root / "__pycache__").mkdir()
            (root / ".pytest_cache").mkdir()

            # Create files
            (root / "train.py").write_text("# Training script\nimport torch")
            (root / "src" / "__init__.py").write_text("")
            (root / "src" / "model.py").write_text("class Model: pass")
            (root / "src" / "models" / "transformer.py").write_text("# Transformer")
            (root / "tests" / "test_model.py").write_text("# Tests")
            (root / "data" / "sample.txt").write_text("sample data")
            (root / "requirements.txt").write_text("torch>=1.0")
            (root / "README.md").write_text("# Project")
            (root / ".gitignore").write_text("__pycache__/\n*.pyc")
            (root / "__pycache__" / "cached.pyc").write_text("cached")
            (root / ".git" / "config").write_text("[core]")
            (root / "large_file.bin").write_text("x" * 1024 * 1024)  # 1MB

            yield root

    def test_packaging_includes_correct_files(self, project_dir):
        """Test that packaging includes the right files and excludes others."""
        packager = CodePackager()

        # Create package
        archive_path = packager.create_package(project_dir)

        assert archive_path.exists()
        assert str(archive_path).endswith(".tar.gz")

        # Check contents
        included_files = set()
        with tarfile.open(archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                included_files.add(member.name)

        # Should include Python files and important config
        assert "train.py" in included_files
        assert "src/__init__.py" in included_files
        assert "src/model.py" in included_files
        assert "src/models/transformer.py" in included_files
        assert "requirements.txt" in included_files
        assert "README.md" in included_files

        # Should exclude cache and git directories
        assert not any("__pycache__" in f for f in included_files)
        assert not any(".git/" in f for f in included_files)
        assert not any(".pytest_cache" in f for f in included_files)
        assert not any(".pyc" in f for f in included_files)

        # Clean up
        os.unlink(archive_path)

    def test_custom_excludes(self, project_dir):
        """Test custom exclude patterns."""
        # Add custom excludes via constructor
        custom_excludes = {"data/", "*.md", "tests/"}
        packager = CodePackager(exclude_patterns=custom_excludes)

        archive_path = packager.create_package(project_dir)

        included_files = set()
        with tarfile.open(archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                included_files.add(member.name)

        # Custom excludes should work
        assert not any("data/" in f for f in included_files)
        assert "README.md" not in included_files
        assert not any("tests/" in f for f in included_files)

        # Should still exclude defaults
        assert not any("__pycache__" in f for f in included_files)

        os.unlink(archive_path)

    @pytest.mark.parametrize("num_files,file_size", [
        (10, 1024),      # 10 files, 1KB each
        (100, 1024),     # 100 files, 1KB each
        (10, 1024*1024), # 10 files, 1MB each
    ])
    def test_packaging_performance(self, num_files, file_size):
        """Test packaging performance with various file configurations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test files
            for i in range(num_files):
                (root / f"file_{i}.py").write_text("x" * file_size)

            packager = CodePackager()

            start = time.time()
            archive_path = packager.create_package(root)
            duration = time.time() - start

            # Should complete in reasonable time
            assert duration < 10.0  # 10 seconds max

            # Check archive was created
            assert Path(archive_path).exists()
            archive_size = Path(archive_path).stat().st_size

            # Archive should be compressed
            total_input_size = num_files * file_size
            assert archive_size < total_input_size * 0.9  # At least 10% compression

            os.unlink(archive_path)

    def test_empty_directory(self):
        """Test packaging an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            packager = CodePackager()
            archive_path = packager.create_package(Path(tmpdir))

            # Should still create an archive
            assert Path(archive_path).exists()

            # Check it's a valid tarfile
            with tarfile.open(archive_path, "r:gz") as tar:
                members = list(tar.getmembers())
                assert len(members) == 0  # Empty archive

            os.unlink(archive_path)

    def test_single_file_directory(self):
        """Test packaging a directory with a single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "main.py").write_text("print('hello')")

            packager = CodePackager()
            archive_path = packager.create_package(root)

            with tarfile.open(archive_path, "r:gz") as tar:
                members = list(tar.getmembers())
                assert len(members) == 1
                assert members[0].name == "main.py"

            os.unlink(archive_path)
