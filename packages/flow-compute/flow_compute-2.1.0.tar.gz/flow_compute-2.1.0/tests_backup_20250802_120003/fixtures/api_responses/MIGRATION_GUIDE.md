# API Response Fixtures Migration Guide

This guide explains how to migrate from hardcoded API responses to using the new fixture system.

## Benefits of Using Fixtures

1. **Maintainability**: Update responses in one place
2. **Consistency**: Same response data across all tests
3. **Readability**: Tests focus on logic, not data setup
4. **Reusability**: Share common responses between tests
5. **Type Safety**: Fixtures provide consistent structure

## Migration Steps

### 1. Import the Fixture Module

```python
from tests.fixtures.api_responses import fcp_responses
```

### 2. Replace Hardcoded Responses

#### Before:
```python
def test_project_response():
    api_response = {
        "fid": "proj-abc123",
        "name": "my-project",
        "created_at": "2024-01-15T10:30:00Z"
    }
    # test code...
```

#### After:
```python
def test_project_response():
    api_response = fcp_responses.project_success
    # test code...
```

### 3. Use with Mocks

#### Before:
```python
mock_client.get_task.return_value = {
    "task_id": "task-123",
    "status": "running",
    "instance_type": "gpu.nvidia.a100",
    # ... many more fields
}
```

#### After:
```python
mock_client.get_task.return_value = fcp_responses.task_running
```

### 4. Create Custom Responses

When you need a response with specific values:

```python
# Create custom task
custom_task = fcp_responses.custom_task(
    task_id="my-task-123",
    status="failed",
    error="Out of memory"
)

# Create custom volume
custom_volume = fcp_responses.custom_volume(
    fid="vol-custom",
    size_gb=5000
)

# Create custom error
custom_error = fcp_responses.custom_error(
    code="QUOTA_EXCEEDED",
    message="GPU quota exceeded"
)
```

## Available Fixtures

### Projects
- `fcp_responses.project_success`

### Instance Types
- `fcp_responses.instance_type_gpu_single`
- `fcp_responses.instance_type_gpu_multi`
- `fcp_responses.instance_type_cpu_only`

### Auctions & Bids
- `fcp_responses.auction_available`
- `fcp_responses.bid_pending`
- `fcp_responses.bid_won`
- `fcp_responses.bid_lost`
- `fcp_responses.bid_expired`

### Volumes
- `fcp_responses.volume_available`
- `fcp_responses.volume_file_share`
- `fcp_responses.volume_attached`

### Tasks
- `fcp_responses.task_created`
- `fcp_responses.task_running`
- `fcp_responses.task_completed`
- `fcp_responses.task_failed`

### Errors
- `fcp_responses.error_validation`
- `fcp_responses.error_not_found`
- `fcp_responses.error_rate_limit`
- `fcp_responses.error_server`

### Lists
- `fcp_responses.allocations_list`
- `fcp_responses.large_task_list`

## Adding New Fixtures

1. Edit `tests/fixtures/api_responses/fcp_responses.json`
2. Add your response under the appropriate category
3. Add a property method in `tests/fixtures/api_responses/__init__.py`

Example:
```python
@property
def my_new_response(self) -> Dict[str, Any]:
    """Description of the response."""
    return _load_fcp_responses()["category"]["my_new_response"].copy()
```

## Best Practices

1. **Always use `.copy()`**: Fixtures return copies to prevent test interference
2. **Group related responses**: Keep similar responses together in the JSON
3. **Document fixtures**: Add docstrings explaining what each fixture represents
4. **Use custom methods**: For variations, use `custom_*` methods instead of modifying fixtures
5. **Keep fixtures minimal**: Include only necessary fields for most tests

## Example Migration

Here's a complete example of migrating a test file:

### Before:
```python
class TestTaskOperations:
    def test_create_task(self):
        mock_response = Mock()
        mock_response.json.return_value = {
            "bid_id": "bid-123",
            "task_id": "task-456"
        }
        # ... test code
    
    def test_task_status(self):
        response_data = {
            "task_id": "task-123",
            "name": "test-task",
            "status": "running",
            "instance_type": "gpu.nvidia.a100",
            "region": "us-central1",
            "created_at": "2024-01-15T14:00:00Z",
            "logs": "Starting...",
            # ... many more fields
        }
        # ... test code
```

### After:
```python
from tests.fixtures.api_responses import fcp_responses

class TestTaskOperations:
    def test_create_task(self):
        mock_response = Mock()
        mock_response.json.return_value = fcp_responses.task_created
        # ... test code
    
    def test_task_status(self):
        response_data = fcp_responses.task_running
        # ... test code
```

The migrated version is cleaner, more maintainable, and ensures consistency across tests.