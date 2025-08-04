# Getting Started

This guide will walk you through your first steps with Vector DB Query.

## Quick Start Tutorial

### Step 1: Process Your First Documents

Let's start by indexing some documents:

```bash
# Process a single file
vector-db-query process ~/Documents/report.pdf

# Process a directory
vector-db-query process ~/Documents/my-notes/

# Process with specific extensions
vector-db-query process ~/Documents --extensions .md .txt
```

### Step 2: Search Your Documents

Now search through your indexed documents:

```bash
# Basic search
vector-db-query query "machine learning algorithms"

# Search with more results
vector-db-query query "Python programming" --limit 20

# Search with score threshold
vector-db-query query "data analysis" --threshold 0.8
```

### Step 3: Interactive Mode

For the best experience, use interactive mode:

```bash
vector-db-query interactive start
```

This opens a rich terminal interface where you can:
- Browse and select files visually
- Build queries interactively
- View results with syntax highlighting
- Manage your configuration

## Core Concepts

### Document Processing

When you process documents, Vector DB Query:

1. **Reads** the document content
2. **Chunks** text into manageable pieces
3. **Generates embeddings** using AI models
4. **Stores** vectors in Qdrant database

### Vector Search

Searching works by:

1. **Converting** your query to a vector
2. **Finding** similar vectors in the database
3. **Ranking** results by similarity score
4. **Returning** the most relevant chunks

### Metadata

Each document chunk stores metadata:
- Source file path
- File type
- Chunk position
- Processing timestamp
- Custom tags (optional)

## Common Workflows

### 1. Building a Knowledge Base

```bash
# Process all documentation
vector-db-query process ~/projects/docs --recursive

# Add more documents incrementally
vector-db-query process ~/downloads/new-papers/

# Check statistics
vector-db-query stats
```

### 2. Research Assistant

```bash
# Start interactive mode
vector-db-query interactive start

# In the menu:
# 1. Select "Query Database"
# 2. Use natural language questions
# 3. Browse results
# 4. Open source documents
```

### 3. API Integration

Enable the MCP server for AI assistants:

```bash
# Enable MCP in config
vector-db-query config set mcp.enabled true

# Start MCP server
vector-db-query mcp start

# Connect from AI assistant
# Use the provided endpoint and token
```

## Interactive Mode Features

### File Browser
- Navigate directories with arrow keys
- Preview files before processing
- Multi-select with space bar
- Filter by extension

### Query Builder
- Natural language input
- Query history (↑/↓ arrows)
- Query templates
- Advanced filters

### Result Viewer
- Syntax highlighting
- Relevance scores
- Source file links
- Export options

### Configuration Editor
- Visual config editing
- Validation
- Import/export settings
- Preset configurations

## Tips for Better Results

### 1. Document Preparation
- Use clear headings in documents
- Keep related content together
- Add metadata when possible

### 2. Query Techniques
- Be specific in queries
- Use relevant keywords
- Try different phrasings
- Combine with filters

### 3. Performance Optimization
- Process documents in batches
- Use appropriate chunk sizes
- Enable caching for frequent queries
- Monitor memory usage

## Command Reference

### Essential Commands

```bash
# Processing
vector-db-query process <path> [options]
  --recursive        Process subdirectories
  --extensions       File types to process
  --batch-size       Documents per batch

# Querying  
vector-db-query query <text> [options]
  --limit           Max results (default: 10)
  --threshold       Min similarity score
  --filter          Metadata filters

# Management
vector-db-query stats            Show statistics
vector-db-query clear            Clear database
vector-db-query export           Export results
```

### Interactive Commands

```bash
# Start interactive mode
vector-db-query interactive start

# Quick menus
vector-db-query interactive menu
vector-db-query interactive query
vector-db-query interactive browse
```

## What's Next?

Now that you understand the basics:

1. Read the [User Guide](user-guide/index.md) for detailed features
2. Configure [Advanced Settings](configuration.md)
3. Explore [Integration Options](user-guide/integrations.md)
4. Check out [Examples](examples/index.md)

## Getting Help

If you run into issues:

1. Check error messages - they often suggest solutions
2. Run `vector-db-query --help` for command help
3. Use `vector-db-query doctor` to diagnose issues
4. Visit our [FAQ](faq.md) page
5. Ask in [GitHub Discussions](https://github.com/your-org/vector-db-query/discussions)