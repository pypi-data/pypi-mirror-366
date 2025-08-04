# Vector DB Query Documentation

Welcome to the Vector DB Query documentation! This tool provides a powerful CLI interface for indexing documents and querying them using vector similarity search.

## Overview

Vector DB Query is a comprehensive solution for:

- 📄 **Document Processing**: Index various document formats (PDF, DOCX, Markdown, text files)
- 🔍 **Semantic Search**: Query your documents using natural language
- 🤖 **AI Integration**: MCP server for AI assistant integration
- 🎨 **Interactive CLI**: Rich terminal interface with animations and themes
- 🚀 **High Performance**: Optimized for large document collections

## Key Features

### Document Processing
- Support for multiple file formats
- Intelligent text chunking with overlap
- Batch processing capabilities
- Metadata preservation

### Vector Database
- Powered by Qdrant vector database
- High-performance similarity search
- Scalable to millions of documents
- Persistent storage

### Interactive CLI
- Beautiful terminal UI with Rich
- File browser with preview
- Interactive query builder
- Real-time progress tracking

### AI Integration
- MCP server for AI assistants
- Standardized API for Claude and other AI tools
- Secure authentication
- Rate limiting support

### Enterprise Monitoring
- Real-time performance dashboard
- Advanced scheduling system
- Multi-channel notifications
- Performance optimization tools

## Quick Start

```bash
# Install
pip install vector-db-query

# Configure
vector-db-query config setup

# Process documents
vector-db-query process /path/to/documents

# Search
vector-db-query query "find information about Python"

# Interactive mode
vector-db-query interactive start
```

## Navigation

- [Installation](installation.md) - Setup instructions
- [Getting Started](getting-started.md) - Quick tutorial
- [User Guide](user-guide/index.md) - Detailed usage instructions
- [Configuration](configuration.md) - Configuration options
- [API Reference](api/index.md) - API documentation
- [Examples](examples/index.md) - Usage examples
- [FAQ](faq.md) - Frequently asked questions

## System Requirements

- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space
- Qdrant vector database (local or cloud)