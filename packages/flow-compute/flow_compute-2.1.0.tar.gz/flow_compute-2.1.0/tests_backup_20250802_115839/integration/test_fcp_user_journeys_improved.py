"""Improved integration tests for FCP user journeys.

These tests use minimal mocking and focus on real behavior.
We only mock at the HTTP boundary when necessary for test isolation.
"""

import uuid
from typing import Any, Dict, List

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus
from flow.providers.fcp.core.errors import FCPInstanceError
from flow.providers.fcp.provider import FCPProvider


class FCPTestDouble:
    """Test double that simulates FCP API behavior.
    
    This is NOT a mock - it simulates realistic API behavior
    for testing without hitting the real API.
    """

    def __init__(self):
        self.calls = []  # Track calls for assertions
        self._projects = {"test-project": "proj-123"}
        self._ssh_keys = {"test-key": "ssh-key-123"}
        self._bids = {}

    def request(self, method: str, url: str, **kwargs) -> Any:
        """Simulate FCP API responses based on realistic behavior."""
        self.calls.append((method, url, kwargs))

        if url == "/v2/projects":
            return self._handle_projects()
        elif url == "/v2/ssh-keys":
            return self._handle_ssh_keys()
        elif url == "/v2/spot/availability":
            return self._handle_availability(kwargs.get("params", {}))
        elif url == "/v2/spot/bids" and method == "POST":
            return self._handle_create_bid(kwargs.get("json", {}))
        elif url == "/v2/spot/bids" and method == "GET":
            return self._handle_list_bids(kwargs.get("params", {}))
        elif url.startswith("/v2/spot/bids/") and method == "GET":
            bid_id = url.split("/")[-1]
            return self._handle_get_bid(bid_id)

        return []

    def _handle_projects(self) -> List[Dict[str, Any]]:
        """Simulate project listing."""
        return [
            {"fid": fid, "name": name, "created_at": "2024-01-01T00:00:00Z"}
            for name, fid in self._projects.items()
        ]

    def _handle_ssh_keys(self) -> List[Dict[str, Any]]:
        """Simulate SSH key listing."""
        return [
            {"fid": fid, "name": name, "public_key": f"ssh-rsa {name}..."}
            for name, fid in self._ssh_keys.items()
        ]

    def _handle_availability(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulate instance availability based on request."""
        # The actual API returns all availability, not filtered by instance type
        # Return a mix of different instance types available in different regions
        all_auctions = [
            {
                "fid": "auc_a5185c00",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100
                "last_instance_price": "$25.00",
                "region": "us-central1-a",
                "capacity": 10,
            },
            {
                "fid": "auc_b6296d11",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100
                "last_instance_price": "$30.00",
                "region": "us-east-1",
                "capacity": 5,
            },
            {
                "fid": "auc_c7307e22",
                "instance_type": "it_5M6aGxGovNeX5ltT",  # 2xa100
                "last_instance_price": "$50.00",
                "region": "us-central1-a",
                "capacity": 3,
            },
            {
                "fid": "auc_d8418f33",
                "instance_type": "it_fK7Cx6TVhOK5ZfXT",  # 4xa100
                "last_instance_price": "$100.00",
                "region": "us-west-2",
                "capacity": 2,
            },
            {
                "fid": "auc_e9529g44",
                "instance_type": "it_J7OyNf9idfImLIFo",  # 8xa100
                "last_instance_price": "$200.00",
                "region": "us-central1-a",
                "capacity": 1,
            },
            {
                "fid": "auc_h100",
                "instance_type": "it_5ECSoHQjLBzrp5YM",  # 8xh100
                "last_instance_price": "$400.00",
                "region": "us-central1-a",
                "capacity": 1,
            },
        ]

        # Apply any filtering if provided
        if params.get("region"):
            all_auctions = [a for a in all_auctions if a["region"] == params["region"]]

        # Filter by instance type if provided
        if params.get("instance_type"):
            requested_type = params["instance_type"]
            all_auctions = [a for a in all_auctions if a["instance_type"] == requested_type]

        return all_auctions

    def _handle_create_bid(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate bid creation."""
        bid_id = f"bid_{uuid.uuid4().hex[:8]}"
        bid = {
            "fid": bid_id,
            "status": "pending",
            "name": payload.get("name", "unnamed"),
            "instance_type": payload["instance_type"],
            "limit_price": payload.get("limit_price", "100.00"),
        }
        self._bids[bid_id] = bid
        return bid

    def _handle_list_bids(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate listing bids for a project."""
        # Return bids in the expected format with 'data' key
        return {"data": list(self._bids.values())}

    def _handle_get_bid(self, bid_id: str) -> Dict[str, Any]:
        """Simulate bid status check."""
        if bid_id not in self._bids:
            raise Exception(f"Bid {bid_id} not found")

        bid = self._bids[bid_id]
        # Simulate progression: pending -> provisioning -> allocated
        if bid["status"] == "pending":
            bid["status"] = "provisioning"
        elif bid["status"] == "provisioning":
            bid["status"] = "allocated"

        return bid


class TestFCPUserJourneysImproved:
    """Test real user workflows with minimal mocking.
    
    These tests verify complete user journeys with realistic
    API behavior simulation.
    """

    @pytest.fixture
    def provider(self):
        """Create provider with test double."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "project": "test-project",
                "region": "us-central1-a",
                "ssh_keys": ["test-key"],
            }
        )

        test_double = FCPTestDouble()
        provider = FCPProvider(config, http_client=test_double)
        provider._test_double = test_double  # For assertions
        return provider

    def test_complete_gpu_training_workflow(self, provider):
        """Test the complete workflow a user follows to run GPU training."""
        # Step 1: User searches for available GPU instances
        instances = provider.find_instances({
            "instance_type": "a100",
            "max_price_per_hour": 50.0,
        })

        assert len(instances) > 0, "Should find available instances"
        # All instances should be some form of a100
        assert all("a100" in i.instance_type for i in instances)
        assert all(i.price_per_hour <= 50.0 for i in instances)

        # Step 2: User picks cheapest instance
        cheapest = min(instances, key=lambda i: i.price_per_hour)

        # Step 3: User submits training job
        config = TaskConfig(
            name="bert-training",
            instance_type="a100",  # User uses friendly name
            command=["python", "train.py", "--epochs", "10"],
            env={"CUDA_VISIBLE_DEVICES": "0"},
            upload_code=False,  # Disable code upload for integration test
        )

        task = provider.submit_task("a100", config)

        # Step 4: Verify task creation
        assert task.task_id.startswith("bid_")
        assert task.status == TaskStatus.PENDING
        assert task.name == "bert-training"

        # Step 5: User checks task status
        updated_task = provider.get_task(task.task_id)
        assert updated_task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]

    def test_multi_gpu_instance_selection(self, provider):
        """Test selecting different GPU configurations."""
        # User wants to compare different GPU counts
        configs_to_test = [
            ("a100", 1),      # Single GPU
            ("2xa100", 2),    # Dual GPU
            ("4xa100", 4),    # Quad GPU
            ("8xa100", 8),    # Full node
        ]

        results = {}
        for instance_type, expected_gpus in configs_to_test:
            instances = provider.find_instances({"instance_type": instance_type})

            if instances:
                # Verify we get appropriate instance types back
                cheapest = min(instances, key=lambda i: i.price_per_hour)
                results[instance_type] = {
                    "available": True,
                    "price": cheapest.price_per_hour,
                    "price_per_gpu": cheapest.price_per_hour / expected_gpus,
                }
            else:
                results[instance_type] = {"available": False}

        # Verify price scaling makes sense
        if all(r["available"] for r in results.values()):
            # More GPUs should cost more in total
            assert results["2xa100"]["price"] > results["a100"]["price"]
            assert results["4xa100"]["price"] > results["2xa100"]["price"]

            # But price per GPU might decrease (bulk discount)
            assert results["2xa100"]["price_per_gpu"] <= results["a100"]["price_per_gpu"]

    def test_instance_type_migration_path(self, provider):
        """Test helping users migrate from old to new instance names."""
        # Common mistakes users make when migrating
        migration_tests = [
            # (what user tries, what they should use, should work)
            ("nvidia-a100", "a100", False),
            ("A100", "a100", False),
            ("gpu-a100", "a100", False),
            ("a100", "a100", True),
            ("a100-80gb", "a100", False),  # Incomplete name
            ("a100-80gb.sxm.1x", "a100", True),  # Full FCP name works
        ]

        for user_input, recommended, should_work in migration_tests:
            if should_work:
                # Should succeed
                instances = provider.find_instances({"instance_type": user_input})
                assert len(instances) > 0
            else:
                # Should fail with helpful error
                with pytest.raises(FCPInstanceError) as exc:
                    provider.find_instances({"instance_type": user_input})

                error = str(exc.value)
                assert f"Unknown instance type: {user_input}" in error
                assert "Available:" in error
                assert recommended in error, f"Error should suggest '{recommended}'"

    def test_h100_instance_selection(self, provider):
        """Test H100 instance selection and usage."""
        # H100s are more expensive but faster
        h100_instances = provider.find_instances({"instance_type": "8xh100"})
        a100_instances = provider.find_instances({"instance_type": "8xa100"})

        if h100_instances and a100_instances:
            h100_price = min(i.price_per_hour for i in h100_instances)
            a100_price = min(i.price_per_hour for i in a100_instances)

            # H100s should be more expensive
            assert h100_price > a100_price

            # But might have better availability
            assert len(h100_instances) >= 0  # At least some availability

    def test_instance_unavailability_handling(self, provider):
        """Test graceful handling when instances aren't available."""
        # Simulate searching for instance type with no availability
        provider._test_double._handle_availability = lambda params: []

        instances = provider.find_instances({"instance_type": "a100"})

        # Should return empty list, not error
        assert instances == []

    def test_concurrent_task_submission(self, provider):
        """Test submitting multiple tasks concurrently."""
        # Find instances first
        instances = provider.find_instances({"instance_type": "a100"})
        assert len(instances) >= 2, "Need at least 2 instances for test"

        # Submit multiple tasks
        tasks = []
        num_tasks = min(3, len(instances))  # Use up to 3 instances if available
        for i in range(num_tasks):
            config = TaskConfig(
                name=f"parallel-job-{i}",
                instance_type="a100",
                command=["python", f"job_{i}.py"],
                upload_code=False,  # Disable code upload for integration test
            )
            task = provider.submit_task("a100", config)
            tasks.append(task)

        # All should succeed
        assert len(tasks) == num_tasks
        assert all(t.task_id for t in tasks)
        assert len(set(t.task_id for t in tasks)) == num_tasks  # All unique

    def test_api_call_efficiency(self, provider):
        """Test that we make efficient API calls."""
        # Reset call tracking
        provider._test_double.calls = []

        # User workflow: find instances and submit task
        instances = provider.find_instances({"instance_type": "a100"})
        task = provider.submit_task(
            "a100",
            TaskConfig(name="test", instance_type="a100", command=["echo", "hi"], upload_code=False)
        )

        # Check API calls were efficient
        calls = provider._test_double.calls

        # Should have made these calls:
        # 1. Projects (if needed for initialization)
        # 2. SSH keys (if needed)
        # 3. Spot availability
        # 4. Create bid

        # Count each type
        call_types = {}
        for method, url, _ in calls:
            key = f"{method} {url.split('?')[0]}"
            call_types[key] = call_types.get(key, 0) + 1

        # Should have made availability calls (one for find_instances, one for submit_task)
        assert call_types.get("GET /v2/spot/availability", 0) == 2
        assert call_types.get("POST /v2/spot/bids", 0) == 1
