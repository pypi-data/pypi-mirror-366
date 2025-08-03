"""Task resolution utilities for Flow CLI.

This module provides intelligent task resolution that accepts either
task IDs or task names, following the principle of least surprise.
When ambiguous, it fails fast with helpful guidance.

Design principles:
- Exact ID match always wins (no ambiguity)
- Name prefix matching for convenience
- Clear error messages for ambiguous cases
- Zero magic, predictable behavior
"""

from typing import List, Optional, Tuple

from flow import Flow
from flow.api.models import Task
from .task_fetcher import TaskFetcher
from .task_index_cache import TaskIndexCache


def resolve_task_identifier(
    flow_client: Flow, identifier: str, require_unique: bool = True
) -> Tuple[Optional[Task], Optional[str]]:
    """Resolve a task identifier to a Task object.

    Resolution order:
    1. Index reference (e.g., :1, :2)
    2. Direct get_task() lookup (for exact task IDs)
    3. Exact task_id match from list
    4. Exact name match
    5. Prefix match on task_id
    6. Prefix match on name

    Args:
        flow_client: Flow API client
        identifier: Task ID, name, or index reference to resolve
        require_unique: If True, fail on ambiguous matches

    Returns:
        Tuple of (Task if found, error message if any)
    """
    # Check for index reference first (e.g., :1, :2)
    if identifier.startswith(":"):
        cache = TaskIndexCache()
        task_id, error = cache.resolve_index(identifier)
        if error:
            return None, error
        if task_id:
            # Resolve the cached task ID
            identifier = task_id

    # Try direct lookup first - this is the 80/20 optimization
    # Most users will provide exact task IDs
    try:
        task = flow_client.get_task(identifier)
        return task, None
    except Exception:
        # Not a valid task ID or doesn't exist - continue with list-based search
        pass

    # Use centralized task fetcher for consistent behavior
    task_fetcher = TaskFetcher(flow_client)
    all_tasks = task_fetcher.fetch_for_resolution()

    # 1. Exact task_id match
    for task in all_tasks:
        if task.task_id == identifier:
            return task, None

    # 2. Exact name match
    name_matches = [t for t in all_tasks if t.name == identifier]
    if len(name_matches) == 1:
        return name_matches[0], None
    elif len(name_matches) > 1:
        return None, _format_ambiguous_error(identifier, name_matches, "name")

    # 3. Prefix match on task_id
    id_prefix_matches = [t for t in all_tasks if t.task_id.startswith(identifier)]
    if len(id_prefix_matches) == 1:
        return id_prefix_matches[0], None
    elif len(id_prefix_matches) > 1 and require_unique:
        return None, _format_ambiguous_error(identifier, id_prefix_matches, "ID prefix")

    # 4. Prefix match on name
    name_prefix_matches = [t for t in all_tasks if t.name and t.name.startswith(identifier)]
    if len(name_prefix_matches) == 1:
        return name_prefix_matches[0], None
    elif len(name_prefix_matches) > 1 and require_unique:
        return None, _format_ambiguous_error(identifier, name_prefix_matches, "name prefix")

    # No matches - provide helpful error message
    error_msg = f"No task found matching '{identifier}'"

    # Add helpful suggestions based on the identifier format
    suggestions = []

    # If it looks like a task ID, suggest checking status
    if identifier.startswith("task-") or len(identifier) > 20:
        suggestions.extend(
            [
                "Task may still be initializing. Try again in a few seconds.",
                "Verify the task ID is correct.",
            ]
        )

    suggestions.append("Use 'flow status' to see all tasks.")
    suggestions.append("After running 'flow status', use index shortcuts like :1, :2, :3, etc.")

    error_msg += "\n\nSuggestions:"
    for i, suggestion in enumerate(suggestions, 1):
        error_msg += f"\n  {i}. {suggestion}"

    return None, error_msg


def _format_ambiguous_error(identifier: str, matches: List[Task], match_type: str) -> str:
    """Format an error message for ambiguous matches."""
    lines = [f"Multiple tasks match {match_type} '{identifier}':"]
    for task in matches[:5]:  # Show max 5
        # Only show task ID if it's not a bid ID
        if task.task_id and not task.task_id.startswith("bid_"):
            lines.append(f"  - {task.name or 'unnamed'} ({task.task_id})")
        else:
            lines.append(f"  - {task.name or 'unnamed'}")
    if len(matches) > 5:
        lines.append(f"  ... and {len(matches) - 5} more")
    lines.append("\nUse a more specific identifier or the full task ID")
    return "\n".join(lines)
