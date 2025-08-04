"""Test configuration for MOA SDK."""

from unittest.mock import MagicMock

import pytest

# Mock external dependencies for testing
try:
    import httpx
except ImportError:
    httpx = MagicMock()

try:
    import pydantic
except ImportError:
    pydantic = MagicMock()


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def mock_config_env(mock_api_key, monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("MOA_API_KEY", mock_api_key)
    monkeypatch.setenv("MOA_ENVIRONMENT", "beta")
    monkeypatch.setenv("MOA_API_VERSION", "v1")
    monkeypatch.setenv("MOA_TIMEOUT", "30.0")
    monkeypatch.setenv("MOA_MAX_RETRIES", "3")


@pytest.fixture
def sample_memory_data():
    """Sample memory data for testing."""
    return {
        "content": "This is a test memory for unit testing",
        "metadata": {"source": "test", "category": "unit-test"},
        "tags": ["test", "memory", "sample"],
        "retention_days": 30,
    }


@pytest.fixture
def sample_search_response():
    """Sample search response for testing."""
    return {
        "results": [
            {
                "memory": {
                    "memory_id": "test-memory-1",
                    "content": "First test memory",
                    "metadata": {},
                    "tags": ["test"],
                    "created_at": "2023-01-01T00:00:00Z",
                    "access_count": 0,
                    "retention_days": 30,
                },
                "score": 0.95,
                "highlights": {"content": ["test memory"]},
                "explanation": "High relevance match",
            }
        ],
        "total_results": 1,
        "search_time_ms": 45.2,
        "search_config": {
            "vector_weight": 0.4,
            "keyword_weight": 0.3,
            "fuzzy_weight": 0.15,
            "temporal_weight": 0.1,
            "metadata_weight": 0.05,
        },
    }


@pytest.fixture
def sample_graph_search_response():
    """Sample graph search response for testing."""
    return {
        "results": [
            {
                "node": {
                    "memory_id": "test-node-1",
                    "content": "Graph node content",
                    "metadata": {},
                    "tags": ["graph", "test"],
                    "node_type": "memory",
                },
                "score": 0.88,
                "path": {
                    "nodes": ["start-node", "test-node-1"],
                    "relationships": [],
                    "total_strength": 0.75,
                    "path_length": 1,
                    "path_type": "shortest",
                },
                "related_nodes": [],
                "metadata": {},
            }
        ],
        "total_results": 1,
        "search_type": "shortest_path",
        "execution_time_ms": 120,
        "graph_stats": {"total_nodes": 100, "total_edges": 250},
        "search_config": {"max_depth": 3, "min_strength": 0.3},
    }
