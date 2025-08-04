# API Reference

This document provides a comprehensive reference for the Vector DB Query Python API.

## Table of Contents

1. [Document Processing](#document-processing)
2. [Readers](#readers)
3. [Embeddings](#embeddings)
4. [Vector Database](#vector-database)
5. [Configuration](#configuration)
6. [MCP Integration](#mcp-integration)
7. [Utilities](#utilities)

## Document Processing

### DocumentProcessor

The main class for processing documents into vector embeddings.

```python
from vector_db_query.document_processor import DocumentProcessor

processor = DocumentProcessor(
    chunking_strategy="sliding_window",  # or "semantic", "paragraph"
    chunk_size=1000,
    chunk_overlap=200,
    embedding_service=None,  # Uses default if None
    vector_store=None,       # Uses default if None
)
```

#### Methods

##### process_file(file_path, metadata=None)
Process a single file.

```python
document = processor.process_file(
    "/path/to/document.pdf",
    metadata={"category": "research", "author": "John Doe"}
)

# Returns: ProcessedDocument
# - document.chunks: List[TextChunk]
# - document.embeddings: List[List[float]]
# - document.metadata: DocumentMetadata
# - document.success: bool
# - document.errors: List[str]
```

##### process_directory(directory_path, recursive=True, progress_callback=None)
Process all files in a directory.

```python
def on_progress(current, total, filename):
    print(f"Processing {filename}: {current}/{total}")

documents = processor.process_directory(
    "/path/to/documents",
    recursive=True,
    progress_callback=on_progress
)

# Returns: Generator[ProcessedDocument]
```

##### process_files(file_paths, progress_callback=None)
Process a list of files.

```python
files = ["/path/to/doc1.pdf", "/path/to/doc2.docx"]
documents = processor.process_files(files, progress_callback=on_progress)

# Returns: List[ProcessedDocument]
```

### ProcessedDocument

Result of document processing.

```python
@dataclass
class ProcessedDocument:
    file_path: str
    chunks: List[TextChunk]
    embeddings: List[List[float]]
    metadata: DocumentMetadata
    success: bool
    errors: List[str]
    processing_time: float
    partial_success: bool = False
```

### TextChunk

A chunk of text with metadata.

```python
@dataclass
class TextChunk:
    text: str
    metadata: ChunkMetadata
    embedding: Optional[List[float]] = None
```

### ChunkMetadata

Metadata for a text chunk.

```python
@dataclass
class ChunkMetadata:
    start_index: int
    end_index: int
    chunk_index: int
    total_chunks: int
    overlap_with_previous: int
    overlap_with_next: int
    section: Optional[str] = None
    page_number: Optional[int] = None
```

## Readers

### ReaderFactory

Factory for creating appropriate readers based on file type.

```python
from vector_db_query.document_processor.reader import ReaderFactory

factory = ReaderFactory()

# Get reader for a file
reader = factory.get_reader("/path/to/document.pdf")

# Check supported extensions
print(factory.supported_extensions)  # {'.pdf', '.docx', '.txt', ...}

# Register custom reader
factory.register_reader(".custom", CustomReader)
```

### Base Reader Classes

#### DocumentReader
Base class for all document readers.

```python
from vector_db_query.document_processor.base_readers import DocumentReader

class CustomReader(DocumentReader):
    @property
    def supported_extensions(self) -> List[str]:
        return [".custom"]
    
    def read(self, file_path: Path) -> str:
        # Implementation
        return extracted_text
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        # Optional: Extract metadata
        return {"custom": "metadata"}
```

### Specialized Readers

#### PDFReader
```python
from vector_db_query.document_processor.pdf_reader import PDFReader

reader = PDFReader(
    extract_images=False,
    password=None
)
text = reader.read("/path/to/document.pdf")
metadata = reader.extract_metadata("/path/to/document.pdf")
```

#### HTMLReader
```python
from vector_db_query.document_processor.html_reader import HTMLReader

reader = HTMLReader(
    remove_scripts=True,
    remove_styles=True,
    extract_links=True
)
text = reader.read("/path/to/page.html")
```

#### ImageOCRReader
```python
from vector_db_query.document_processor.image_ocr_reader import ImageOCRReader

reader = ImageOCRReader(
    language="eng",
    dpi=300,
    preprocessing=True,
    confidence_threshold=60.0
)
text = reader.read("/path/to/image.png")
```

#### ConfigReader
```python
from vector_db_query.document_processor.config_reader import ConfigReader

# Base class for JSON, YAML, XML, INI readers
reader = JSONReader(pretty_print=True)
text = reader.read("/path/to/config.json")
```

## Embeddings

### EmbeddingService

Service for generating embeddings from text.

```python
from vector_db_query.embeddings import EmbeddingService

service = EmbeddingService(
    provider="google",  # or "openai", "huggingface"
    model="embedding-001",
    api_key="your-api-key",
    dimensions=768,
    batch_size=100
)

# Single embedding
embedding = service.embed_text("Hello world")

# Batch embeddings
texts = ["Hello", "World", "AI"]
embeddings = service.embed_batch(texts)

# With retry logic
embeddings = service.embed_batch(texts, max_retries=3, retry_delay=1.0)
```

### GeminiEmbedder

Google's Gemini embedding implementation.

```python
from vector_db_query.embeddings.gemini_embedder import GeminiEmbedder

embedder = GeminiEmbedder(
    model="embedding-001",
    task_type="RETRIEVAL_DOCUMENT",  # or "RETRIEVAL_QUERY"
    api_key="your-api-key"
)

# Document embedding
doc_embedding = embedder.embed_text(
    "Document text",
    task_type="RETRIEVAL_DOCUMENT"
)

# Query embedding
query_embedding = embedder.embed_text(
    "Search query",
    task_type="RETRIEVAL_QUERY"
)
```

## Vector Database

### QdrantVectorStore

Vector store implementation using Qdrant.

```python
from vector_db_query.vector_store import QdrantVectorStore

store = QdrantVectorStore(
    host="localhost",
    port=6333,
    collection_name="documents",
    vector_size=768,
    distance_metric="cosine"  # or "euclidean", "dot"
)

# Initialize collection
store.initialize_collection(recreate=False)

# Add documents
documents = [
    {
        "id": "doc1",
        "vector": [0.1, 0.2, ...],  # 768 dimensions
        "payload": {
            "text": "Document text",
            "file_path": "/path/to/doc.pdf",
            "chunk_index": 0
        }
    }
]
store.add_documents(documents)

# Search
results = store.search(
    query_vector=[0.1, 0.2, ...],
    limit=10,
    score_threshold=0.7,
    filters={
        "file_type": "pdf",
        "created_after": "2024-01-01"
    }
)

# Get statistics
stats = store.get_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Index size: {stats['index_size_bytes']}")
```

### Search Results

```python
@dataclass
class SearchResult:
    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None
```

## Configuration

### ConfigManager

Centralized configuration management.

```python
from vector_db_query.utils.config import get_config

config = get_config()

# Get values
log_level = config.get("app.log_level")
chunk_size = config.get("document_processing.chunk_size", default=1000)

# Set values
config.set("app.log_level", "DEBUG")
config.set("document_processing.chunk_size", 1500)

# Subscribe to changes
def on_config_change(key, value):
    print(f"Config changed: {key} = {value}")

config.subscribe(on_config_change)

# Validate configuration
issues = config.validate()
if issues:
    print(f"Config issues: {issues}")

# Export as environment variables
env_vars = config.export_env()
```

### FileFormatConfig

File format configuration management.

```python
from vector_db_query.utils.config_enhanced import FileFormatConfig

formats = FileFormatConfig()

# Check if format is supported
if formats.is_supported(".pdf"):
    print("PDF is supported")

# Get all supported formats
all_formats = formats.all_supported
print(f"Total formats: {len(all_formats)}")

# Add custom format
formats.custom_extensions.append(".myformat")
```

## MCP Integration

### MCPServer

Model Context Protocol server for AI integration.

```python
from vector_db_query.mcp_integration import MCPServer

server = MCPServer(
    host="localhost",
    port=5000,
    vector_store=store,
    document_processor=processor
)

# Start server
server.start()

# Available tools
tools = server.get_available_tools()
# - search_documents
# - process_document
# - get_statistics
# - list_collections
```

### MCP Client Usage

```python
from vector_db_query.mcp_integration.client import MCPClient

client = MCPClient(
    server_url="http://localhost:5000",
    api_key="your-api-key"
)

# Search documents
results = client.search_documents(
    query="machine learning",
    limit=10,
    filters={"file_type": "pdf"}
)

# Process new document
result = client.process_document(
    file_path="/path/to/new_doc.pdf",
    metadata={"category": "research"}
)

# Get statistics
stats = client.get_statistics()
```

## Utilities

### Logger

Centralized logging configuration.

```python
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Processing started")
logger.debug("Debug information")
logger.error("Error occurred", exc_info=True)

# Configure logging
from vector_db_query.utils.logger import setup_logging

setup_logging(
    log_level="DEBUG",
    log_file="app.log",
    log_to_console=True,
    json_format=False
)
```

### File Scanner

Scan directories for processable files.

```python
from vector_db_query.document_processor.scanner import FileScanner

scanner = FileScanner(
    supported_extensions={".pdf", ".docx", ".txt"},
    max_file_size_mb=100
)

# Scan directory
files = scanner.scan_directory(
    "/path/to/documents",
    recursive=True,
    exclude_patterns=["*.tmp", "~*"]
)

# Get scan summary
summary = scanner.get_scan_summary(
    "/path/to/documents",
    recursive=True
)
print(f"Total files: {summary['total_files']}")
print(f"Supported files: {summary['supported_files']}")
print(f"Total size: {summary['total_size_mb']} MB")
```

### Text Chunker

Split text into chunks for processing.

```python
from vector_db_query.chunking import TextChunker

chunker = TextChunker(
    chunk_size=1000,
    chunk_overlap=200,
    respect_sentence_boundaries=True
)

# Simple chunking
chunks = chunker.chunk_text(
    "Long document text...",
    metadata={"source": "document.pdf"}
)

# Semantic chunking
semantic_chunker = SemanticChunker(
    embedding_service=embedder,
    similarity_threshold=0.8
)
chunks = semantic_chunker.chunk_text(text)
```

### Cache Manager

Caching for expensive operations.

```python
from vector_db_query.utils.cache import CacheManager

cache = CacheManager(
    cache_dir="./cache",
    max_size_mb=1000,
    ttl_hours=24
)

# Cache embeddings
cache_key = cache.generate_key("document.pdf", "embeddings")
if cache.exists(cache_key):
    embeddings = cache.get(cache_key)
else:
    embeddings = generate_embeddings()
    cache.set(cache_key, embeddings)

# Clear old cache
cache.cleanup(older_than_hours=48)
```

## Error Handling

### Custom Exceptions

```python
from vector_db_query.exceptions import (
    VectorDBError,
    DocumentProcessingError,
    EmbeddingError,
    ConfigurationError
)

try:
    document = processor.process_file(file_path)
except DocumentProcessingError as e:
    logger.error(f"Failed to process {file_path}: {e}")
    # Handle error
except VectorDBError as e:
    logger.error(f"Database error: {e}")
    # Handle error
```

## Complete Example

```python
import asyncio
from pathlib import Path
from vector_db_query import (
    DocumentProcessor,
    QdrantVectorStore,
    GeminiEmbedder,
    get_config
)

async def main():
    # Load configuration
    config = get_config()
    
    # Initialize components
    embedder = GeminiEmbedder(
        api_key=config.get("embedding.api_key"),
        model=config.get("embedding.model")
    )
    
    vector_store = QdrantVectorStore(
        host=config.get("vector_db.host"),
        port=config.get("vector_db.port"),
        collection_name=config.get("vector_db.collection_name")
    )
    
    processor = DocumentProcessor(
        embedding_service=embedder,
        vector_store=vector_store,
        chunk_size=config.get("document_processing.chunk_size"),
        chunk_overlap=config.get("document_processing.chunk_overlap")
    )
    
    # Process documents
    docs_path = Path("~/Documents").expanduser()
    processed = 0
    failed = 0
    
    async for doc in processor.process_directory(docs_path, recursive=True):
        if doc.success:
            processed += 1
            print(f"✓ Processed: {doc.file_path}")
        else:
            failed += 1
            print(f"✗ Failed: {doc.file_path} - {doc.errors}")
    
    print(f"\nProcessed: {processed}, Failed: {failed}")
    
    # Search example
    results = await vector_store.search(
        query_vector=await embedder.embed_text("machine learning algorithms"),
        limit=5
    )
    
    print("\nSearch Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.payload['file_path']} (score: {result.score:.3f})")
        print(f"   {result.payload['text'][:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

## Performance Tips

1. **Batch Processing**: Always use batch methods when processing multiple items
2. **Caching**: Enable caching for embeddings to avoid recomputation
3. **Parallel Processing**: Configure `max_workers` based on your system
4. **Memory Management**: Set appropriate limits for large files
5. **Connection Pooling**: Use connection pools for database operations

## Thread Safety

Most classes are thread-safe for read operations but not for write operations. Use appropriate locking when modifying shared state:

```python
import threading

lock = threading.Lock()

with lock:
    # Modify shared configuration
    config.set("key", "value")
```

## Async Support

Many operations support async execution:

```python
# Async embedding
async def embed_async():
    embeddings = await embedder.embed_batch_async(texts)
    return embeddings

# Async search
async def search_async():
    results = await vector_store.search_async(query_vector)
    return results
```