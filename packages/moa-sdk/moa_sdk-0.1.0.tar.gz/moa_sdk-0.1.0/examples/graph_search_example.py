"""
Advanced graph search example for MOA SDK.

This example demonstrates:
- Different graph search algorithms
- Relationship generation
- Graph optimization
- Relationship statistics
"""

import asyncio
import os

from moa import Environment, MOAClient
from moa.exceptions import MOAError


async def main():
    """Main async example function."""
    # Initialize client
    api_key = os.getenv("MOA_API_KEY", "your-api-key-here")

    if api_key == "your-api-key-here":
        print("Please set MOA_API_KEY environment variable")
        return

    async with MOAClient(api_key=api_key, environment=Environment.BETA) as client:
        try:
            print("=== MOA Graph Search Example ===\n")

            # First, create some memories to work with
            print("1. Creating sample memories for graph search...")
            memories = [
                {
                    "content": "Project Alpha is a machine learning initiative focused on natural language processing for customer service automation.",
                    "tags": ["project", "ml", "nlp", "customer-service"],
                    "metadata": {
                        "department": "engineering",
                        "priority": "high",
                        "status": "active",
                    },
                },
                {
                    "content": "Weekly team meeting discussed the roadmap for Project Alpha. Key decisions: adopt transformer architecture, integrate with existing CRM.",
                    "tags": ["meeting", "project", "roadmap", "architecture"],
                    "metadata": {
                        "meeting_type": "planning",
                        "project": "alpha",
                        "attendees": 8,
                    },
                },
                {
                    "content": "Research paper on transformer architectures for conversational AI. Potential application in Project Alpha's NLP components.",
                    "tags": ["research", "transformer", "conversational-ai", "nlp"],
                    "metadata": {
                        "source": "arxiv",
                        "relevance": "high",
                        "project": "alpha",
                    },
                },
                {
                    "content": "Customer feedback analysis shows 40% of support tickets could be automated using advanced NLP techniques.",
                    "tags": ["customer-feedback", "analysis", "automation", "nlp"],
                    "metadata": {
                        "data_source": "support_tickets",
                        "automation_potential": 40,
                    },
                },
                {
                    "content": "Integration plan for CRM system with new AI capabilities. Timeline: Q2 implementation, Q3 full rollout.",
                    "tags": ["integration", "crm", "ai", "timeline"],
                    "metadata": {
                        "timeline": "Q2-Q3",
                        "system": "CRM",
                        "type": "integration_plan",
                    },
                },
            ]

            memory_ids = []
            for i, memory_data in enumerate(memories, 1):
                response = await client.memory.acreate_memory(memory_data)
                memory_ids.append(response.memory_id)
                print(f"   Created memory {i}: {response.memory_id}")

            print(f"\nCreated {len(memory_ids)} memories for graph search demo.")

            # Generate relationships between memories
            print("\n2. Generating relationships between memories...")
            relationship_response = (
                await client.relationships.agenerate_relationships_for_memories(
                    memory_ids=memory_ids, force_regenerate=True, batch_size=5
                )
            )

            print(f"   Status: {relationship_response.status}")
            print(f"   Generated relationships: {relationship_response.stats}")
            print(f"   Processing time: {relationship_response.processing_time_ms}ms")

            # Get relationship statistics
            print("\n3. Getting relationship statistics...")
            stats = await client.relationships.aget_relationship_stats()
            print(f"   Total relationships: {stats.total_relationships}")
            print(f"   Average strength: {stats.average_strength:.3f}")
            print(f"   Relationship types: {stats.relationship_types}")
            print(f"   Graph density: {stats.graph_density:.3f}")

            # Demonstrate different graph search algorithms
            print("\n4. Demonstrating graph search algorithms...")

            # Shortest path search
            print("\n   4a. Shortest Path Search")
            print(
                "   Finding memories connected via shortest paths to 'machine learning project'"
            )
            shortest_path_results = await client.graph.asearch_shortest_path(
                query="machine learning project",
                max_depth=3,
                max_results=5,
                min_relationship_strength=0.2,
            )

            print(f"   Found {len(shortest_path_results.results)} results:")
            for i, result in enumerate(shortest_path_results.results, 1):
                print(f"     {i}. Score: {result.score:.3f}")
                print(f"        Content: {result.node.content[:80]}...")
                if result.path:
                    print(f"        Path length: {result.path.path_length}")
                    print(f"        Path strength: {result.path.total_strength:.3f}")
                print()

            # Similarity cluster search
            print("   4b. Similarity Cluster Search")
            print("   Finding semantic neighborhoods around 'NLP automation'")
            cluster_results = await client.graph.asearch_similarity_cluster(
                query="NLP automation",
                max_depth=2,
                max_results=5,
                min_concept_relevance=0.3,
            )

            print(f"   Found {len(cluster_results.results)} results in cluster:")
            for i, result in enumerate(cluster_results.results, 1):
                print(f"     {i}. Score: {result.score:.3f}")
                print(f"        Content: {result.node.content[:80]}...")
                print(f"        Tags: {result.node.tags}")
                print()

            # Concept traversal search
            print("   4c. Concept Traversal Search")
            print("   Exploring concept relationships around 'project management'")
            concept_results = await client.graph.asearch_concept_traversal(
                query="project management", max_depth=3, max_results=5
            )

            print(f"   Found {len(concept_results.results)} results:")
            for i, result in enumerate(concept_results.results, 1):
                print(f"     {i}. Score: {result.score:.3f}")
                print(f"        Content: {result.node.content[:80]}...")
                if result.related_nodes:
                    print(f"        Related nodes: {len(result.related_nodes)}")
                print()

            # Temporal flow search
            print("   4d. Temporal Flow Search")
            print("   Finding memories in temporal sequence for 'project timeline'")
            temporal_results = await client.graph.asearch_temporal_flow(
                query="project timeline",
                max_depth=3,
                max_results=5,
                weight_by_recency=True,
            )

            print(f"   Found {len(temporal_results.results)} results:")
            for i, result in enumerate(temporal_results.results, 1):
                print(f"     {i}. Score: {result.score:.3f}")
                print(f"        Content: {result.node.content[:80]}...")
                if hasattr(result, "explanation") and result.explanation:
                    print(f"        Explanation: {result.explanation}")
                print()

            # Get available search types
            print("\n5. Available graph search types:")
            search_types = await client.graph.aget_search_types()
            for search_type in search_types:
                print(f"   - {search_type.type_name}: {search_type.description}")

            # Optimize the graph
            print("\n6. Optimizing the relationship graph...")
            optimization_results = await client.relationships.aoptimize_graph(
                regenerate_relationships=False,  # We just generated them
                cleanup_threshold=0.1,
                batch_size=5,
            )

            if "cleanup" in optimization_results:
                cleanup = optimization_results["cleanup"]
                print(f"   Removed {cleanup['removed_count']} weak relationships")
                print(f"   Remaining: {cleanup['remaining_count']} relationships")

            if "final_stats" in optimization_results:
                final_stats = optimization_results["final_stats"]
                print(f"   Final graph density: {final_stats['graph_density']:.3f}")

            # Advanced search with filters
            print("\n7. Advanced search with relationship type filters...")
            filtered_results = await client.graph.agraph_search(
                {
                    "query": "customer service automation",
                    "search_type": "semantic_neighborhood",
                    "max_depth": 2,
                    "max_results": 3,
                    "include_relationship_types": [
                        "semantic_similarity",
                        "concept_related",
                    ],
                    "weight_by_access_frequency": True,
                    "boost_direct_connections": 2.0,
                }
            )

            print(f"   Found {len(filtered_results.results)} filtered results:")
            for i, result in enumerate(filtered_results.results, 1):
                print(f"     {i}. Score: {result.score:.3f}")
                print(f"        Content: {result.node.content[:80]}...")
                print()

            print(f"   Search execution time: {filtered_results.execution_time_ms}ms")
            print(f"   Graph stats: {filtered_results.graph_stats}")

            # Clean up - delete created memories
            print("\n8. Cleaning up created memories...")
            for memory_id in memory_ids:
                try:
                    await client.memory.adelete_memory(memory_id)
                except MOAError:
                    pass  # Memory might already be deleted

            print("   Cleanup completed.")

            print("\n=== Graph Search Example Completed Successfully! ===")

        except Exception as e:
            print(f"Error during graph search example: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
