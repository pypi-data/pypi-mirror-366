"""Graph search API operations for MOA SDK."""

from typing import Any, Dict, List, Union

from ..models.graph import (
    GraphSearchRequest,
    GraphSearchResponse,
    GraphSearchType,
)
from ..utils.http import HTTPClient


class GraphSearchAPI:
    """Graph search operations API client."""

    def __init__(self, http_client: HTTPClient):
        """Initialize Graph Search API client."""
        self.http = http_client

    def graph_search(
        self, request: Union[GraphSearchRequest, Dict[str, Any]]
    ) -> GraphSearchResponse:
        """Perform advanced graph-based search on memories.

        Args:
            request: Graph search request data

        Returns:
            GraphSearchResponse: Graph search results
        """
        if isinstance(request, dict):
            request_data = request
        else:
            request_data = request.dict(exclude_unset=True)

        response_data = self.http.post("graph-search", json_data=request_data)
        return GraphSearchResponse(**response_data)

    async def agraph_search(
        self, request: Union[GraphSearchRequest, Dict[str, Any]]
    ) -> GraphSearchResponse:
        """Async perform advanced graph-based search on memories."""
        if isinstance(request, dict):
            request_data = request
        else:
            request_data = request.dict(exclude_unset=True)

        response_data = await self.http.apost("graph-search", json_data=request_data)
        return GraphSearchResponse(**response_data)

    def get_search_types(self) -> List[GraphSearchType]:
        """Get available graph search types and their descriptions.

        Returns:
            List[GraphSearchType]: Available search types
        """
        response_data = self.http.get("graph-search/types")
        return [
            GraphSearchType(**item) for item in response_data.get("search_types", [])
        ]

    async def aget_search_types(self) -> List[GraphSearchType]:
        """Async get available graph search types and their descriptions."""
        response_data = await self.http.aget("graph-search/types")
        return [
            GraphSearchType(**item) for item in response_data.get("search_types", [])
        ]

    def search_shortest_path(
        self,
        query: str,
        max_depth: int = 3,
        max_results: int = 20,
        min_relationship_strength: float = 0.3,
        **kwargs,
    ) -> GraphSearchResponse:
        """Find memories connected via shortest relationship paths.

        Args:
            query: Search query
            max_depth: Maximum search depth
            max_results: Maximum number of results
            min_relationship_strength: Minimum relationship strength
            **kwargs: Additional search parameters

        Returns:
            GraphSearchResponse: Search results
        """
        request = GraphSearchRequest(
            query=query,
            search_type="shortest_path",
            max_depth=max_depth,
            max_results=max_results,
            min_relationship_strength=min_relationship_strength,
            **kwargs,
        )
        return self.graph_search(request)

    async def asearch_shortest_path(
        self,
        query: str,
        max_depth: int = 3,
        max_results: int = 20,
        min_relationship_strength: float = 0.3,
        **kwargs,
    ) -> GraphSearchResponse:
        """Async find memories connected via shortest relationship paths."""
        request = GraphSearchRequest(
            query=query,
            search_type="shortest_path",
            max_depth=max_depth,
            max_results=max_results,
            min_relationship_strength=min_relationship_strength,
            **kwargs,
        )
        return await self.agraph_search(request)

    def search_similarity_cluster(
        self,
        query: str,
        max_depth: int = 2,
        max_results: int = 20,
        min_concept_relevance: float = 0.4,
        **kwargs,
    ) -> GraphSearchResponse:
        """Find semantic neighborhoods of similar memories.

        Args:
            query: Search query
            max_depth: Maximum search depth
            max_results: Maximum number of results
            min_concept_relevance: Minimum concept relevance
            **kwargs: Additional search parameters

        Returns:
            GraphSearchResponse: Search results
        """
        request = GraphSearchRequest(
            query=query,
            search_type="similarity_cluster",
            max_depth=max_depth,
            max_results=max_results,
            min_concept_relevance=min_concept_relevance,
            **kwargs,
        )
        return self.graph_search(request)

    async def asearch_similarity_cluster(
        self,
        query: str,
        max_depth: int = 2,
        max_results: int = 20,
        min_concept_relevance: float = 0.4,
        **kwargs,
    ) -> GraphSearchResponse:
        """Async find semantic neighborhoods of similar memories."""
        request = GraphSearchRequest(
            query=query,
            search_type="similarity_cluster",
            max_depth=max_depth,
            max_results=max_results,
            min_concept_relevance=min_concept_relevance,
            **kwargs,
        )
        return await self.agraph_search(request)

    def search_concept_traversal(
        self, query: str, max_depth: int = 3, max_results: int = 20, **kwargs
    ) -> GraphSearchResponse:
        """Search based on concept relationships.

        Args:
            query: Search query
            max_depth: Maximum search depth
            max_results: Maximum number of results
            **kwargs: Additional search parameters

        Returns:
            GraphSearchResponse: Search results
        """
        request = GraphSearchRequest(
            query=query,
            search_type="concept_traversal",
            max_depth=max_depth,
            max_results=max_results,
            **kwargs,
        )
        return self.graph_search(request)

    async def asearch_concept_traversal(
        self, query: str, max_depth: int = 3, max_results: int = 20, **kwargs
    ) -> GraphSearchResponse:
        """Async search based on concept relationships."""
        request = GraphSearchRequest(
            query=query,
            search_type="concept_traversal",
            max_depth=max_depth,
            max_results=max_results,
            **kwargs,
        )
        return await self.agraph_search(request)

    def search_temporal_flow(
        self,
        query: str,
        max_depth: int = 3,
        max_results: int = 20,
        weight_by_recency: bool = True,
        **kwargs,
    ) -> GraphSearchResponse:
        """Find memories in temporal sequence.

        Args:
            query: Search query
            max_depth: Maximum search depth
            max_results: Maximum number of results
            weight_by_recency: Weight results by recency
            **kwargs: Additional search parameters

        Returns:
            GraphSearchResponse: Search results
        """
        request = GraphSearchRequest(
            query=query,
            search_type="temporal_flow",
            max_depth=max_depth,
            max_results=max_results,
            weight_by_recency=weight_by_recency,
            **kwargs,
        )
        return self.graph_search(request)

    async def asearch_temporal_flow(
        self,
        query: str,
        max_depth: int = 3,
        max_results: int = 20,
        weight_by_recency: bool = True,
        **kwargs,
    ) -> GraphSearchResponse:
        """Async find memories in temporal sequence."""
        request = GraphSearchRequest(
            query=query,
            search_type="temporal_flow",
            max_depth=max_depth,
            max_results=max_results,
            weight_by_recency=weight_by_recency,
            **kwargs,
        )
        return await self.agraph_search(request)

    def search_causal_chain(
        self, query: str, max_depth: int = 4, max_results: int = 20, **kwargs
    ) -> GraphSearchResponse:
        """Discover causal relationships between memories.

        Args:
            query: Search query
            max_depth: Maximum search depth
            max_results: Maximum number of results
            **kwargs: Additional search parameters

        Returns:
            GraphSearchResponse: Search results
        """
        request = GraphSearchRequest(
            query=query,
            search_type="causal_chain",
            max_depth=max_depth,
            max_results=max_results,
            **kwargs,
        )
        return self.graph_search(request)

    async def asearch_causal_chain(
        self, query: str, max_depth: int = 4, max_results: int = 20, **kwargs
    ) -> GraphSearchResponse:
        """Async discover causal relationships between memories."""
        request = GraphSearchRequest(
            query=query,
            search_type="causal_chain",
            max_depth=max_depth,
            max_results=max_results,
            **kwargs,
        )
        return await self.agraph_search(request)
