"""Unit tests for script size handling."""

import base64
import gzip
import hashlib
from unittest.mock import Mock, patch

import pytest

from flow.providers.fcp.runtime.script_size import (
    CompressionStrategy,
    InlineStrategy,
    PreparedScript,
    ScriptSizeHandler,
    ScriptTooLargeError,
    SplitStrategy,
)
from flow.providers.fcp.storage import IStorageBackend, StorageUrl


class TestInlineStrategy:
    """Test inline strategy for small scripts."""
    
    def test_can_handle_small_script(self):
        """Test that inline strategy accepts small scripts."""
        strategy = InlineStrategy()
        small_script = "#!/bin/bash\necho 'Hello World'"
        
        assert strategy.can_handle(small_script, 10_000) is True
    
    def test_cannot_handle_large_script(self):
        """Test that inline strategy rejects large scripts."""
        strategy = InlineStrategy()
        large_script = "#!/bin/bash\n" + "echo 'x' " * 2000  # >10KB
        
        assert strategy.can_handle(large_script, 10_000) is False
    
    def test_prepare_returns_unchanged_script(self):
        """Test that inline strategy returns script unchanged."""
        strategy = InlineStrategy()
        script = "#!/bin/bash\necho 'Test'"
        
        result = strategy.prepare(script, 10_000)
        
        assert isinstance(result, PreparedScript)
        assert result.content == script
        assert result.strategy == "inline"
        assert result.requires_network is False
        assert result.metadata["original_size"] == len(script.encode("utf-8"))


class TestCompressionStrategy:
    """Test compression strategy."""
    
    def test_can_handle_compressible_script(self):
        """Test that compression strategy can handle scripts that compress well."""
        strategy = CompressionStrategy()
        # Highly repetitive script that compresses well
        script = "#!/bin/bash\n" + "echo 'test line' # comment\n" * 500
        
        assert strategy.can_handle(script, 10_000) is True
    
    def test_cannot_handle_incompressible_large_script(self):
        """Test that compression strategy rejects scripts that don't compress enough."""
        strategy = CompressionStrategy()
        # Random data doesn't compress well
        import random
        import string
        random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=20_000))
        script = f"#!/bin/bash\n# {random_data}"
        
        assert strategy.can_handle(script, 10_000) is False
    
    def test_prepare_creates_bootstrap_script(self):
        """Test that compression creates a valid bootstrap script."""
        strategy = CompressionStrategy()
        original = "#!/bin/bash\necho 'Hello World'\n" * 100
        
        result = strategy.prepare(original, 10_000)
        
        # Verify result structure
        assert isinstance(result, PreparedScript)
        assert result.strategy == "compressed"
        assert result.requires_network is False
        assert "#!/bin/bash" in result.content
        assert "base64 -d | gunzip" in result.content
        assert result.metadata["original_size"] == len(original.encode("utf-8"))
        assert result.metadata["compression_ratio"] > 1.0
        
        # Verify the compressed data is valid
        assert "COMPRESSED_EOF" in result.content
        
    def test_compressed_script_can_be_decompressed(self):
        """Test that compressed script can be decompressed to original."""
        strategy = CompressionStrategy()
        original = "#!/bin/bash\necho 'Test Script'\ndate\nhostname"
        
        result = strategy.prepare(original, 10_000)
        
        # Extract the base64 data from the bootstrap script
        lines = result.content.split('\n')
        start_idx = None
        end_idx = None
        for i, line in enumerate(lines):
            if "cat <<'COMPRESSED_EOF'" in line:
                start_idx = i + 1
            elif line.strip() == "COMPRESSED_EOF":
                end_idx = i
                break
        
        assert start_idx is not None and end_idx is not None
        compressed_data = '\n'.join(lines[start_idx:end_idx])
        
        # Decompress and verify
        decoded = base64.b64decode(compressed_data)
        decompressed = gzip.decompress(decoded).decode('utf-8')
        
        assert decompressed == original


class TestSplitStrategy:
    """Test split strategy with external storage."""
    
    def setup_method(self):
        """Set up mock storage backend."""
        self.mock_storage = Mock(spec=IStorageBackend)
        self.strategy = SplitStrategy(self.mock_storage)
    
    def test_can_handle_large_script(self):
        """Test that split strategy can handle large scripts."""
        large_script = "#!/bin/bash\n" + "x" * 1_000_000  # 1MB
        
        assert self.strategy.can_handle(large_script, 10_000) is True
    
    def test_cannot_handle_enormous_script(self):
        """Test that split strategy rejects scripts over 100MB."""
        enormous_script = "x" * 101_000_000  # >100MB
        
        assert self.strategy.can_handle(enormous_script, 10_000) is False
    
    def test_prepare_stores_and_creates_bootstrap(self):
        """Test that split strategy stores script and creates download bootstrap."""
        script = "#!/bin/bash\necho 'Large script content'"
        script_hash = hashlib.sha256(script.encode("utf-8")).hexdigest()
        
        # Mock storage response
        mock_url = StorageUrl(
            url="https://storage.example.com/scripts/abc123",
            expires_at=None,
            content_type="text/x-shellscript",
            size_bytes=len(script.encode("utf-8"))
        )
        self.mock_storage.store.return_value = mock_url
        
        result = self.strategy.prepare(script, 10_000)
        
        # Verify storage was called
        self.mock_storage.store.assert_called_once()
        call_args = self.mock_storage.store.call_args
        assert call_args[1]["key"].endswith(script_hash)
        assert call_args[1]["data"] == script.encode("utf-8")
        
        # Verify result
        assert isinstance(result, PreparedScript)
        assert result.strategy == "split"
        assert result.requires_network is True
        assert result.metadata["original_size"] == len(script.encode("utf-8"))
        assert result.metadata["payload_url"] == mock_url.url
        assert result.metadata["sha256"] == script_hash
        
        # Verify bootstrap script
        assert "#!/bin/bash" in result.content
        assert mock_url.url in result.content
        assert script_hash in result.content
        assert "curl -fsSL" in result.content
        assert "sha256sum" in result.content


class TestScriptSizeHandler:
    """Test main script size handler."""
    
    def test_small_script_uses_inline(self):
        """Test that small scripts use inline strategy."""
        handler = ScriptSizeHandler(storage_backend=None)
        small_script = "#!/bin/bash\necho 'small'"
        
        result = handler.prepare_script(small_script)
        
        assert result.strategy == "inline"
        assert result.content == small_script
    
    def test_medium_script_uses_compression(self):
        """Test that medium scripts use compression."""
        handler = ScriptSizeHandler(storage_backend=None)
        # Create a script that's too big for inline but compresses well
        medium_script = "#!/bin/bash\n" + "echo 'repeated line'\n" * 1000
        
        result = handler.prepare_script(medium_script)
        
        assert result.strategy == "compressed"
        assert "base64 -d | gunzip" in result.content
    
    def test_large_script_uses_split_with_storage(self):
        """Test that large scripts use split strategy when storage available."""
        mock_storage = Mock(spec=IStorageBackend)
        mock_storage.store.return_value = StorageUrl(
            url="https://example.com/script",
            expires_at=None,
            content_type="text/x-shellscript",
            size_bytes=100
        )
        
        handler = ScriptSizeHandler(storage_backend=mock_storage)
        # Create a large incompressible script
        import random
        import string
        random_data = ''.join(random.choices(string.ascii_letters, k=50_000))
        large_script = f"#!/bin/bash\n# {random_data}"
        
        result = handler.prepare_script(large_script)
        
        assert result.strategy == "split"
        assert result.requires_network is True
    
    def test_large_script_fails_without_storage(self):
        """Test that large scripts fail when no storage backend available."""
        handler = ScriptSizeHandler(storage_backend=None)
        # Create a large incompressible script
        import random
        import string
        random_data = ''.join(random.choices(string.ascii_letters, k=50_000))
        large_script = f"#!/bin/bash\n# {random_data}"
        
        with pytest.raises(ScriptTooLargeError) as exc_info:
            handler.prepare_script(large_script)
        
        assert "exceeds maximum supported size" in str(exc_info.value)
        assert "inline" in exc_info.value.strategies_tried
        assert "compressed" in exc_info.value.strategies_tried
    
    def test_validate_script_size(self):
        """Test script size validation."""
        handler = ScriptSizeHandler(storage_backend=None)
        
        # Small script should validate
        is_valid, error = handler.validate_script_size("#!/bin/bash\necho 'test'")
        assert is_valid is True
        assert error is None
        
        # Large incompressible script should fail with helpful message
        import random
        import string
        # Create random data that won't compress well
        random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=50_000))
        large_script = f"#!/bin/bash\n# {random_data}"
        is_valid, error = handler.validate_script_size(large_script)
        assert is_valid is False
        assert "Configure local storage backend" in error or "storage backend is configured" in error
    
    def test_handler_continues_on_strategy_error(self):
        """Test that handler tries next strategy if one fails."""
        # Create a handler with a failing compression strategy
        handler = ScriptSizeHandler(storage_backend=None)
        
        # Mock the compression strategy to fail
        with patch.object(handler.strategies[1], 'can_handle', side_effect=Exception("Compression failed")):
            # Small script should still work with inline
            result = handler.prepare_script("#!/bin/bash\necho 'test'")
            assert result.strategy == "inline"


class TestPreparedScript:
    """Test PreparedScript model."""
    
    def test_size_bytes_property(self):
        """Test that size_bytes calculates correctly."""
        script = PreparedScript(
            content="Hello World",
            strategy="inline",
            requires_network=False
        )
        
        assert script.size_bytes == len("Hello World".encode("utf-8"))
    
    def test_compression_ratio_property(self):
        """Test compression ratio calculation."""
        script = PreparedScript(
            content="compressed",
            strategy="compressed",
            metadata={"original_size": 1000}
        )
        
        expected_ratio = 1000 / len("compressed".encode("utf-8"))
        assert script.compression_ratio == expected_ratio
        
        # Non-compressed script should return None
        inline_script = PreparedScript(
            content="inline",
            strategy="inline"
        )
        assert inline_script.compression_ratio is None