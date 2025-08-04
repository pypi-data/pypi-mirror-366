"""Memory API operations for MOA SDK."""

from typing import Any, Dict, Optional, Union

from ..models.base import AnalyticsResponse
from ..models.memory import (
    BulkMemoryOperation,
    BulkMemoryResponse,
    Memory,
    MemoryCreateRequest,
    MemoryResponse,
    MemoryUpdateRequest,
    SearchFilters,
    SearchResponse,
)
from ..utils.http import HTTPClient


class MemoryAPI:
    """Memory operations API client."""

    def __init__(self, http_client: HTTPClient):
        """Initialize Memory API client."""
        self.http = http_client

    def create_memory(
        self, request: Union[MemoryCreateRequest, Dict[str, Any]]
    ) -> MemoryResponse:
        """Create a new memory.

        Args:
            request: Memory creation request data

        Returns:
            MemoryResponse: Created memory response
        """
        if isinstance(request, dict):
            request_data = request
        else:
            request_data = request.dict(exclude_unset=True)

        response_data = self.http.post("memories", json_data=request_data)
        return MemoryResponse(**response_data)

    async def acreate_memory(
        self, request: Union[MemoryCreateRequest, Dict[str, Any]]
    ) -> MemoryResponse:
        """Async create a new memory."""
        if isinstance(request, dict):
            request_data = request
        else:
            request_data = request.dict(exclude_unset=True)

        response_data = await self.http.apost("memories", json_data=request_data)
        return MemoryResponse(**response_data)

    def get_memory(self, memory_id: str) -> Memory:
        """Get a specific memory by ID.

        Args:
            memory_id: Unique memory identifier

        Returns:
            Memory: Memory object
        """
        response_data = self.http.get(f"memories/{memory_id}")
        return Memory(**response_data)

    async def aget_memory(self, memory_id: str) -> Memory:
        """Async get a specific memory by ID."""
        response_data = await self.http.aget(f"memories/{memory_id}")
        return Memory(**response_data)

    def update_memory(
        self, memory_id: str, request: Union[MemoryUpdateRequest, Dict[str, Any]]
    ) -> MemoryResponse:
        """Update an existing memory.

        Args:
            memory_id: Unique memory identifier
            request: Memory update request data

        Returns:
            MemoryResponse: Updated memory response
        """
        if isinstance(request, dict):
            request_data = request
        else:
            request_data = request.dict(exclude_unset=True)

        response_data = self.http.put(f"memories/{memory_id}", json_data=request_data)
        return MemoryResponse(**response_data)

    async def aupdate_memory(
        self, memory_id: str, request: Union[MemoryUpdateRequest, Dict[str, Any]]
    ) -> MemoryResponse:
        """Async update an existing memory."""
        if isinstance(request, dict):
            request_data = request
        else:
            request_data = request.dict(exclude_unset=True)

        response_data = await self.http.aput(
            f"memories/{memory_id}", json_data=request_data
        )
        return MemoryResponse(**response_data)

    def delete_memory(self, memory_id: str) -> MemoryResponse:
        """Delete a memory.

        Args:
            memory_id: Unique memory identifier

        Returns:
            MemoryResponse: Deletion response
        """
        response_data = self.http.delete(f"memories/{memory_id}")
        return MemoryResponse(**response_data)

    async def adelete_memory(self, memory_id: str) -> MemoryResponse:
        """Async delete a memory."""
        response_data = await self.http.adelete(f"memories/{memory_id}")
        return MemoryResponse(**response_data)

    def search_memories(
        self,
        query: str,
        filters: Optional[Union[SearchFilters, Dict[str, Any]]] = None,
        vector_weight: float = 0.4,
        keyword_weight: float = 0.3,
        fuzzy_weight: float = 0.15,
        temporal_weight: float = 0.1,
        metadata_weight: float = 0.05,
        max_results: int = 10,
    ) -> SearchResponse:
        """Search memories using hybrid approach.

        Args:
            query: Search query string
            filters: Optional search filters
            vector_weight: Weight for vector similarity
            keyword_weight: Weight for keyword matching
            fuzzy_weight: Weight for fuzzy matching
            temporal_weight: Weight for temporal relevance
            metadata_weight: Weight for metadata matching
            max_results: Maximum number of results

        Returns:
            SearchResponse: Search results
        """
        params = {
            "query": query,
            "vector_weight": vector_weight,
            "keyword_weight": keyword_weight,
            "fuzzy_weight": fuzzy_weight,
            "temporal_weight": temporal_weight,
            "metadata_weight": metadata_weight,
            "max_results": max_results,
        }

        if filters:
            if isinstance(filters, dict):
                params["filters"] = str(filters)
            else:
                params["filters"] = filters.json()

        response_data = self.http.get("memories/search", params=params)
        return SearchResponse(**response_data)

    async def asearch_memories(
        self,
        query: str,
        filters: Optional[Union[SearchFilters, Dict[str, Any]]] = None,
        vector_weight: float = 0.4,
        keyword_weight: float = 0.3,
        fuzzy_weight: float = 0.15,
        temporal_weight: float = 0.1,
        metadata_weight: float = 0.05,
        max_results: int = 10,
    ) -> SearchResponse:
        """Async search memories using hybrid approach."""
        params = {
            "query": query,
            "vector_weight": vector_weight,
            "keyword_weight": keyword_weight,
            "fuzzy_weight": fuzzy_weight,
            "temporal_weight": temporal_weight,
            "metadata_weight": metadata_weight,
            "max_results": max_results,
        }

        if filters:
            if isinstance(filters, dict):
                params["filters"] = str(filters)
            else:
                params["filters"] = filters.json()

        response_data = await self.http.aget("memories/search", params=params)
        return SearchResponse(**response_data)

    def get_analytics(self) -> AnalyticsResponse:
        """Get memory analytics.

        Returns:
            AnalyticsResponse: Analytics data
        """
        response_data = self.http.get("memories/analytics")
        return AnalyticsResponse(**response_data)

    async def aget_analytics(self) -> AnalyticsResponse:
        """Async get memory analytics."""
        response_data = await self.http.aget("memories/analytics")
        return AnalyticsResponse(**response_data)

    def bulk_operation(
        self, operation: Union[BulkMemoryOperation, Dict[str, Any]]
    ) -> BulkMemoryResponse:
        """Perform bulk operations on memories.

        Args:
            operation: Bulk operation request

        Returns:
            BulkMemoryResponse: Bulk operation response
        """
        if isinstance(operation, dict):
            operation_data = operation
        else:
            operation_data = operation.dict(exclude_unset=True)

        response_data = self.http.post("memories/bulk", json_data=operation_data)
        return BulkMemoryResponse(**response_data)

    async def abulk_operation(
        self, operation: Union[BulkMemoryOperation, Dict[str, Any]]
    ) -> BulkMemoryResponse:
        """Async perform bulk operations on memories."""
        if isinstance(operation, dict):
            operation_data = operation
        else:
            operation_data = operation.dict(exclude_unset=True)

        response_data = await self.http.apost("memories/bulk", json_data=operation_data)
        return BulkMemoryResponse(**response_data)
