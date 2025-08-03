"""FCP provider-specific errors with proper hierarchy.

This module defines a clean error hierarchy for FCP operations,
providing specific error types for different failure scenarios.
"""

from flow.errors import FlowError


class FCPError(FlowError):
    """Base error for all FCP provider operations."""

    pass


class FCPAPIError(FCPError):
    """Error communicating with FCP API."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class FCPAuthenticationError(FCPAPIError):
    """Authentication failed with FCP API."""

    pass


class FCPResourceNotFoundError(FCPAPIError):
    """Requested resource not found in FCP."""

    pass


class FCPQuotaExceededError(FCPAPIError):
    """Quota or limit exceeded in FCP."""

    pass


class FCPValidationError(FCPError):
    """Invalid parameters provided to FCP operation."""

    pass


class FCPTimeoutError(FCPError):
    """Operation timed out."""

    pass


class FCPInstanceError(FCPError):
    """Error related to instance operations."""

    pass


class FCPBidError(FCPError):
    """Error related to bid operations."""

    pass


class FCPVolumeError(FCPError):
    """Error related to volume operations."""

    pass
