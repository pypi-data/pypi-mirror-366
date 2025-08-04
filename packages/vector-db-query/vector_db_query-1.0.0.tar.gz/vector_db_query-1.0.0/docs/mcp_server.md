# MCP Server Documentation

## Overview

The Vector DB Query system includes a Model Context Protocol (MCP) server that allows Large Language Models (LLMs) like Claude to query your vector database directly. This enables AI-powered search and retrieval of your documents.

## Features

- **Secure Authentication**: JWT-based authentication with client credentials
- **Rate Limiting**: Protect against abuse with configurable rate limits
- **Structured Responses**: Formatted results optimized for LLM consumption
- **Context Management**: Intelligent context window management for token limits
- **Audit Logging**: Complete audit trail of all queries and responses
- **Performance Monitoring**: Real-time metrics and performance tracking

## Quick Start

### 1. Initialize MCP Configuration

```bash
vector-db-query mcp init
```

This creates:
- `config/mcp.yaml` - Server configuration
- `config/mcp_auth.yaml` - Authentication configuration
- A default client with credentials

**Important**: Save the client secret securely - it cannot be retrieved later!

### 2. Start the MCP Server

```bash
vector-db-query mcp start
```

The server runs on stdio (standard input/output) as per MCP protocol.

### 3. Connect from Claude

Use the client credentials to connect Claude or other LLMs to your MCP server.

## Available Tools

### 1. query-vectors

Search the vector database using natural language queries.

**Parameters**:
- `query` (string, required): Search query text
- `limit` (integer, optional): Maximum results (1-100, default: 10)
- `threshold` (float, optional): Minimum similarity score (0.0-1.0)
- `collection` (string, optional): Target collection name
- `filters` (object, optional): Metadata filters

**Example**:
```json
{
  "tool": "query-vectors",
  "parameters": {
    "query": "What are the benefits of microservices?",
    "limit": 5,
    "threshold": 0.7
  }
}
```

### 2. search-similar

Find documents similar to provided text.

**Parameters**:
- `text` (string, required): Reference text
- `limit` (integer, optional): Maximum results (1-100, default: 10)
- `collection` (string, optional): Target collection name
- `include_source` (boolean, optional): Include source info (default: true)

**Example**:
```json
{
  "tool": "search-similar",
  "parameters": {
    "text": "Microservices are small, independent services...",
    "limit": 3
  }
}
```

### 3. get-context

Get expanded context for a specific document chunk.

**Parameters**:
- `document_id` (string, required): Document identifier
- `chunk_id` (string, required): Chunk identifier
- `context_size` (integer, optional): Characters before/after (100-2000, default: 500)

**Example**:
```json
{
  "tool": "get-context",
  "parameters": {
    "document_id": "doc_123",
    "chunk_id": "chunk_456",
    "context_size": 1000
  }
}
```

## Available Resources

### 1. collections

List available vector collections.

**Response**:
```json
{
  "collections": [
    {
      "name": "default",
      "vectors_count": 1000,
      "status": "ready"
    }
  ]
}
```

### 2. server/status

Get server status information.

**Response**:
```json
{
  "status": "running",
  "version": "1.0.0",
  "uptime": "2h 15m 30s",
  "connected_clients": 1
}
```

### 3. server/metrics

Get server metrics and statistics.

**Response**:
```json
{
  "server": {
    "total_requests": 150,
    "success_rate": "98.5%",
    "average_duration_ms": "125.3"
  },
  "tools": {
    "query-vectors": {
      "requests": 100,
      "errors": 2,
      "average_duration_ms": "150.5"
    }
  }
}
```

## Authentication

### Creating Clients

```bash
# Create a new client
vector-db-query mcp auth create-client my-client \
  --permissions read query \
  --rate-limit 200

# List all clients
vector-db-query mcp auth list-clients

# Generate a token
vector-db-query mcp auth generate-token my-client <client-secret>
```

### Client Configuration

Export client configuration for distribution:

```bash
vector-db-query mcp auth export-config my-client --output client-config.yaml
```

## Security

### Rate Limiting

Default limits per client:
- 100 requests per minute
- 1000 requests per hour
- Burst limit of 20 requests

### Input Validation

- Query length limited to 5000 characters
- Collection names must be alphanumeric with underscores/hyphens
- Filters support only basic types (string, number, boolean)
- Automatic sanitization of sensitive fields

### Forbidden Patterns

The following patterns are blocked in queries:
- SQL injection attempts (DROP, DELETE, etc.)
- Script injection (JavaScript, HTML)
- Command execution attempts

## Configuration

### Server Configuration (config/mcp.yaml)

```yaml
mcp:
  server_host: localhost
  server_port: 5000
  max_connections: 10
  auth_enabled: true
  token_expiry: 3600
  max_context_tokens: 100000
  enable_caching: true
  cache_ttl: 300
```

### Environment Variables

- `MCP_SERVER_HOST`: Override server host
- `MCP_SERVER_PORT`: Override server port
- `MCP_AUTH_ENABLED`: Enable/disable authentication
- `MCP_DEBUG`: Enable debug logging

## Monitoring

### View Metrics

```bash
# View current metrics
vector-db-query mcp metrics

# Export metrics to file
vector-db-query mcp metrics --export metrics.json
```

### Log Files

Logs are stored in `logs/mcp/`:
- `mcp_server.log` - General server logs
- `mcp_errors.log` - Error logs only
- `mcp_audit.log` - Audit trail (JSON format)

## Testing

### Test Client

Run the built-in test client:

```bash
# Run all tests
vector-db-query mcp test-client --client-id test-client

# Generate example queries
vector-db-query mcp example-queries
```

### Example Script

See `examples/test_mcp_integration.py` for a complete example.

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify client credentials
   - Check token expiry
   - Ensure auth config exists

2. **Rate Limit Exceeded**
   - Wait before retrying
   - Check client rate limits
   - Consider increasing limits

3. **No Results Found**
   - Verify documents are processed
   - Check collection name
   - Lower similarity threshold

4. **Connection Refused**
   - Ensure server is running
   - Check firewall settings
   - Verify port availability

### Debug Mode

Enable debug logging:

```bash
vector-db-query mcp start --debug
```

## Best Practices

1. **Security**
   - Always use authentication in production
   - Regularly rotate client secrets
   - Monitor audit logs for suspicious activity

2. **Performance**
   - Use appropriate result limits
   - Enable caching for repeated queries
   - Monitor response times

3. **Context Management**
   - Set reasonable token limits
   - Use filters to reduce result size
   - Implement pagination for large results

## API Reference

For detailed API documentation, see:
- [MCP Protocol Specification](https://github.com/anthropics/mcp)
- [Tool Schemas](./api/tools.md)
- [Response Formats](./api/responses.md)