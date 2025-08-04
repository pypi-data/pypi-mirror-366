"""
Basic usage example for MOA SDK.

This example demonstrates:
- Client initialization
- Creating memories
- Searching memories
- Getting memory by ID
- Updating and deleting memories
- Error handling
"""

import os

from moa import Environment, MOAClient
from moa.exceptions import MOAAuthError, MOANotFoundError, MOAValidationError


def main():
    """Main example function."""
    # Initialize client with API key
    # You can set MOA_API_KEY environment variable or pass it directly
    api_key = os.getenv("MOA_API_KEY", "your-api-key-here")

    if api_key == "your-api-key-here":
        print(
            "Please set MOA_API_KEY environment variable or update the api_key variable"
        )
        return

    # Create client for beta environment
    client = MOAClient(
        api_key=api_key,
        environment=Environment.BETA,
        timeout=30.0,
        debug=True,  # Enable debug mode to see requests
    )

    try:
        # Test API connection
        print("Testing API connection...")
        health = client.health_check()
        print(f"API Status: {health.status}")

        # Create a memory
        print("\n1. Creating a memory...")
        memory_data = {
            "content": "Meeting with the development team about Q4 roadmap. Key points: API improvements, mobile app development, and user analytics dashboard.",
            "metadata": {
                "meeting_type": "roadmap_planning",
                "attendees": ["John", "Sarah", "Mike", "Lisa"],
                "duration_minutes": 60,
                "location": "Conference Room A",
            },
            "tags": ["meeting", "roadmap", "Q4", "development"],
            "retention_days": 365,
        }

        create_response = client.memory.create_memory(memory_data)
        memory_id = create_response.memory_id
        print(f"Created memory with ID: {memory_id}")

        # Create another memory for search demonstration
        print("\n2. Creating another memory...")
        memory_data_2 = {
            "content": "Product launch strategy discussion. Focus on marketing channels, pricing strategy, and launch timeline for new API features.",
            "metadata": {
                "meeting_type": "product_launch",
                "department": "marketing",
                "priority": "high",
            },
            "tags": ["product", "launch", "strategy", "marketing", "API"],
            "retention_days": 180,
        }

        create_response_2 = client.memory.create_memory(memory_data_2)
        memory_id_2 = create_response_2.memory_id
        print(f"Created memory with ID: {memory_id_2}")

        # Search memories
        print("\n3. Searching memories...")
        search_results = client.memory.search_memories(
            query="API development roadmap",
            max_results=10,
            vector_weight=0.6,  # Emphasize semantic similarity
            keyword_weight=0.4,  # Some keyword matching
            temporal_weight=0.1,  # Recent memories slightly preferred
        )

        print(f"Found {len(search_results.results)} memories:")
        for i, result in enumerate(search_results.results, 1):
            print(f"  {i}. Score: {result.score:.3f}")
            print(f"     Content: {result.memory.content[:100]}...")
            print(f"     Tags: {result.memory.tags}")
            if result.highlights:
                print(f"     Highlights: {result.highlights}")
            print()

        # Get memory by ID
        print("4. Getting memory by ID...")
        retrieved_memory = client.memory.get_memory(memory_id)
        print(f"Retrieved memory: {retrieved_memory.content[:50]}...")
        print(f"Created at: {retrieved_memory.created_at}")
        print(f"Access count: {retrieved_memory.access_count}")

        # Update memory
        print("\n5. Updating memory...")
        update_data = {
            "metadata": {
                **retrieved_memory.metadata,
                "updated_by": "admin",
                "last_review": "2024-01-15",
            },
            "tags": retrieved_memory.tags + ["reviewed"],
        }

        update_response = client.memory.update_memory(memory_id, update_data)
        print(f"Update status: {update_response.status}")

        # Get analytics
        print("\n6. Getting analytics...")
        analytics = client.memory.get_analytics()
        print(f"Total memories: {analytics.total_memories}")
        print(f"Memory size: {analytics.memory_size_bytes} bytes")

        # Search with filters (using tags)
        print("\n7. Searching with filters...")
        filtered_results = client.memory.search_memories(query="meeting", max_results=5)

        print(f"Found {len(filtered_results.results)} meetings:")
        for result in filtered_results.results:
            tags = result.memory.tags
            meeting_tags = [tag for tag in tags if "meeting" in tag.lower()]
            print(f"  - {result.memory.content[:60]}... (Tags: {meeting_tags})")

        # Clean up - delete created memories
        print("\n8. Cleaning up...")
        try:
            delete_response_1 = client.memory.delete_memory(memory_id)
            print(f"Deleted memory 1: {delete_response_1.status}")

            delete_response_2 = client.memory.delete_memory(memory_id_2)
            print(f"Deleted memory 2: {delete_response_2.status}")
        except MOANotFoundError:
            print("Memory already deleted or not found")

        print("\nExample completed successfully!")

    except MOAAuthError:
        print("Authentication failed. Please check your API key.")
    except MOAValidationError as e:
        print(f"Validation error: {e.message}")
        if e.details:
            print(f"Details: {e.details}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Always close the client to cleanup resources
        client.close()


if __name__ == "__main__":
    main()
