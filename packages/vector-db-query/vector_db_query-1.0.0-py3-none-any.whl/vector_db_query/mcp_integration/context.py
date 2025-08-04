"""Context management for MCP server responses."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..vector_db.models import SearchResult
from .formatter import ResponseFormatter


logger = logging.getLogger(__name__)


@dataclass
class TokenEstimate:
    """Token count estimate for content."""
    
    content: str
    char_count: int
    estimated_tokens: int
    
    @classmethod
    def from_text(cls, text: str) -> "TokenEstimate":
        """Create token estimate from text.
        
        Args:
            text: Text to estimate
            
        Returns:
            TokenEstimate instance
        """
        char_count = len(text)
        # Rough estimate: 1 token ≈ 4 characters
        estimated_tokens = char_count // 4
        
        return cls(
            content=text,
            char_count=char_count,
            estimated_tokens=estimated_tokens
        )


@dataclass
class ContextWindow:
    """Represents a context window for LLM."""
    
    max_tokens: int
    used_tokens: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def remaining_tokens(self) -> int:
        """Get remaining tokens in window."""
        return max(0, self.max_tokens - self.used_tokens)
    
    @property
    def is_full(self) -> bool:
        """Check if window is full."""
        return self.remaining_tokens <= 0
    
    @property
    def usage_percentage(self) -> float:
        """Get usage percentage."""
        if self.max_tokens == 0:
            return 0.0
        return (self.used_tokens / self.max_tokens) * 100
    
    def can_fit(self, token_count: int) -> bool:
        """Check if content can fit in window.
        
        Args:
            token_count: Number of tokens
            
        Returns:
            True if can fit
        """
        return token_count <= self.remaining_tokens
    
    def add_result(self, result: Dict[str, Any], token_count: int) -> bool:
        """Add result to window if it fits.
        
        Args:
            result: Result to add
            token_count: Token count for result
            
        Returns:
            True if added successfully
        """
        if not self.can_fit(token_count):
            return False
        
        self.results.append(result)
        self.used_tokens += token_count
        return True


class ContextManager:
    """Manages context windows for MCP responses."""
    
    def __init__(
        self,
        max_context_tokens: int = 100000,
        reserve_tokens: int = 1000,
        formatter: Optional[ResponseFormatter] = None
    ):
        """Initialize context manager.
        
        Args:
            max_context_tokens: Maximum tokens for context
            reserve_tokens: Tokens to reserve for system use
            formatter: Response formatter
        """
        self.max_context_tokens = max_context_tokens
        self.reserve_tokens = reserve_tokens
        self.effective_max_tokens = max_context_tokens - reserve_tokens
        self.formatter = formatter or ResponseFormatter()
        
        logger.info(
            f"Context manager initialized with {self.effective_max_tokens} "
            f"effective tokens (reserved: {reserve_tokens})"
        )
    
    def build_context(
        self,
        results: List[SearchResult],
        token_limit: Optional[int] = None,
        prioritize: bool = True
    ) -> ContextWindow:
        """Build context window from search results.
        
        Args:
            results: Search results to include
            token_limit: Optional token limit override
            prioritize: Whether to prioritize by score
            
        Returns:
            ContextWindow with selected results
        """
        # Use provided limit or default
        max_tokens = min(
            token_limit or self.effective_max_tokens,
            self.effective_max_tokens
        )
        
        # Create context window
        window = ContextWindow(max_tokens=max_tokens)
        
        # Prioritize results if requested
        if prioritize:
            results = self.prioritize_results(results)
        
        # Add results to window
        for result in results:
            # Format result
            formatted = self.formatter.format_single_result(result)
            
            # Estimate tokens
            token_estimate = self.estimate_result_tokens(formatted)
            
            # Try to add to window
            if window.can_fit(token_estimate):
                window.add_result(formatted, token_estimate)
            else:
                # Window full
                logger.debug(
                    f"Context window full at {window.usage_percentage:.1f}% "
                    f"({window.used_tokens}/{window.max_tokens} tokens)"
                )
                break
        
        # Add metadata
        window.metadata = {
            "total_results": len(results),
            "included_results": len(window.results),
            "truncated": len(window.results) < len(results),
            "usage_percentage": round(window.usage_percentage, 2)
        }
        
        return window
    
    def prioritize_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Prioritize results for inclusion in context.
        
        Args:
            results: Results to prioritize
            
        Returns:
            Prioritized results
        """
        # Sort by score (highest first)
        prioritized = sorted(results, key=lambda r: r.score, reverse=True)
        
        # Could implement more sophisticated prioritization:
        # - Diversity (avoid too many similar results)
        # - Recency (prefer newer documents)
        # - Source variety (mix different sources)
        
        return prioritized
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        return self.formatter.estimate_tokens(text)
    
    def estimate_result_tokens(self, result: Dict[str, Any]) -> int:
        """Estimate tokens for a formatted result.
        
        Args:
            result: Formatted result dictionary
            
        Returns:
            Estimated token count
        """
        # Convert to string representation
        import json
        result_str = json.dumps(result, separators=(',', ':'))
        
        # Estimate tokens
        return self.estimate_tokens(result_str)
    
    def split_large_results(
        self,
        results: List[SearchResult],
        chunk_size: int = 10
    ) -> List[List[SearchResult]]:
        """Split results into manageable chunks.
        
        Args:
            results: Results to split
            chunk_size: Results per chunk
            
        Returns:
            List of result chunks
        """
        chunks = []
        for i in range(0, len(results), chunk_size):
            chunks.append(results[i:i + chunk_size])
        return chunks
    
    def create_summary_context(
        self,
        results: List[SearchResult],
        max_results: int = 5
    ) -> Dict[str, Any]:
        """Create a summary context for many results.
        
        Args:
            results: All results
            max_results: Maximum detailed results to include
            
        Returns:
            Summary context dictionary
        """
        # Include top results in detail
        detailed_results = results[:max_results]
        
        # Create summary for remaining
        remaining = results[max_results:]
        summary = {
            "detailed_results": [
                self.formatter.format_single_result(r)
                for r in detailed_results
            ],
            "summary": {
                "additional_results": len(remaining),
                "score_range": {
                    "min": min(r.score for r in remaining) if remaining else 0,
                    "max": max(r.score for r in remaining) if remaining else 0
                },
                "sources": list(set(
                    r.document.file_path for r in remaining
                ))[:5]  # Top 5 sources
            }
        }
        
        return summary
    
    def optimize_for_tokens(
        self,
        content: str,
        max_tokens: int,
        preserve_structure: bool = True
    ) -> str:
        """Optimize content to fit within token limit.
        
        Args:
            content: Content to optimize
            max_tokens: Maximum tokens allowed
            preserve_structure: Try to preserve content structure
            
        Returns:
            Optimized content
        """
        current_tokens = self.estimate_tokens(content)
        
        if current_tokens <= max_tokens:
            return content
        
        # Calculate reduction ratio
        reduction_ratio = max_tokens / current_tokens
        
        if preserve_structure:
            # Try to preserve structure by truncating sections
            lines = content.split('\n')
            
            # Keep ratio of lines
            keep_lines = int(len(lines) * reduction_ratio)
            
            # Prioritize beginning and end
            if keep_lines >= 2:
                half = keep_lines // 2
                optimized_lines = lines[:half] + ['...'] + lines[-half:]
            else:
                optimized_lines = lines[:keep_lines]
            
            optimized = '\n'.join(optimized_lines)
        else:
            # Simple truncation
            target_chars = int(len(content) * reduction_ratio)
            optimized = self.formatter.truncate_content(content, target_chars)
        
        return optimized
    
    def get_context_stats(self, window: ContextWindow) -> Dict[str, Any]:
        """Get statistics about a context window.
        
        Args:
            window: Context window
            
        Returns:
            Statistics dictionary
        """
        return {
            "max_tokens": window.max_tokens,
            "used_tokens": window.used_tokens,
            "remaining_tokens": window.remaining_tokens,
            "usage_percentage": window.usage_percentage,
            "result_count": len(window.results),
            "average_tokens_per_result": (
                window.used_tokens / len(window.results)
                if window.results else 0
            )
        }
    
    def create_sliding_windows(
        self,
        results: List[SearchResult],
        window_size: int = 10000,
        overlap: int = 1000
    ) -> List[ContextWindow]:
        """Create sliding context windows for large result sets.
        
        Args:
            results: All results
            window_size: Size of each window in tokens
            overlap: Overlap between windows in tokens
            
        Returns:
            List of context windows
        """
        windows = []
        current_position = 0
        
        while current_position < len(results):
            # Create window starting at current position
            window = ContextWindow(max_tokens=window_size)
            
            # Add results starting from current position
            for i in range(current_position, len(results)):
                result = results[i]
                formatted = self.formatter.format_single_result(result)
                tokens = self.estimate_result_tokens(formatted)
                
                if not window.add_result(formatted, tokens):
                    break
            
            if window.results:
                windows.append(window)
            
            # Move position forward (with overlap)
            if window.results:
                # Calculate how many results to skip
                skip_tokens = window_size - overlap
                skip_results = 0
                token_count = 0
                
                for r in window.results:
                    token_count += self.estimate_result_tokens(r)
                    skip_results += 1
                    if token_count >= skip_tokens:
                        break
                
                current_position += max(1, skip_results)
            else:
                # No results added, move forward by 1
                current_position += 1
        
        return windows