"""Base models for MOA SDK."""

from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, ConfigDict, Field
except ImportError:
    # Fallback for when pydantic is not installed during development
    class BaseModel:
        pass

    def Field(*args, **kwargs):
        return None

    def ConfigDict(*args, **kwargs):
        return None


class MOABaseModel(BaseModel):
    """Base model for all MOA API models."""

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )


class ErrorDetail(MOABaseModel):
    """Model for error details in API responses."""

    loc: List[str] = Field(..., description="Error location")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class HTTPValidationError(MOABaseModel):
    """Model for HTTP validation errors."""

    detail: List[ErrorDetail] = Field(..., description="Validation error details")


class PaginationInfo(MOABaseModel):
    """Model for pagination information."""

    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class BaseResponse(MOABaseModel):
    """Base response model."""

    status: str = Field(..., description="Response status")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: Optional[datetime] = Field(None, description="Response timestamp")


class HealthResponse(MOABaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: Optional[str] = Field(None, description="API version")
    uptime: Optional[float] = Field(None, description="Uptime in seconds")


class AnalyticsResponse(MOABaseModel):
    """Analytics response model."""

    total_memories: int = Field(..., description="Total number of memories")
    memory_size_bytes: int = Field(..., description="Total memory size in bytes")
    last_activity: Optional[datetime] = Field(
        None, description="Last activity timestamp"
    )
    search_stats: Dict[str, Any] = Field(
        default_factory=dict, description="Search statistics"
    )
    graph_stats: Dict[str, Any] = Field(
        default_factory=dict, description="Graph statistics"
    )
