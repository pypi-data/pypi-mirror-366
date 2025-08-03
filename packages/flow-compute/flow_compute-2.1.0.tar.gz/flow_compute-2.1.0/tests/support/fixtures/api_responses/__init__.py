"""API response fixtures for testing.

This module provides easy access to common API response fixtures,
eliminating the need for hardcoded responses in test files.
"""

import json
from pathlib import Path
from typing import Any, Dict

# Load fixtures on import
_FIXTURES_DIR = Path(__file__).parent
_FCP_RESPONSES = None


def _load_fcp_responses() -> Dict[str, Any]:
    """Load FCP API response fixtures."""
    global _FCP_RESPONSES
    if _FCP_RESPONSES is None:
        with open(_FIXTURES_DIR / "fcp_responses.json") as f:
            _FCP_RESPONSES = json.load(f)
    return _FCP_RESPONSES


class FCPResponses:
    """FCP API response fixtures."""
    
    @property
    def project_success(self) -> Dict[str, Any]:
        """Successful project response."""
        return _load_fcp_responses()["project"]["success"].copy()
    
    @property
    def instance_type_gpu_single(self) -> Dict[str, Any]:
        """Single GPU instance type response."""
        return _load_fcp_responses()["instance_types"]["gpu_single"].copy()
    
    @property
    def instance_type_gpu_multi(self) -> Dict[str, Any]:
        """Multi-GPU instance type response."""
        return _load_fcp_responses()["instance_types"]["gpu_multi"].copy()
    
    @property 
    def instance_type_cpu_only(self) -> Dict[str, Any]:
        """CPU-only instance type response."""
        return _load_fcp_responses()["instance_types"]["cpu_only"].copy()
    
    @property
    def auction_available(self) -> Dict[str, Any]:
        """Available auction response."""
        return _load_fcp_responses()["auctions"]["available"].copy()
    
    @property
    def bid_pending(self) -> Dict[str, Any]:
        """Pending bid response."""
        return _load_fcp_responses()["bids"]["pending"].copy()
    
    @property
    def bid_won(self) -> Dict[str, Any]:
        """Won bid response."""
        return _load_fcp_responses()["bids"]["won"].copy()
    
    @property
    def bid_lost(self) -> Dict[str, Any]:
        """Lost bid response."""
        return _load_fcp_responses()["bids"]["lost"].copy()
    
    @property
    def bid_expired(self) -> Dict[str, Any]:
        """Expired bid response."""
        return _load_fcp_responses()["bids"]["expired"].copy()
    
    @property
    def volume_available(self) -> Dict[str, Any]:
        """Available volume response."""
        return _load_fcp_responses()["volumes"]["available"].copy()
    
    @property
    def volume_file_share(self) -> Dict[str, Any]:
        """File share volume response."""
        return _load_fcp_responses()["volumes"]["file_share"].copy()
    
    @property
    def volume_attached(self) -> Dict[str, Any]:
        """Attached volume response."""
        return _load_fcp_responses()["volumes"]["attached"].copy()
    
    @property
    def task_created(self) -> Dict[str, Any]:
        """Task creation response."""
        return _load_fcp_responses()["tasks"]["created"].copy()
    
    @property
    def task_running(self) -> Dict[str, Any]:
        """Running task response."""
        return _load_fcp_responses()["tasks"]["running"].copy()
    
    @property
    def task_completed(self) -> Dict[str, Any]:
        """Completed task response."""
        return _load_fcp_responses()["tasks"]["completed"].copy()
    
    @property
    def task_failed(self) -> Dict[str, Any]:
        """Failed task response."""
        return _load_fcp_responses()["tasks"]["failed"].copy()
    
    @property
    def allocations_list(self) -> list:
        """List of allocations response."""
        return _load_fcp_responses()["allocations"]["list"].copy()
    
    @property
    def error_validation(self) -> Dict[str, Any]:
        """Validation error response."""
        return _load_fcp_responses()["errors"]["validation"].copy()
    
    @property
    def error_not_found(self) -> Dict[str, Any]:
        """Not found error response."""
        return _load_fcp_responses()["errors"]["not_found"].copy()
    
    @property
    def error_rate_limit(self) -> Dict[str, Any]:
        """Rate limit error response."""
        return _load_fcp_responses()["errors"]["rate_limit"].copy()
    
    @property
    def error_server(self) -> Dict[str, Any]:
        """Server error response."""
        return _load_fcp_responses()["errors"]["server_error"].copy()
    
    @property
    def large_task_list(self) -> Dict[str, Any]:
        """Large task list response."""
        return _load_fcp_responses()["large_responses"]["task_list"].copy()
    
    def custom_task(self, **kwargs) -> Dict[str, Any]:
        """Create a custom task response with provided fields."""
        base = self.task_running
        base.update(kwargs)
        return base
    
    def custom_volume(self, **kwargs) -> Dict[str, Any]:
        """Create a custom volume response with provided fields."""
        base = self.volume_available
        base.update(kwargs)
        return base
    
    def custom_error(self, code: str, message: str, **kwargs) -> Dict[str, Any]:
        """Create a custom error response."""
        error = {
            "error": message,
            "code": code,
            "message": message
        }
        error.update(kwargs)
        return error


# Singleton instance
fcp_responses = FCPResponses()


# Export for convenience
__all__ = ['fcp_responses', 'FCPResponses']