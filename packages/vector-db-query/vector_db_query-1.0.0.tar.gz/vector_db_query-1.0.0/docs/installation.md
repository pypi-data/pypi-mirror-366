# Installation Guide

## Prerequisites

Before installing Vector DB Query, ensure you have:

- **Python 3.9+** installed
- **pip** package manager
- **Qdrant** vector database (optional for local setup)

## Installation Methods

### 1. Install from PyPI (Recommended)

```bash
pip install vector-db-query
```

### 2. Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/vector-db-query.git
cd vector-db-query

# Install in development mode
pip install -e .
```

### 3. Docker Installation

```bash
# Pull the Docker image
docker pull vector-db-query:latest

# Run with Docker Compose
docker-compose up -d
```

## Setting up Qdrant

Vector DB Query requires a Qdrant instance for vector storage.

### Local Qdrant with Docker

```bash
docker run -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### Qdrant Cloud

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a cluster
3. Get your API key and URL

## Initial Configuration

After installation, run the setup wizard:

```bash
vector-db-query config setup
```

This will prompt you for:

1. **Qdrant Connection**
   - Host (default: localhost)
   - Port (default: 6333)
   - API key (if using Qdrant Cloud)

2. **Embeddings API**
   - Provider (Google, OpenAI, etc.)
   - API key
   - Model selection

3. **Processing Settings**
   - Chunk size
   - File extensions to process

### Manual Configuration

You can also create the configuration manually:

```bash
mkdir -p ~/.vector_db_query
nano ~/.vector_db_query/config.yaml
```

Example configuration:

```yaml
app:
  name: Vector DB Query
  version: 1.0.0

qdrant:
  host: localhost
  port: 6333
  collection_name: documents
  api_key: null  # Set for Qdrant Cloud

embeddings:
  provider: google
  model: models/embedding-001
  api_key: YOUR_API_KEY_HERE
  dimension: 768

processing:
  chunk_size: 1000
  chunk_overlap: 200
  file_extensions:
    - .txt
    - .md
    - .pdf
    - .doc
    - .docx

mcp:
  enabled: false
  port: 8080
  auth_required: false
```

## Verify Installation

Check that everything is installed correctly:

```bash
# Check version
vector-db-query --version

# Test configuration
vector-db-query config test

# Check Qdrant connection
vector-db-query status
```

## Development Installation

For development work:

```bash
# Clone repository
git clone https://github.com/your-org/vector-db-query.git
cd vector-db-query

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Troubleshooting

### Common Issues

**1. Import Error**
```
ModuleNotFoundError: No module named 'vector_db_query'
```
Solution: Ensure you've installed the package and activated your virtual environment.

**2. Qdrant Connection Error**
```
Connection refused to localhost:6333
```
Solution: Ensure Qdrant is running. Start with:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**3. API Key Error**
```
Invalid API key for embeddings
```
Solution: Check your API key in the configuration file.

### Getting Help

- Check the [FAQ](faq.md)
- Visit our [GitHub Issues](https://github.com/your-org/vector-db-query/issues)
- Join our [Discord Community](https://discord.gg/vector-db-query)

## Next Steps

Once installed, proceed to the [Getting Started](getting-started.md) guide to learn how to use Vector DB Query.