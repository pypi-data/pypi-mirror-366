"""
Sovant Python SDK

Official Python library for the Sovant Memory API.
"""

__version__ = "1.0.0"

from .client import SovantClient, AsyncSovantClient
from .exceptions import (
    SovantError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    NetworkError,
)
from .types import (
    Memory,
    MemoryType,
    EmotionType,
    EmotionalContext,
    CreateMemoryInput,
    UpdateMemoryInput,
    SearchOptions,
    SearchResult,
    Thread,
    ThreadStatus,
    CreateThreadInput,
    UpdateThreadInput,
    ThreadStats,
    BatchCreateResult,
    PaginatedResponse,
)

__all__ = [
    # Client classes
    "SovantClient",
    "AsyncSovantClient",
    # Exceptions
    "SovantError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "NetworkError",
    # Types
    "Memory",
    "MemoryType",
    "EmotionType",
    "EmotionalContext",
    "CreateMemoryInput",
    "UpdateMemoryInput",
    "SearchOptions",
    "SearchResult",
    "Thread",
    "ThreadStatus",
    "CreateThreadInput",
    "UpdateThreadInput",
    "ThreadStats",
    "BatchCreateResult",
    "PaginatedResponse",
]