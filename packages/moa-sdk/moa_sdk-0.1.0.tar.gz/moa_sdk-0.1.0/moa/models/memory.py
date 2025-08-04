"""Memory-related models for MOA SDK."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import MOABaseModel

try:
    from pydantic import Field
except ImportError:

    def Field(*args, **kwargs):
        return None


class MemoryCreateRequest(MOABaseModel):
    """Request model for creating a memory."""

    content: str = Field(
        ..., min_length=1, max_length=100000, description="Memory content"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Memory metadata")
    tags: Optional[List[str]] = Field(None, description="Memory tags")
    retention_days: int = Field(30, description="Retention period in days")


class MemoryUpdateRequest(MOABaseModel):
    """Request model for updating a memory."""

    content: Optional[str] = Field(
        None, min_length=1, max_length=100000, description="Updated memory content"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Updated memory metadata"
    )
    tags: Optional[List[str]] = Field(None, description="Updated memory tags")


class MemoryResponse(MOABaseModel):
    """Response model for memory operations."""

    memory_id: str = Field(..., description="Unique memory identifier")
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Response message")


class Memory(MOABaseModel):
    """Full memory object model."""

    memory_id: str = Field(..., description="Unique memory identifier")
    content: str = Field(..., description="Memory content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Memory metadata"
    )
    tags: List[str] = Field(default_factory=list, description="Memory tags")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    accessed_at: Optional[datetime] = Field(None, description="Last access timestamp")
    access_count: int = Field(0, description="Number of times accessed")
    retention_days: int = Field(30, description="Retention period in days")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class SearchResult(MOABaseModel):
    """Individual search result model."""

    memory: Memory = Field(..., description="Memory object")
    score: float = Field(..., description="Relevance score")
    highlights: Optional[Dict[str, List[str]]] = Field(
        None, description="Search highlights"
    )
    explanation: Optional[str] = Field(None, description="Score explanation")


class SearchResponse(MOABaseModel):
    """Response model for memory search operations."""

    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of matching results")
    search_time_ms: float = Field(
        ..., description="Search execution time in milliseconds"
    )
    search_config: Dict[str, float] = Field(
        ..., description="Search configuration used"
    )


class SearchFilters(MOABaseModel):
    """Search filters for memory queries."""

    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    date_from: Optional[datetime] = Field(
        None, description="Filter memories from this date"
    )
    date_to: Optional[datetime] = Field(
        None, description="Filter memories until this date"
    )
    metadata_filters: Optional[Dict[str, Any]] = Field(
        None, description="Metadata filters"
    )
    content_type: Optional[str] = Field(None, description="Filter by content type")
    min_score: Optional[float] = Field(None, description="Minimum relevance score")


class BulkMemoryOperation(MOABaseModel):
    """Bulk operation request model."""

    memory_ids: List[str] = Field(..., description="List of memory IDs")
    operation: str = Field(..., description="Operation type (delete, update, etc.)")
    data: Optional[Dict[str, Any]] = Field(None, description="Operation data")


class BulkMemoryResponse(MOABaseModel):
    """Bulk operation response model."""

    success_count: int = Field(..., description="Number of successful operations")
    failure_count: int = Field(..., description="Number of failed operations")
    total_count: int = Field(..., description="Total number of operations")
    failures: List[Dict[str, Any]] = Field(
        default_factory=list, description="Failed operations details"
    )
    execution_time_ms: float = Field(
        ..., description="Total execution time in milliseconds"
    )
