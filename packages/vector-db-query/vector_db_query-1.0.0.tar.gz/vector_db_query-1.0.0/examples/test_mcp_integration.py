#!/usr/bin/env python3
"""Example script for testing MCP integration."""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vector_db_query.mcp_integration import (
    MCPAuthenticator,
    MCPServerManager,
    TokenManager,
    VectorQueryMCPServer,
)
from vector_db_query.mcp_integration.test_client import MCPTestClient
from vector_db_query.vector_db import VectorDBService


async def main():
    """Run MCP integration test."""
    print("MCP Integration Test Example")
    print("=" * 50)
    
    # 1. Initialize services
    print("\n1. Initializing services...")
    
    # Initialize vector DB service
    vector_service = VectorDBService()
    vector_service.initialize()
    
    # Create MCP server manager
    server_manager = MCPServerManager(vector_service=vector_service)
    
    # 2. Create test client credentials
    print("\n2. Setting up authentication...")
    
    auth_config_path = Path("config/mcp_auth.yaml")
    token_manager = TokenManager(auth_config_path)
    
    # Create a test client if it doesn't exist
    try:
        client_info = token_manager.create_client(
            client_id="example-client",
            permissions=["read", "query"],
            rate_limit=100
        )
        print(f"Created client: {client_info['client_id']}")
        client_secret = client_info['client_secret']
    except ValueError:
        # Client already exists
        print("Using existing client: example-client")
        client_secret = input("Enter client secret: ")
    
    # 3. Start MCP server in background
    print("\n3. Starting MCP server...")
    
    # Note: In production, the server would run in a separate process
    # Here we'll just demonstrate the client testing
    
    # 4. Run client tests
    print("\n4. Running client tests...")
    
    test_client = MCPTestClient(auth_config=auth_config_path)
    
    try:
        # Connect to server
        await test_client.connect("example-client", client_secret)
        
        # Test query vectors
        print("\n- Testing query-vectors tool...")
        result = await test_client.test_query_vectors(
            query="What are the benefits of using vector databases?",
            limit=3
        )
        result.display()
        
        # Test search similar
        print("\n- Testing search-similar tool...")
        result = await test_client.test_search_similar(
            text="Vector databases enable semantic search...",
            limit=2
        )
        result.display()
        
        # Test get context
        print("\n- Testing get-context tool...")
        result = await test_client.test_get_context(
            document_id="doc_example",
            chunk_id="chunk_001"
        )
        result.display()
        
        # Run full test suite
        print("\n5. Running full test suite...")
        summary = await test_client.run_test_suite()
        
        # Save results
        output_path = Path("mcp_test_results.json")
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nTest results saved to: {output_path}")
        
    finally:
        await test_client.disconnect()
    
    print("\n✓ MCP integration test completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())