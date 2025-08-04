#!/usr/bin/env python3
"""
MCP Usage Examples

This script demonstrates various ways to use the MCP server
for querying the vector database.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vector_db_query.mcp_integration import (
    TokenManager,
    MCPTestClient,
    SecurityValidator,
    InputSanitizer,
)


# Example 1: Basic Query
async def example_basic_query():
    """Simple query example."""
    print("\n=== Example 1: Basic Query ===")
    
    client = MCPTestClient()
    
    # Simulate a basic query
    result = await client.test_query_vectors(
        query="What is machine learning?",
        limit=3
    )
    
    print(f"Query: {result.test_name}")
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms:.2f}ms")
    
    if result.response:
        print(f"Results found: {result.response['total']}")
        for i, res in enumerate(result.response['results'], 1):
            print(f"\n{i}. Score: {res['score']:.3f}")
            print(f"   Content: {res['content'][:100]}...")


# Example 2: Advanced Query with Filters
async def example_advanced_query():
    """Query with filters and threshold."""
    print("\n=== Example 2: Advanced Query ===")
    
    # Example query parameters
    query_params = {
        "query": "database optimization techniques",
        "limit": 5,
        "threshold": 0.7,
        "filters": {
            "category": "technical",
            "year": 2024
        }
    }
    
    print(f"Query Parameters:")
    print(json.dumps(query_params, indent=2))
    
    # Validate inputs
    validator = SecurityValidator()
    try:
        validated_query = validator.validate_query(query_params["query"])
        validated_filters = validator.validate_filters(query_params["filters"])
        print("\n✓ Query validation passed")
    except Exception as e:
        print(f"\n✗ Validation failed: {e}")


# Example 3: Similarity Search
async def example_similarity_search():
    """Find similar documents."""
    print("\n=== Example 3: Similarity Search ===")
    
    reference_text = """
    Microservices architecture is an approach to developing applications 
    as a collection of small, independent services that communicate through 
    well-defined interfaces.
    """
    
    client = MCPTestClient()
    
    result = await client.test_search_similar(
        text=reference_text,
        limit=3
    )
    
    print(f"Reference text: {reference_text[:100]}...")
    print(f"Success: {result.success}")
    
    if result.response:
        print(f"\nSimilar documents found: {result.response['total']}")
        for i, doc in enumerate(result.response['results'], 1):
            print(f"\n{i}. {doc['source']['file_name']}")
            print(f"   Score: {doc['score']:.3f}")
            print(f"   Content: {doc['content'][:100]}...")


# Example 4: Get Expanded Context
async def example_get_context():
    """Get context around a specific chunk."""
    print("\n=== Example 4: Get Expanded Context ===")
    
    client = MCPTestClient()
    
    # In a real scenario, you'd get these IDs from a search result
    result = await client.test_get_context(
        document_id="doc_example_001",
        chunk_id="chunk_005"
    )
    
    print(f"Document ID: doc_example_001")
    print(f"Chunk ID: chunk_005")
    print(f"Success: {result.success}")
    
    if result.response:
        context = result.response
        print(f"\nMain content: {context['content'][:100]}...")
        print(f"Before context: {context['before_context'][:50]}...")
        print(f"After context: {context['after_context'][:50]}...")


# Example 5: Batch Processing
async def example_batch_queries():
    """Process multiple queries in batch."""
    print("\n=== Example 5: Batch Processing ===")
    
    queries = [
        "What is artificial intelligence?",
        "Explain neural networks",
        "How does deep learning work?",
        "What are transformers in ML?"
    ]
    
    print(f"Processing {len(queries)} queries...")
    
    client = MCPTestClient()
    tasks = []
    
    for query in queries:
        task = client.test_query_vectors(query, limit=2)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Summary
    successful = sum(1 for r in results if r.success)
    total_duration = sum(r.duration_ms for r in results)
    
    print(f"\nBatch Summary:")
    print(f"  Successful: {successful}/{len(queries)}")
    print(f"  Total duration: {total_duration:.2f}ms")
    print(f"  Average duration: {total_duration/len(queries):.2f}ms")


# Example 6: Security and Input Sanitization
def example_security():
    """Demonstrate security features."""
    print("\n=== Example 6: Security Features ===")
    
    # Test various inputs
    test_inputs = [
        ("Normal query", "What is machine learning?"),
        ("SQL injection", "'; DROP TABLE users; --"),
        ("Script injection", "<script>alert('xss')</script>"),
        ("Path traversal", "../../etc/passwd"),
        ("Long query", "x" * 6000),
    ]
    
    validator = SecurityValidator()
    sanitizer = InputSanitizer()
    
    for name, query in test_inputs:
        print(f"\n{name}: {query[:50]}...")
        try:
            # Validate query
            validated = validator.validate_query(query)
            print("  ✓ Validation passed")
            
            # Sanitize for safety
            sanitized = sanitizer.sanitize_string(validated)
            if sanitized != query:
                print(f"  → Sanitized: {sanitized[:50]}...")
        except Exception as e:
            print(f"  ✗ Rejected: {str(e)}")


# Example 7: Authentication Flow
async def example_authentication():
    """Demonstrate authentication process."""
    print("\n=== Example 7: Authentication ===")
    
    # Initialize token manager
    auth_config = Path("config/mcp_auth.yaml")
    if not auth_config.exists():
        print("Auth config not found. Run 'vector-db-query mcp init' first.")
        return
    
    token_manager = TokenManager(auth_config)
    
    # List available clients
    clients = token_manager.list_clients()
    print(f"\nAvailable clients: {len(clients)}")
    for client in clients:
        print(f"  - {client['client_id']} (rate limit: {client['rate_limit']} req/min)")
    
    # In a real scenario, you'd use actual credentials
    print("\n(Authentication example - would use real credentials in practice)")


# Example 8: Error Handling
async def example_error_handling():
    """Demonstrate error handling patterns."""
    print("\n=== Example 8: Error Handling ===")
    
    client = MCPTestClient()
    
    # Test various error scenarios
    error_scenarios = [
        ("Empty query", ""),
        ("Invalid characters", "SELECT * FROM 🎉"),
        ("Nonexistent document", "doc_does_not_exist"),
    ]
    
    for scenario, param in error_scenarios:
        print(f"\n{scenario}:")
        try:
            if scenario == "Empty query":
                result = await client.test_query_vectors(query=param)
            elif scenario == "Nonexistent document":
                result = await client.test_get_context(
                    document_id=param,
                    chunk_id="chunk_001"
                )
            else:
                result = await client.test_query_vectors(query=param)
            
            if result.success:
                print("  ✓ Unexpectedly succeeded")
            else:
                print(f"  ✗ Failed as expected: {result.error}")
                
        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")


# Example 9: Performance Monitoring
async def example_performance():
    """Monitor query performance."""
    print("\n=== Example 9: Performance Monitoring ===")
    
    client = MCPTestClient()
    
    # Run multiple queries to gather performance data
    queries = [
        ("Short query", "AI"),
        ("Medium query", "What are the key principles of software architecture?"),
        ("Long query", " ".join(["machine learning"] * 50)),
    ]
    
    for query_type, query in queries:
        result = await client.test_query_vectors(query[:5000], limit=5)
        
        print(f"\n{query_type}:")
        print(f"  Query length: {len(query)} chars")
        print(f"  Duration: {result.duration_ms:.2f}ms")
        print(f"  Success: {result.success}")
        
        if result.response:
            print(f"  Results: {len(result.response.get('results', []))}")


# Example 10: Complete Workflow
async def example_complete_workflow():
    """Complete workflow from query to results."""
    print("\n=== Example 10: Complete Workflow ===")
    
    # Step 1: Initialize client
    client = MCPTestClient()
    print("1. Client initialized")
    
    # Step 2: Perform initial search
    print("\n2. Searching for 'microservices architecture'...")
    search_result = await client.test_query_vectors(
        query="microservices architecture",
        limit=5
    )
    
    if not search_result.success:
        print(f"   Search failed: {search_result.error}")
        return
    
    print(f"   Found {search_result.response['total']} results")
    
    # Step 3: Get more similar documents
    if search_result.response['results']:
        first_result = search_result.response['results'][0]
        print(f"\n3. Finding similar to top result...")
        
        similar_result = await client.test_search_similar(
            text=first_result['content'],
            limit=3
        )
        
        if similar_result.success:
            print(f"   Found {similar_result.response['total']} similar documents")
    
    # Step 4: Get expanded context (if we had real IDs)
    print("\n4. Would get expanded context for specific chunks...")
    print("   (Skipped - requires real document IDs)")
    
    print("\n✓ Workflow completed successfully!")


async def main():
    """Run all examples."""
    print("MCP Usage Examples")
    print("=" * 50)
    
    # Run examples
    await example_basic_query()
    await example_advanced_query()
    await example_similarity_search()
    await example_get_context()
    await example_batch_queries()
    example_security()
    await example_authentication()
    await example_error_handling()
    await example_performance()
    await example_complete_workflow()
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())