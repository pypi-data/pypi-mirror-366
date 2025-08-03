"""Async test utilities for Flow SDK.

Provides utilities for testing asynchronous code patterns, including
fixtures, helpers, and mock objects for async operations.
"""

import asyncio
import contextlib
import functools
import time
from typing import Any, AsyncContextManager, AsyncIterator, Callable, Optional, TypeVar
from unittest.mock import AsyncMock, Mock

import pytest


T = TypeVar("T")


# Async test decorators
def async_test(timeout: float = 5.0):
    """Decorator for async test functions with automatic timeout."""
    def decorator(func):
        @functools.wraps(func)
        @pytest.mark.asyncio
        @pytest.mark.timeout(timeout)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Async fixtures
@pytest.fixture
async def async_client():
    """Fixture providing a mock async HTTP client."""
    client = AsyncMock()
    # Common response patterns
    client.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value={}))
    client.post.return_value = AsyncMock(status=201, json=AsyncMock(return_value={}))
    client.delete.return_value = AsyncMock(status=204)
    return client


@pytest.fixture
async def event_loop():
    """Provide a new event loop for each test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Cleanup pending tasks
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.close()


# Async context managers
@contextlib.asynccontextmanager
async def async_timeout(seconds: float) -> AsyncIterator[None]:
    """Async context manager for timing out operations."""
    async def timeout_handler():
        await asyncio.sleep(seconds)
        raise asyncio.TimeoutError(f"Operation timed out after {seconds} seconds")
    
    task = asyncio.create_task(timeout_handler())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass


@contextlib.asynccontextmanager
async def measure_async_time() -> AsyncIterator[dict]:
    """Measure execution time of async operations."""
    metrics = {"start": time.time(), "end": None, "duration": None}
    yield metrics
    metrics["end"] = time.time()
    metrics["duration"] = metrics["end"] - metrics["start"]


# Async test helpers
async def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 5.0,
    interval: float = 0.1,
    message: Optional[str] = None
) -> None:
    """Wait for a condition to become true."""
    start_time = time.time()
    while not condition():
        if time.time() - start_time > timeout:
            msg = message or f"Condition not met within {timeout} seconds"
            raise asyncio.TimeoutError(msg)
        await asyncio.sleep(interval)


async def async_retry(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry an async function with exponential backoff."""
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_attempts):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                await asyncio.sleep(current_delay)
                current_delay *= backoff
    
    raise last_exception


async def gather_with_timeout(
    *coros,
    timeout: float = 5.0,
    return_exceptions: bool = False
) -> list:
    """Gather multiple coroutines with a shared timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.gather(*coros, return_exceptions=return_exceptions),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        # Cancel all pending coroutines
        for coro in coros:
            if hasattr(coro, "cancel"):
                coro.cancel()
        raise


# Mock async iterators
class AsyncIteratorMock:
    """Mock for async iterators."""
    
    def __init__(self, items: list):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


# Async stream helpers
class AsyncStreamMock:
    """Mock for async streams (e.g., WebSocket, SSE)."""
    
    def __init__(self):
        self.messages = []
        self.closed = False
        self._queue = asyncio.Queue()
    
    async def send(self, message: Any) -> None:
        """Send a message to the stream."""
        if self.closed:
            raise RuntimeError("Stream is closed")
        self.messages.append(("send", message))
        await self._queue.put(message)
    
    async def receive(self) -> Any:
        """Receive a message from the stream."""
        if self.closed and self._queue.empty():
            raise RuntimeError("Stream is closed")
        return await self._queue.get()
    
    async def close(self) -> None:
        """Close the stream."""
        self.closed = True
        self.messages.append(("close", None))


# Async test assertions
async def assert_async_raises(exception_type: type, coro: Any) -> Any:
    """Assert that an async function raises a specific exception."""
    with pytest.raises(exception_type) as exc_info:
        await coro
    return exc_info


async def assert_completes_within(coro: Any, seconds: float) -> Any:
    """Assert that an async operation completes within a time limit."""
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        pytest.fail(f"Coroutine did not complete within {seconds} seconds")


# Background task helpers
class BackgroundTaskRunner:
    """Helper for managing background tasks in tests."""
    
    def __init__(self):
        self.tasks = []
    
    def run(self, coro: Any) -> asyncio.Task:
        """Start a background task."""
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return task
    
    async def cleanup(self) -> None:
        """Cancel and cleanup all background tasks."""
        for task in self.tasks:
            task.cancel()
        
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()


# Async queue helpers
class AsyncQueueMock:
    """Enhanced async queue for testing."""
    
    def __init__(self, maxsize: int = 0):
        self.queue = asyncio.Queue(maxsize=maxsize)
        self.put_count = 0
        self.get_count = 0
        self.history = []
    
    async def put(self, item: Any) -> None:
        """Put an item in the queue."""
        await self.queue.put(item)
        self.put_count += 1
        self.history.append(("put", item))
    
    async def get(self) -> Any:
        """Get an item from the queue."""
        item = await self.queue.get()
        self.get_count += 1
        self.history.append(("get", item))
        return item
    
    def qsize(self) -> int:
        """Get current queue size."""
        return self.queue.qsize()
    
    def empty(self) -> bool:
        """Check if queue is empty."""
        return self.queue.empty()
    
    def full(self) -> bool:
        """Check if queue is full."""
        return self.queue.full()


# Concurrency testing helpers
async def run_concurrent(
    func: Callable[..., Any],
    args_list: list,
    max_concurrent: Optional[int] = None
) -> list:
    """Run a function concurrently with different arguments."""
    if max_concurrent is None:
        # Run all at once
        return await asyncio.gather(
            *[func(*args) for args in args_list]
        )
    
    # Run with concurrency limit
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_run(args):
        async with semaphore:
            return await func(*args)
    
    return await asyncio.gather(
        *[limited_run(args) for args in args_list]
    )


# Event simulation
class EventSimulator:
    """Simulate async events for testing."""
    
    def __init__(self):
        self.events = []
        self._listeners = {}
    
    def on(self, event_name: str, handler: Callable) -> None:
        """Register an event handler."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(handler)
    
    async def emit(self, event_name: str, data: Any = None) -> None:
        """Emit an event to all listeners."""
        self.events.append((event_name, data))
        
        if event_name in self._listeners:
            await asyncio.gather(
                *[handler(data) for handler in self._listeners[event_name]]
            )
    
    def clear(self) -> None:
        """Clear all events and listeners."""
        self.events.clear()
        self._listeners.clear()