# MCP Integration Guide

This guide explains how to integrate the Vector DB Query MCP server with various LLMs and applications.

## Table of Contents

1. [Understanding MCP](#understanding-mcp)
2. [Server Setup](#server-setup)
3. [Claude Integration](#claude-integration)
4. [Custom Client Integration](#custom-client-integration)
5. [Security Best Practices](#security-best-practices)
6. [Advanced Usage](#advanced-usage)

## Understanding MCP

Model Context Protocol (MCP) is a standardized protocol for connecting LLMs to external tools and data sources. Key concepts:

- **Tools**: Functions that LLMs can invoke (e.g., query-vectors)
- **Resources**: Data sources LLMs can access (e.g., collections)
- **Stdio Transport**: Communication via standard input/output
- **Structured Responses**: JSON-formatted results

## Server Setup

### Prerequisites

1. **Vector Database Running**
   ```bash
   vector-db-query vector init
   vector-db-query vector status
   ```

2. **Documents Processed**
   ```bash
   vector-db-query process /path/to/documents
   ```

3. **MCP Configuration**
   ```bash
   vector-db-query mcp init
   ```

### Starting the Server

```bash
# Basic start
vector-db-query mcp start

# With debug logging
vector-db-query mcp start --debug

# With custom config
vector-db-query mcp start --config config/custom_mcp.yaml
```

## Claude Integration

### Step 1: Create Claude Client

```bash
# Create a client for Claude
vector-db-query mcp auth create-client claude-client \
  --permissions read query \
  --rate-limit 500
```

### Step 2: Configure Claude

1. Export the client configuration:
   ```bash
   vector-db-query mcp auth export-config claude-client \
     --output claude-config.yaml
   ```

2. In Claude's MCP settings, add:
   ```yaml
   servers:
     - name: vector-db-query
       command: vector-db-query
       args: [mcp, start]
       env:
         MCP_CLIENT_ID: claude-client
         MCP_CLIENT_SECRET: <your-secret>
   ```

### Step 3: Use in Claude

Once connected, you can use natural language:

```
"Search my documents for information about machine learning algorithms"

"Find documents similar to this text: Neural networks are..."

"Get more context for document doc_123 chunk chunk_456"
```

## Custom Client Integration

### Python Client Example

```python
import asyncio
from mcp import Client
from vector_db_query.mcp_integration import TokenManager

async def query_vectors(query: str):
    # Initialize client
    client = Client(
        name="my-app",
        version="1.0.0"
    )
    
    # Authenticate
    token_manager = TokenManager()
    token = token_manager.generate_token(
        "my-client-id",
        "my-client-secret"
    )
    
    # Connect to server
    await client.connect_stdio(
        ["vector-db-query", "mcp", "start"],
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Query vectors
    result = await client.call_tool(
        "query-vectors",
        {
            "query": query,
            "limit": 10,
            "threshold": 0.7
        }
    )
    
    return result

# Run query
results = asyncio.run(query_vectors("What is machine learning?"))
```

### JavaScript/TypeScript Client

```typescript
import { Client } from '@modelcontextprotocol/sdk';

async function searchDocuments(query: string) {
  const client = new Client({
    name: 'my-app',
    version: '1.0.0'
  });
  
  // Connect to server
  await client.connectStdio({
    command: 'vector-db-query',
    args: ['mcp', 'start'],
    env: {
      MCP_CLIENT_ID: process.env.MCP_CLIENT_ID,
      MCP_CLIENT_SECRET: process.env.MCP_CLIENT_SECRET
    }
  });
  
  // Search documents
  const result = await client.callTool('query-vectors', {
    query: query,
    limit: 5
  });
  
  return result;
}
```

## Security Best Practices

### 1. Client Credentials

- **Never commit secrets** to version control
- Use environment variables or secure vaults
- Rotate credentials regularly

```bash
# Good: Using environment variables
export MCP_CLIENT_SECRET=$(vault read secret/mcp/client)

# Bad: Hardcoding in scripts
CLIENT_SECRET="abc123"  # Don't do this!
```

### 2. Network Security

For production deployments:

```yaml
# config/mcp_production.yaml
mcp:
  server_host: 0.0.0.0  # Bind to specific interface
  auth_enabled: true
  allowed_clients:
    - claude-prod
    - internal-app
  rate_limit_requests: 1000
  enable_audit: true
```

### 3. Input Validation

The server automatically validates inputs, but clients should also:

```python
# Client-side validation
def validate_query(query: str) -> str:
    if len(query) > 5000:
        raise ValueError("Query too long")
    
    if not query.strip():
        raise ValueError("Query cannot be empty")
    
    # Remove potentially harmful characters
    query = query.replace('\x00', '')
    
    return query
```

### 4. Monitoring

Set up monitoring for security events:

```bash
# Watch audit logs
tail -f logs/mcp/mcp_audit.log | jq '.details | select(.success == false)'

# Monitor rate limits
vector-db-query mcp metrics | grep rate_limit
```

## Advanced Usage

### 1. Custom Tool Parameters

Extend tool functionality with filters:

```json
{
  "tool": "query-vectors",
  "parameters": {
    "query": "database optimization",
    "filters": {
      "year": 2024,
      "category": "technical",
      "author": "john.doe"
    },
    "limit": 20,
    "threshold": 0.6
  }
}
```

### 2. Batch Queries

Process multiple queries efficiently:

```python
async def batch_search(queries: List[str]):
    tasks = []
    for query in queries:
        task = client.call_tool("query-vectors", {
            "query": query,
            "limit": 5
        })
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### 3. Context Window Management

For large result sets:

```python
# First, get total count
initial_result = await client.call_tool("query-vectors", {
    "query": "machine learning",
    "limit": 1
})

total_results = initial_result.get("total", 0)

# Then paginate through results
all_results = []
for offset in range(0, total_results, 10):
    page = await client.call_tool("query-vectors", {
        "query": "machine learning",
        "limit": 10,
        "offset": offset  # If supported
    })
    all_results.extend(page["results"])
```

### 4. Caching Strategies

Implement client-side caching:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_results(query_hash: str):
    # Cache results for identical queries
    pass

def search_with_cache(query: str):
    query_hash = hashlib.md5(query.encode()).hexdigest()
    
    # Check cache first
    cached = get_cached_results(query_hash)
    if cached:
        return cached
    
    # Otherwise, query server
    results = query_vectors(query)
    cache_results(query_hash, results)
    
    return results
```

### 5. Error Handling

Robust error handling example:

```python
async def safe_query(query: str, retries: int = 3):
    for attempt in range(retries):
        try:
            result = await client.call_tool("query-vectors", {
                "query": query
            })
            return result
            
        except RateLimitError as e:
            # Wait and retry
            wait_time = e.retry_after or (2 ** attempt)
            await asyncio.sleep(wait_time)
            
        except ValidationError as e:
            # Don't retry validation errors
            logger.error(f"Invalid query: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Query failed (attempt {attempt + 1}): {e}")
            if attempt == retries - 1:
                raise
    
    return None
```

## Performance Optimization

### 1. Connection Pooling

For high-traffic applications:

```python
class MCPConnectionPool:
    def __init__(self, size: int = 5):
        self.connections = []
        self.size = size
    
    async def get_connection(self):
        if not self.connections:
            # Create new connection
            client = await self.create_client()
            return client
        
        return self.connections.pop()
    
    async def return_connection(self, client):
        if len(self.connections) < self.size:
            self.connections.append(client)
```

### 2. Result Streaming

For large result sets:

```python
async def stream_results(query: str):
    async for chunk in client.stream_tool("query-vectors", {
        "query": query,
        "stream": True  # If supported
    }):
        yield chunk["results"]
```

### 3. Parallel Processing

Process multiple collections:

```python
async def search_all_collections(query: str):
    # Get all collections
    collections = await client.call_resource("collections")
    
    # Search each in parallel
    tasks = []
    for collection in collections["collections"]:
        task = client.call_tool("query-vectors", {
            "query": query,
            "collection": collection["name"]
        })
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Merge and sort by score
    all_results = []
    for result in results:
        all_results.extend(result["results"])
    
    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[:10]  # Top 10 across all collections
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
echo '{"method": "list_tools"}' | vector-db-query mcp start

# Check server logs
tail -f logs/mcp/mcp_server.log
```

### Authentication Problems

```bash
# Verify client exists
vector-db-query mcp auth list-clients

# Test token generation
vector-db-query mcp auth generate-token test-client <secret>
```

### Performance Issues

```bash
# Check metrics
vector-db-query mcp metrics

# Monitor resource usage
htop -p $(pgrep -f "vector-db-query mcp")
```

## Next Steps

- Read the [API Reference](./api_reference.md)
- Explore [Example Scripts](../examples/)
- Join the [Community Forum](https://github.com/your-repo/discussions)