"""Test template engine functionality.

The template engine is responsible for rendering script templates.
Currently using a simple implementation but tests ensure interface stability.
"""

import pytest

from flow.providers.fcp.runtime.startup.templates import SimpleTemplateEngine, create_template_engine


class TestSimpleTemplateEngine:
    """Test the simple template engine implementation."""

    def test_render_without_variables(self):
        """Test rendering template without variables."""
        engine = SimpleTemplateEngine()
        template = "#!/bin/bash\necho 'Hello World'"

        result = engine.render(template, {})

        assert result == template

    def test_render_with_basic_substitution(self):
        """Test rendering with basic variable substitution."""
        engine = SimpleTemplateEngine()
        template = "Hello ${name}, welcome to ${place}"

        result = engine.render(template, {
            "name": "Alice",
            "place": "Wonderland"
        })

        assert result == "Hello Alice, welcome to Wonderland"

    def test_render_missing_variables(self):
        """Test rendering with missing variables."""
        engine = SimpleTemplateEngine()
        template = "Hello ${name}, your ID is ${id}"

        result = engine.render(template, {"name": "Bob"})

        # Missing variables should remain as-is
        assert result == "Hello Bob, your ID is ${id}"

    def test_render_with_special_characters(self):
        """Test rendering with special characters in values."""
        engine = SimpleTemplateEngine()
        template = "Command: ${cmd}"

        test_cases = [
            ("echo 'hello'", "Command: echo 'hello'"),
            ("rm -rf /", "Command: rm -rf /"),
            ("$VAR && echo done", "Command: $VAR && echo done"),
            ("a\\nb\\tc", "Command: a\\nb\\tc"),
        ]

        for value, expected in test_cases:
            result = engine.render(template, {"cmd": value})
            assert result == expected

    def test_render_bash_script_template(self):
        """Test rendering a bash script template."""
        engine = SimpleTemplateEngine()
        template = """#!/bin/bash
set -e

IMAGE=${image}
CONTAINER_NAME=${container_name}

echo "Pulling $IMAGE"
docker pull $IMAGE

echo "Running container $CONTAINER_NAME"
docker run -d --name $CONTAINER_NAME $IMAGE
"""

        result = engine.render(template, {
            "image": "ubuntu:22.04",
            "container_name": "my-app"
        })

        assert "IMAGE=ubuntu:22.04" in result
        assert "CONTAINER_NAME=my-app" in result
        assert "Pulling $IMAGE" in result

    def test_render_with_numeric_values(self):
        """Test rendering with numeric values."""
        engine = SimpleTemplateEngine()
        template = "Port: ${port}, Timeout: ${timeout}s"

        result = engine.render(template, {
            "port": 8080,
            "timeout": 30
        })

        assert result == "Port: 8080, Timeout: 30s"

    def test_render_with_none_values(self):
        """Test rendering with None values."""
        engine = SimpleTemplateEngine()
        template = "Value: ${value}"

        result = engine.render(template, {"value": None})

        # None should be rendered as empty string or "None"
        assert result in ["Value: ", "Value: None"]


class TestTemplateEngineFactory:
    """Test the template engine factory."""

    def test_create_simple_engine(self):
        """Test creating simple template engine."""
        engine = create_template_engine("simple")

        assert isinstance(engine, SimpleTemplateEngine)

    def test_create_default_engine(self):
        """Test creating default template engine."""
        engine = create_template_engine()

        assert isinstance(engine, SimpleTemplateEngine)

    def test_create_invalid_engine(self):
        """Test creating invalid template engine type."""
        with pytest.raises(ValueError, match="Unknown template engine"):
            create_template_engine("invalid_engine_type")

    def test_simple_engine_interface(self):
        """Test that created engine has correct interface."""
        engine = create_template_engine("simple")

        # Should have render method
        assert hasattr(engine, "render")
        assert callable(engine.render)

        # Test basic rendering
        result = engine.render("Hello ${name}", {"name": "World"})
        assert result == "Hello World"


class TestTemplateEngineEdgeCases:
    """Test edge cases for template engine."""

    def test_empty_template(self):
        """Test rendering empty template."""
        engine = SimpleTemplateEngine()

        result = engine.render("", {"key": "value"})
        assert result == ""

    def test_template_with_no_placeholders(self):
        """Test template without any placeholders."""
        engine = SimpleTemplateEngine()
        template = "Just plain text"

        result = engine.render(template, {"key": "value"})
        assert result == template

    def test_json_like_template(self):
        """Test template with JSON-like structure."""
        engine = SimpleTemplateEngine()
        template = 'CONFIG=${json_value}'

        result = engine.render(template, {"json_value": '{"key": "value"}'})
        assert result == 'CONFIG={"key": "value"}'

    def test_multiple_same_variable(self):
        """Test template with same variable multiple times."""
        engine = SimpleTemplateEngine()
        template = "${name} says hello to ${name}"

        result = engine.render(template, {"name": "Alice"})
        assert result == "Alice says hello to Alice"

    def test_unicode_handling(self):
        """Test template with unicode characters."""
        engine = SimpleTemplateEngine()
        template = "Hello ${emoji} ${name}"

        result = engine.render(template, {
            "emoji": "🚀",
            "name": "世界"
        })

        assert result == "Hello 🚀 世界"
