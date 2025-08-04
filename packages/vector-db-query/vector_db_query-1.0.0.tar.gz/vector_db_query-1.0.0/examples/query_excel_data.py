#!/usr/bin/env python3
"""Example: Query Excel data from the vector database."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vector_db_query.vector_db.client import QdrantClient
from vector_db_query.document_processor.embedder import GeminiEmbedder
from vector_db_query.utils.config import get_config

def search_excel_data(query: str, limit: int = 5):
    """Search through Excel data in the vector database."""
    
    # Initialize configuration
    config = get_config()
    
    # Create embedder for query
    embedder = GeminiEmbedder(
        api_key=config.get("embeddings.api_key"),
        model=config.get("embeddings.model", "models/embedding-001")
    )
    
    # Create Qdrant client
    client = QdrantClient(
        host=config.get("qdrant.host", "localhost"),
        port=config.get("qdrant.port", 6333)
    )
    
    # Connect to Qdrant
    if not client.connect():
        print("Failed to connect to Qdrant. Make sure it's running.")
        return
    
    # Generate embedding for query
    print(f"Searching for: {query}")
    query_embedding = embedder.embed_single(query)
    
    # Search in the collection
    results = client.search(
        collection_name="documents",
        query_vector=query_embedding.vector,
        limit=limit
    )
    
    # Display results
    print(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Score: {result.score:.4f}")
        print(f"  Source: {result.payload.get('source', 'Unknown')}")
        print(f"  Content: {result.payload.get('content', '')[:200]}...")
        print(f"  Metadata: {result.payload.get('metadata', {})}")
        print()

if __name__ == "__main__":
    # Example queries
    queries = [
        "What are the sales figures for Widget A?",
        "Show employee salaries",
        "Project status information",
        "Company revenue data"
    ]
    
    print("Excel Data Search Examples")
    print("=" * 50)
    
    for query in queries:
        search_excel_data(query, limit=3)
        print("-" * 50)