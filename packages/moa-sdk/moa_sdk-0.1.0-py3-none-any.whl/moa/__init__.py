"""
MOA Python SDK - Memory Of Agents

A comprehensive Python SDK for interacting with the MOA (Memory Of Agents) API.
Provides revolutionary dual-track AI memory infrastructure with zero information loss.
"""

__version__ = "0.1.0"
__author__ = "MOA Team"
__email__ = "hello@memof.ai"

from .client import MOAClient
from .config import Config, Environment
from .exceptions import (
    MOAAPIError,
    MOAAuthError,
    MOAConnectionError,
    MOAError,
    MOATimeoutError,
    MOAValidationError,
)
from .models.graph import (
    GraphSearchRequest,
    GraphSearchResponse,
)

# Import main models for convenience
from .models.memory import (
    MemoryCreateRequest,
    MemoryResponse,
    MemoryUpdateRequest,
    SearchResponse,
)

__all__ = [
    # Main client
    "MOAClient",
    # Configuration
    "Environment",
    "Config",
    # Exceptions
    "MOAError",
    "MOAAPIError",
    "MOAAuthError",
    "MOAConnectionError",
    "MOATimeoutError",
    "MOAValidationError",
    # Models
    "MemoryCreateRequest",
    "MemoryUpdateRequest",
    "MemoryResponse",
    "SearchResponse",
    "GraphSearchRequest",
    "GraphSearchResponse",
]
