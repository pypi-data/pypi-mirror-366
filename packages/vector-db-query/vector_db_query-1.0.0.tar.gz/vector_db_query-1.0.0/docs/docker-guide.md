# Docker Deployment Guide

This guide covers how to build, run, and deploy Vector DB Query System using Docker.

## Prerequisites

- Docker installed (https://www.docker.com/get-started)
- Docker Compose (usually included with Docker Desktop)
- Docker Hub account (for publishing)

## Quick Start

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/yourusername/vector-db-query.git
cd vector-db-query

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Pre-built Image

```bash
# Pull from Docker Hub
docker pull yourusername/vector-db-query:latest

# Run with Qdrant
docker network create vector-db-net

# Start Qdrant
docker run -d \
  --name qdrant \
  --network vector-db-net \
  -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Start Vector DB Query
docker run -it \
  --name vector-db-query \
  --network vector-db-net \
  -p 5000:5000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -e QDRANT_HOST=qdrant \
  yourusername/vector-db-query:latest
```

## Building the Image

### Local Build

```bash
# Build the image
docker build -t vector-db-query:latest .

# Build with specific version tag
docker build -t vector-db-query:1.0.0 .
```

### Multi-platform Build

```bash
# Setup buildx (one time)
docker buildx create --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t vector-db-query:latest \
  .
```

## Running Containers

### Interactive CLI Mode

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  vector-db-query:latest \
  interactive
```

### MCP Server Mode

```bash
docker run -d \
  --name vector-db-mcp \
  -p 5000:5000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  vector-db-query:latest \
  mcp start
```

### Process Documents

```bash
docker run --rm \
  -v $(pwd)/documents:/documents \
  -v $(pwd)/data:/app/data \
  vector-db-query:latest \
  process /documents
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_HOST` | Qdrant server hostname | localhost |
| `QDRANT_PORT` | Qdrant server port | 6333 |
| `LOG_LEVEL` | Logging level | INFO |
| `MCP_SERVER_HOST` | MCP server bind address | 0.0.0.0 |
| `MCP_SERVER_PORT` | MCP server port | 5000 |
| `GOOGLE_API_KEY` | Google AI API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `COHERE_API_KEY` | Cohere API key | - |

## Volumes

| Volume | Description |
|--------|-------------|
| `/app/config` | Configuration files |
| `/app/data` | Application data |
| `/app/logs` | Log files |
| `/documents` | Input documents for processing |

## Docker Compose Configuration

### Basic Setup

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage

  vector-db-query:
    image: vector-db-query:latest
    depends_on:
      - qdrant
    ports:
      - "5000:5000"
    environment:
      - QDRANT_HOST=qdrant
    volumes:
      - ./config:/app/config
      - ./data:/app/data

volumes:
  qdrant_storage:
```

### Production Setup

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    deploy:
      resources:
        limits:
          memory: 2G

  vector-db-query:
    image: vector-db-query:latest
    restart: unless-stopped
    depends_on:
      - qdrant
    ports:
      - "127.0.0.1:5000:5000"
    environment:
      - QDRANT_HOST=qdrant
      - LOG_LEVEL=WARNING
    volumes:
      - ./config:/app/config:ro
      - ./data:/app/data
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          memory: 1G

volumes:
  qdrant_storage:
```

## Publishing to Docker Hub

1. **Login to Docker Hub**:
   ```bash
   docker login
   ```

2. **Tag the image**:
   ```bash
   docker tag vector-db-query:latest yourusername/vector-db-query:latest
   docker tag vector-db-query:latest yourusername/vector-db-query:1.0.0
   ```

3. **Push to Docker Hub**:
   ```bash
   docker push yourusername/vector-db-query:latest
   docker push yourusername/vector-db-query:1.0.0
   ```

## Health Checks

The container includes a health check that runs:
```bash
vector-db-query status
```

Check container health:
```bash
docker ps
docker inspect vector-db-query | jq '.[0].State.Health'
```

## Troubleshooting

### Container won't start
- Check logs: `docker logs vector-db-query`
- Verify Qdrant is running: `docker ps | grep qdrant`
- Check network connectivity: `docker network ls`

### Permission issues
- Ensure volumes have correct permissions
- The container runs as non-root user `appuser` (UID 1000)

### Connection errors
- Verify environment variables are set correctly
- Check if services are on the same network
- Ensure ports are not already in use

## Security Considerations

1. **Run as non-root**: The container runs as `appuser`
2. **Read-only root filesystem**: Add `read_only: true` in production
3. **Network isolation**: Use custom networks, not default bridge
4. **Secrets management**: Use Docker secrets for API keys
5. **Resource limits**: Set memory and CPU limits

## Kubernetes Deployment

See [kubernetes/](../kubernetes/) directory for Kubernetes manifests and Helm charts.