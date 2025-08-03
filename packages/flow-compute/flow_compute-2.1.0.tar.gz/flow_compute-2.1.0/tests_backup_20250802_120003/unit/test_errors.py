"""Tests for Flow SDK error handling."""

from flow.errors import (
    APIError,
    AuthenticationError,
    ConfigParserError,
    FlowError,
    FlowOperationError,
    InvalidResponseError,
    NetworkError,
    ProviderError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)


class TestFlowErrors:
    """Test Flow SDK error classes."""

    def test_base_flow_error(self):
        """Test base FlowError."""
        error = FlowError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid API key")
        assert str(error) == "Invalid API key"
        assert isinstance(error, FlowError)

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        error = ResourceNotFoundError("Task not found")
        assert str(error) == "Task not found"
        assert isinstance(error, FlowError)

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid instance type")
        assert str(error) == "Invalid instance type"
        assert isinstance(error, FlowError)

    def test_api_error_with_status(self):
        """Test APIError with status code."""
        error = APIError("Bad request", status_code=400)
        assert str(error) == "Bad request"
        assert error.status_code == 400
        assert isinstance(error, FlowError)

    def test_api_error_without_status(self):
        """Test APIError without status code."""
        error = APIError("Server error")
        assert str(error) == "Server error"
        assert error.status_code is None

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("Connection refused")
        assert str(error) == "Connection refused"
        assert isinstance(error, FlowError)

    def test_invalid_response_error(self):
        """Test InvalidResponseError."""
        error = InvalidResponseError("Invalid JSON response")
        assert str(error) == "Invalid JSON response"
        assert isinstance(error, FlowError)

    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError("Request timed out")
        assert str(error) == "Request timed out"
        assert isinstance(error, FlowError)

    def test_configuration_error(self):
        """Test ProviderError."""
        error = ProviderError("Missing API key")
        assert str(error) == "Missing API key"
        assert isinstance(error, FlowError)

    def test_config_parser_error(self):
        """Test ConfigParserError."""
        error = ConfigParserError("Invalid YAML syntax")
        assert str(error) == "Invalid YAML syntax"
        assert isinstance(error, FlowError)

    def test_flow_operation_error(self):
        """Test FlowOperationError with context."""
        cause = ValueError("Invalid value")
        error = FlowOperationError("submit", "task-123", cause)
        assert "submit failed for task-123" in str(error)
        assert error.operation == "submit"
        assert error.resource_id == "task-123"
        assert error.cause == cause
        assert isinstance(error, FlowError)

    def test_error_inheritance(self):
        """Test error inheritance chain."""
        # All errors should inherit from FlowError
        errors = [
            AuthenticationError("test"),
            ResourceNotFoundError("test"),
            ValidationError("test"),
            APIError("test"),
            NetworkError("test"),
            InvalidResponseError("test"),
            TimeoutError("test"),
            ProviderError("test"),
            ConfigParserError("test"),
            FlowOperationError("test", "resource-1", ValueError("test cause")),
        ]

        for error in errors:
            assert isinstance(error, FlowError)
            assert isinstance(error, Exception)
