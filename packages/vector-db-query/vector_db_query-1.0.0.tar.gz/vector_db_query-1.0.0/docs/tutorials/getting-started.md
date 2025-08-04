# Getting Started with Vector DB Query

## Introduction

Vector DB Query is a powerful tool for semantic document search. This tutorial will walk you through your first steps.

## Prerequisites

- Python 3.9 or higher
- 4GB RAM minimum
- 10GB free disk space

## Installation

### From PyPI (Recommended)

```bash
pip install vector-db-query
```

### With Monitoring Features

```bash
pip install vector-db-query[monitoring]
```

## Initial Setup

### 1. Configure the System

```bash
vdq config setup
```

This creates a default configuration file at `~/.vdq/config.yaml`.

### 2. Start Qdrant

Vector DB Query uses Qdrant as its vector database. You can start it using Docker:

```bash
docker run -p 6333:6333 -v ~/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 3. Verify Installation

```bash
vdq --version
vdq status
```

## Your First Document

### 1. Create a Test Document

```bash
echo "Machine learning is a subset of artificial intelligence that enables systems to learn from data." > ml-intro.txt
```

### 2. Process the Document

```bash
vdq process ml-intro.txt
```

### 3. Search Your Document

```bash
vdq query "what is machine learning?"
```

## Processing Multiple Documents

### 1. Create a Document Directory

```bash
mkdir my-docs
cp *.pdf *.txt *.docx my-docs/
```

### 2. Process All Documents

```bash
vdq process my-docs/
```

### 3. Search Across All Documents

```bash
vdq query "artificial intelligence applications"
```

## Using Collections

Collections help organize your documents by topic or type.

### 1. Create a Collection

```bash
vdq vector create-collection --name research
```

### 2. Process Documents into a Collection

```bash
vdq process ~/research-papers/ --collection research
```

### 3. Search Within a Collection

```bash
vdq query "neural networks" --collection research
```

## Interactive Mode

For a better experience, use interactive mode:

```bash
vdq interactive start
```

Features:
- Visual file browser
- Live search results
- Document preview
- Search history

## Monitoring Dashboard

Start the monitoring dashboard to track system performance:

```bash
vdq monitor
```

Open http://localhost:8501 in your browser.

## Next Steps

- Read the [User Guide](../user-guide/index.md)
- Explore [Advanced Features](../user-guide/advanced-features.md)
- Set up [MCP Integration](../user-guide/mcp-integration.md)
- Join our [Community](https://github.com/your-org/vector-db-query/discussions)