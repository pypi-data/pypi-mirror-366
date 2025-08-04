#!/usr/bin/env python3
"""Example: Using MCP API to query the vector database."""

import requests
import json

# MCP server endpoint (when running)
MCP_URL = "http://localhost:5000"

def search_via_mcp(query: str, collection: str = "documents", limit: int = 5):
    """Search using the MCP API."""
    
    # Prepare the request
    payload = {
        "query": query,
        "collection": collection,
        "limit": limit
    }
    
    headers = {
        "Content-Type": "application/json",
        # Add auth token if required
        # "Authorization": "Bearer YOUR_TOKEN"
    }
    
    try:
        # Send search request
        response = requests.post(
            f"{MCP_URL}/query",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"Query: {query}")
            print(f"Found {len(results.get('results', []))} results:\n")
            
            for i, result in enumerate(results.get('results', []), 1):
                print(f"Result {i}:")
                print(f"  Score: {result.get('score', 0):.4f}")
                print(f"  Content: {result.get('content', '')[:200]}...")
                print()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to MCP server. Make sure it's running:")
        print("  vdq mcp serve")

def list_collections_via_mcp():
    """List all collections via MCP API."""
    try:
        response = requests.get(f"{MCP_URL}/collections")
        if response.status_code == 200:
            collections = response.json()
            print("Available collections:")
            for collection in collections:
                print(f"  - {collection['name']} ({collection['vectors_count']} vectors)")
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("MCP server not running")

if __name__ == "__main__":
    print("MCP API Examples")
    print("=" * 50)
    
    # List collections
    list_collections_via_mcp()
    print()
    
    # Search examples
    search_via_mcp("Widget sales data")
    search_via_mcp("Employee information from Excel")