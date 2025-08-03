"""Clean bid building component for FCP provider.

This module provides a clean, testable approach to building bid payloads,
following the Single Responsibility Principle.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from flow.api.models import TaskConfig
from flow.errors import FlowError

logger = logging.getLogger(__name__)


class BidValidationError(FlowError):
    """Raised when bid parameters are invalid."""

    pass


@dataclass
class BidSpecification:
    """Complete specification for a bid request."""

    # Required fields
    project_id: str
    region: str
    name: str
    instance_quantity: int
    limit_price: str  # Dollar string format (e.g., "$25.60")

    # Instance targeting - must have auction_id OR instance_type (not both)
    auction_id: Optional[str] = None
    instance_type: Optional[str] = None

    # Launch specification
    ssh_keys: List[str] = None
    startup_script: str = ""
    volumes: List[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate the specification after initialization."""
        self._validate()

        # Set defaults
        if self.ssh_keys is None:
            self.ssh_keys = []
        if self.volumes is None:
            self.volumes = []

    def _validate(self):
        """Validate bid specification.

        Raises:
            BidValidationError: If specification is invalid
        """
        # Required fields
        if not self.project_id:
            raise BidValidationError("project_id is required")
        if not self.region:
            raise BidValidationError("region is required")
        if not self.name:
            raise BidValidationError("name is required")
        if self.instance_quantity < 1:
            raise BidValidationError("instance_quantity must be at least 1")

        # Price validation
        if not self.limit_price or not self.limit_price.startswith("$"):
            raise BidValidationError("limit_price must be in dollar format (e.g., '$25.60')")

        # Instance targeting validation
        # For spot bids (with auction_id), instance_type is also required by the API
        if self.auction_id and not self.instance_type:
            raise BidValidationError(
                "When auction_id is provided, instance_type is also required for spot bids"
            )
        if not self.auction_id and not self.instance_type:
            raise BidValidationError(
                "Must specify instance_type (and optionally auction_id for spot instances)"
            )

    def to_api_payload(self) -> Dict[str, Any]:
        """Convert to FCP API payload format.

        Returns:
            Dict ready for API submission
        """
        # Build launch specification
        # Extract volume IDs from volume attachment specs
        volume_ids = [vol["volume_id"] for vol in self.volumes] if self.volumes else []

        launch_spec = {
            "ssh_keys": self.ssh_keys,
            "startup_script": self.startup_script,
            "volumes": volume_ids,  # FCP API expects list of volume IDs, not attachment specs
        }

        # Build base payload
        payload = {
            "project": self.project_id,
            "region": self.region,
            "name": self.name,
            "instance_quantity": self.instance_quantity,
            "limit_price": self.limit_price,
            "launch_specification": launch_spec,
        }

        # Add instance targeting
        payload["instance_type"] = self.instance_type
        if self.auction_id:
            payload["auction_id"] = self.auction_id

        return payload


class BidBuilder:
    """Builds bid specifications from task configurations."""

    @staticmethod
    def build_specification(
        config: TaskConfig,
        project_id: str,
        region: str,
        auction_id: Optional[str] = None,
        instance_type_id: Optional[str] = None,
        ssh_keys: Optional[List[str]] = None,
        startup_script: str = "",
        volume_attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> BidSpecification:
        """Build a bid specification from task config and resolved components.

        Args:
            config: Task configuration
            project_id: Resolved project ID
            region: Target region
            auction_id: Optional auction ID for spot instances
            instance_type_id: Optional instance type ID for on-demand
            ssh_keys: List of SSH key IDs
            startup_script: Complete startup script
            volume_attachments: Volume attachment specifications

        Returns:
            Complete BidSpecification

        Raises:
            BidValidationError: If parameters are invalid
        """
        # Determine limit price based on priority or explicit setting
        if config.max_price_per_hour is not None:
            # Explicit limit price takes precedence
            limit_price = f"${config.max_price_per_hour:.2f}"
        else:
            # Use priority tier directly
            tier = config.priority

            # Parse instance type to extract GPU count and type
            instance_type_lower = config.instance_type.lower()
            
            # Extract GPU count and type (e.g., "8xa100" -> count=8, type="a100")
            gpu_count = 1  # Default to single GPU
            gpu_type = instance_type_lower
            
            # Check for count prefix (e.g., "8x")
            if "x" in instance_type_lower:
                parts = instance_type_lower.split("x", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    gpu_count = int(parts[0])
                    gpu_type = parts[1]
            
            # Remove memory suffix (e.g., ".80gb")
            gpu_type = gpu_type.split(".")[0]

            # Per-GPU prices by tier (these are per-GPU prices)
            per_gpu_prices = {
                "h100": {"low": 4.0, "med": 8.0, "high": 16.0},
                "a100": {"low": 3.0, "med": 6.0, "high": 12.0},
                "a10": {"low": 1.0, "med": 2.0, "high": 4.0},
                "t4": {"low": 0.5, "med": 1.0, "high": 2.0},
                "default": {"low": 2.0, "med": 4.0, "high": 8.0},
            }

            gpu_prices = per_gpu_prices.get(gpu_type, per_gpu_prices["default"])
            per_gpu_price = gpu_prices[tier]
            
            # Calculate total price: per-GPU price * number of GPUs
            total_price = per_gpu_price * gpu_count
            limit_price = f"${total_price:.2f}"

        # Ensure we have instance targeting
        if not auction_id and not instance_type_id:
            raise BidValidationError("Either auction_id or instance_type_id must be provided")

        return BidSpecification(
            project_id=project_id,
            region=region,
            name=config.name,
            instance_quantity=config.num_instances,
            limit_price=limit_price,
            auction_id=auction_id,
            instance_type=instance_type_id,
            ssh_keys=ssh_keys or [],
            startup_script=startup_script,
            volumes=volume_attachments or [],
        )

    @staticmethod
    def format_volume_attachment(
        volume_id: str, mount_path: str, mode: str = "rw"
    ) -> Dict[str, Any]:
        """Format a volume attachment specification.

        Args:
            volume_id: ID of the volume to attach
            mount_path: Path to mount the volume
            mode: Access mode (rw or ro)

        Returns:
            Volume attachment dict
        """
        return {
            "volume_id": volume_id,
            "mount_path": mount_path,
            "mode": mode,
        }
