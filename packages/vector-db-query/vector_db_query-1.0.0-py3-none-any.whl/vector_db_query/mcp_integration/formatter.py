"""Response formatting for MCP server."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..document_processor.models import Chunk, ProcessedDocument
from ..vector_db.models import SearchResult
from .models import ExpandedContext, MCPSearchResult, SourceInfo


logger = logging.getLogger(__name__)


@dataclass
class FormattingConfig:
    """Configuration for response formatting."""
    
    max_content_length: int = 1000
    include_metadata: bool = True
    include_source: bool = True
    include_scores: bool = True
    timestamp_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"
    truncation_suffix: str = "..."
    highlight_matches: bool = False


class ResponseFormatter:
    """Formats responses for MCP protocol."""
    
    def __init__(self, config: Optional[FormattingConfig] = None):
        """Initialize response formatter.
        
        Args:
            config: Formatting configuration
        """
        self.config = config or FormattingConfig()
        logger.info("Response formatter initialized")
    
    def format_search_results(
        self,
        results: List[SearchResult],
        query: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Format search results for MCP response.
        
        Args:
            results: List of search results
            query: Original query
            max_tokens: Maximum tokens to include
            
        Returns:
            Formatted response dictionary
        """
        formatted_results = []
        total_chars = 0
        max_chars = max_tokens * 4 if max_tokens else None  # Rough estimate
        
        for result in results:
            # Format single result
            formatted = self.format_single_result(result)
            
            # Check token limit
            if max_chars:
                result_chars = len(json.dumps(formatted))
                if total_chars + result_chars > max_chars:
                    # Truncate or skip
                    if not formatted_results:
                        # Must include at least one result
                        formatted["content"] = self._truncate_content(
                            formatted["content"],
                            max_chars - total_chars - 500  # Leave room for metadata
                        )
                        formatted_results.append(formatted)
                    break
                
                total_chars += result_chars
            
            formatted_results.append(formatted)
        
        return {
            "query": query,
            "results": formatted_results,
            "total_results": len(results),
            "returned_results": len(formatted_results),
            "truncated": len(formatted_results) < len(results),
            "timestamp": datetime.utcnow().strftime(self.config.timestamp_format)
        }
    
    def format_single_result(self, result: SearchResult) -> Dict[str, Any]:
        """Format a single search result.
        
        Args:
            result: Search result to format
            
        Returns:
            Formatted result dictionary
        """
        # Basic result structure
        formatted = {
            "chunk_id": result.chunk.id,
            "document_id": result.document.id,
            "content": self._format_content(result.chunk.content)
        }
        
        # Add score if configured
        if self.config.include_scores:
            formatted["score"] = round(result.score, 4)
        
        # Add metadata if configured
        if self.config.include_metadata:
            formatted["metadata"] = self._filter_metadata(result.chunk.metadata)
        
        # Add source information if configured
        if self.config.include_source:
            formatted["source"] = self._format_source_info(result)
        
        return formatted
    
    def format_error(self, error: Exception, request_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Format error response.
        
        Args:
            error: Exception that occurred
            request_info: Optional request information
            
        Returns:
            Formatted error dictionary
        """
        error_response = {
            "error": {
                "type": error.__class__.__name__,
                "message": str(error),
                "timestamp": datetime.utcnow().strftime(self.config.timestamp_format)
            }
        }
        
        # Add error details if available
        if hasattr(error, 'code'):
            error_response["error"]["code"] = error.code
        
        if hasattr(error, 'details') and error.details:
            error_response["error"]["details"] = error.details
        
        # Add request info if provided
        if request_info:
            error_response["request"] = request_info
        
        return error_response
    
    def format_context_response(
        self,
        chunk: Chunk,
        document: ProcessedDocument,
        before_context: str,
        after_context: str
    ) -> Dict[str, Any]:
        """Format expanded context response.
        
        Args:
            chunk: The main chunk
            document: The document containing the chunk
            before_context: Context before the chunk
            after_context: Context after the chunk
            
        Returns:
            Formatted context dictionary
        """
        return {
            "chunk": {
                "id": chunk.id,
                "content": chunk.content,
                "metadata": self._filter_metadata(chunk.metadata)
            },
            "context": {
                "before": before_context,
                "after": after_context,
                "before_length": len(before_context),
                "after_length": len(after_context)
            },
            "document": {
                "id": document.id,
                "file_path": document.file_path,
                "total_chunks": document.total_chunks
            },
            "timestamp": datetime.utcnow().strftime(self.config.timestamp_format)
        }
    
    def format_collection_list(self, collections: List[Any]) -> Dict[str, Any]:
        """Format collection list response.
        
        Args:
            collections: List of collections
            
        Returns:
            Formatted collections dictionary
        """
        return {
            "collections": [
                {
                    "name": col.name,
                    "vectors_count": col.vectors_count,
                    "status": col.status,
                    "created_at": col.created_at.strftime(self.config.timestamp_format)
                    if hasattr(col, 'created_at') else None
                }
                for col in collections
            ],
            "total": len(collections),
            "timestamp": datetime.utcnow().strftime(self.config.timestamp_format)
        }
    
    def truncate_content(self, text: str, max_length: Optional[int] = None) -> str:
        """Truncate content to specified length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length (uses config default if None)
            
        Returns:
            Truncated text
        """
        max_length = max_length or self.config.max_content_length
        return self._truncate_content(text, max_length)
    
    def add_metadata(
        self,
        result: Dict[str, Any],
        include_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add metadata to result.
        
        Args:
            result: Result dictionary
            include_fields: Fields to include (None for all)
            
        Returns:
            Result with metadata
        """
        if "metadata" not in result:
            return result
        
        if include_fields:
            result["metadata"] = {
                k: v for k, v in result["metadata"].items()
                if k in include_fields
            }
        
        return result
    
    def _format_content(self, content: str) -> str:
        """Format content for response.
        
        Args:
            content: Raw content
            
        Returns:
            Formatted content
        """
        # Truncate if needed
        formatted = self._truncate_content(content, self.config.max_content_length)
        
        # Clean up whitespace
        formatted = " ".join(formatted.split())
        
        return formatted
    
    def _truncate_content(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        # Find a good break point
        truncate_at = max_length - len(self.config.truncation_suffix)
        
        # Try to break at word boundary
        last_space = text.rfind(' ', 0, truncate_at)
        if last_space > truncate_at * 0.8:  # Within 20% of target
            truncate_at = last_space
        
        return text[:truncate_at].rstrip() + self.config.truncation_suffix
    
    def _filter_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Filter metadata for response.
        
        Args:
            metadata: Raw metadata
            
        Returns:
            Filtered metadata
        """
        # Remove internal fields
        filtered = {
            k: v for k, v in metadata.items()
            if not k.startswith('_') and k not in ['embedding', 'vector']
        }
        
        # Convert non-serializable types
        for key, value in filtered.items():
            if isinstance(value, (datetime,)):
                filtered[key] = value.strftime(self.config.timestamp_format)
            elif isinstance(value, Path):
                filtered[key] = str(value)
        
        return filtered
    
    def _format_source_info(self, result: SearchResult) -> Dict[str, Any]:
        """Format source information.
        
        Args:
            result: Search result
            
        Returns:
            Source information dictionary
        """
        return {
            "file_name": Path(result.document.file_path).name,
            "file_path": result.document.file_path,
            "file_type": result.document.file_type,
            "chunk_index": result.chunk.chunk_index,
            "total_chunks": result.document.total_chunks,
            "created_at": result.document.created_at.strftime(self.config.timestamp_format)
        }
    
    def create_mcp_search_result(self, result: SearchResult) -> MCPSearchResult:
        """Create MCPSearchResult from SearchResult.
        
        Args:
            result: Search result
            
        Returns:
            MCPSearchResult instance
        """
        source_info = SourceInfo(
            file_name=Path(result.document.file_path).name,
            file_path=result.document.file_path,
            chunk_index=result.chunk.chunk_index,
            total_chunks=result.document.total_chunks,
            created_at=result.document.created_at.strftime(self.config.timestamp_format),
            file_type=result.document.file_type
        )
        
        return MCPSearchResult(
            chunk_id=result.chunk.id,
            document_id=result.document.id,
            score=result.score,
            content=self._format_content(result.chunk.content),
            metadata=self._filter_metadata(result.chunk.metadata),
            source_info=source_info
        )
    
    def create_expanded_context(
        self,
        chunk: Chunk,
        document_id: str,
        before_context: str,
        after_context: str
    ) -> ExpandedContext:
        """Create ExpandedContext instance.
        
        Args:
            chunk: The main chunk
            document_id: Document ID
            before_context: Context before
            after_context: Context after
            
        Returns:
            ExpandedContext instance
        """
        return ExpandedContext(
            chunk_id=chunk.id,
            document_id=document_id,
            content=chunk.content,
            before_context=before_context,
            after_context=after_context,
            metadata=self._filter_metadata(chunk.metadata)
        )
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4