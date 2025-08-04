"""Embedding generation using Google Gemini API."""

import os
import time
from typing import Dict, List, Optional, Union

import numpy as np
import google.generativeai as genai

from vector_db_query.document_processor.base import EmbeddingGenerator
from vector_db_query.document_processor.models import Embedding
from vector_db_query.document_processor.exceptions import (
    EmbeddingError,
    EmbeddingAPIError,
    RateLimitError,
    AuthenticationError,
    InvalidDimensionsError
)
from vector_db_query.utils.config import get_config
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiEmbedder(EmbeddingGenerator):
    """Generates embeddings using Google Gemini API."""
    
    VALID_DIMENSIONS = [768, 1536, 3072]
    DEFAULT_DIMENSIONS = 768
    MODEL_NAME = "embedding-001"
    
    # Task types for different use cases
    TASK_TYPES = {
        "retrieval_document": "RETRIEVAL_DOCUMENT",
        "retrieval_query": "RETRIEVAL_QUERY",
        "semantic_similarity": "SEMANTIC_SIMILARITY",
        "classification": "CLASSIFICATION",
        "clustering": "CLUSTERING"
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        dimensions: Optional[int] = None,
        task_type: Optional[str] = None
    ):
        """Initialize the Gemini embedder.
        
        Args:
            api_key: Google API key (uses env var if not provided)
            dimensions: Embedding dimensions (768, 1536, or 3072)
            task_type: Task type for embeddings
            
        Raises:
            AuthenticationError: If API key is not provided
            InvalidDimensionsError: If dimensions are not valid
        """
        config = get_config()
        
        # Get API key
        self._api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self._api_key:
            raise AuthenticationError(
                "Google API key not provided. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
            
        # Set dimensions
        self._dimensions = dimensions or config.get(
            "embedding.dimensions", 
            self.DEFAULT_DIMENSIONS
        )
        if self._dimensions not in self.VALID_DIMENSIONS:
            raise InvalidDimensionsError(self._dimensions, self.VALID_DIMENSIONS)
            
        # Set task type
        self._task_type = task_type or config.get(
            "embedding.task_type",
            "RETRIEVAL_DOCUMENT"
        )
        if self._task_type not in self.TASK_TYPES.values():
            # Check if it's a key instead of value
            if self._task_type.lower() in self.TASK_TYPES:
                self._task_type = self.TASK_TYPES[self._task_type.lower()]
            else:
                logger.warning(
                    f"Unknown task type: {self._task_type}. "
                    f"Using RETRIEVAL_DOCUMENT"
                )
                self._task_type = "RETRIEVAL_DOCUMENT"
                
        # Initialize client
        try:
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(self.MODEL_NAME)
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Gemini client: {e}")
            
        logger.info(
            f"GeminiEmbedder initialized - Model: {self.MODEL_NAME}, "
            f"Dimensions: {self._dimensions}, Task: {self._task_type}"
        )
        
    def embed_single(self, text: str) -> Embedding:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding object
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        embeddings = self.embed_batch([text])
        return embeddings[0]
        
    def embed_batch(
        self, 
        texts: List[str],
        chunk_ids: Optional[List[str]] = None
    ) -> List[Embedding]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            chunk_ids: Optional list of chunk IDs (generated if not provided)
            
        Returns:
            List of embedding objects
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not texts:
            return []
            
        # Generate chunk IDs if not provided
        if chunk_ids is None:
            chunk_ids = [f"chunk_{i}" for i in range(len(texts))]
        elif len(chunk_ids) != len(texts):
            raise ValueError("Number of chunk IDs must match number of texts")
            
        try:
            # Make API call
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            
            result = genai.embed_content(
                model=f"models/{self.MODEL_NAME}",
                content=texts,
                task_type=self._task_type,
                title="Embedding" if self._task_type == "RETRIEVAL_DOCUMENT" else None
            )
            
            # Process results
            embeddings = []
            for i, embedding_values in enumerate(result['embedding']):
                # Convert to numpy array
                vector = np.array(embedding_values)
                
                # Normalize if not 3072 dimensions
                normalized = self._dimensions == 3072
                if not normalized:
                    norm = np.linalg.norm(vector)
                    if norm > 0:
                        vector = vector / norm
                        normalized = True
                        
                embeddings.append(
                    Embedding(
                        vector=vector,
                        chunk_id=chunk_ids[i],
                        dimensions=self._dimensions,
                        model=self.MODEL_NAME,
                        normalized=normalized
                    )
                )
                
            logger.debug(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            self._handle_api_error(e)
            
    def _handle_api_error(self, error: Exception) -> None:
        """Handle API errors appropriately.
        
        Args:
            error: The exception that occurred
            
        Raises:
            Appropriate embedding error based on the exception
        """
        error_str = str(error)
        
        # Check for rate limit
        if "rate_limit" in error_str.lower() or "quota" in error_str.lower():
            # Try to extract retry time
            retry_after = None
            if hasattr(error, 'retry_after'):
                retry_after = error.retry_after
            raise RateLimitError(
                "Rate limit exceeded. Please wait before retrying.",
                retry_after=retry_after
            )
            
        # Check for authentication
        if "invalid_api_key" in error_str.lower() or "unauthorized" in error_str.lower():
            raise AuthenticationError(
                "Invalid API key. Please check your Google API key."
            )
            
        # Check for invalid request
        if "invalid" in error_str.lower():
            raise EmbeddingAPIError(
                f"Invalid request: {error_str}",
                status_code=400
            )
            
        # Generic API error
        raise EmbeddingAPIError(f"API error: {error_str}")
        
    @property
    def model_name(self) -> str:
        """Get the name of the embedding model."""
        return self.MODEL_NAME
        
    @property
    def dimensions(self) -> int:
        """Get the dimensionality of embeddings."""
        return self._dimensions


class EmbeddingBatcher:
    """Handles batch processing of embeddings with rate limiting."""
    
    def __init__(
        self,
        embedder: EmbeddingGenerator,
        batch_size: int = 100,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """Initialize the batcher.
        
        Args:
            embedder: Embedding generator to use
            batch_size: Number of texts per batch
            retry_attempts: Number of retry attempts for failed batches
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.embedder = embedder
        self.batch_size = batch_size
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
    def process_with_progress(
        self,
        texts: List[str],
        chunk_ids: List[str],
        progress_callback: Optional[callable] = None
    ) -> List[Embedding]:
        """Process texts in batches with progress reporting.
        
        Args:
            texts: List of texts to embed
            chunk_ids: List of chunk IDs
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of embeddings
        """
        if len(texts) != len(chunk_ids):
            raise ValueError("Number of texts must match number of chunk IDs")
            
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        
        for batch_idx in range(0, len(texts), self.batch_size):
            batch_end = min(batch_idx + self.batch_size, len(texts))
            batch_texts = texts[batch_idx:batch_end]
            batch_ids = chunk_ids[batch_idx:batch_end]
            
            # Update progress
            if progress_callback:
                current_batch = batch_idx // self.batch_size + 1
                progress_callback(
                    current=batch_idx,
                    total=len(texts),
                    message=f"Processing batch {current_batch}/{total_batches}"
                )
                
            # Process batch with retries
            embeddings = self._process_batch_with_retry(batch_texts, batch_ids)
            all_embeddings.extend(embeddings)
            
        # Final progress update
        if progress_callback:
            progress_callback(
                current=len(texts),
                total=len(texts),
                message="Embedding generation complete"
            )
            
        return all_embeddings
        
    def _process_batch_with_retry(
        self,
        texts: List[str],
        chunk_ids: List[str]
    ) -> List[Embedding]:
        """Process a batch with retry logic.
        
        Args:
            texts: Batch of texts
            chunk_ids: Batch of chunk IDs
            
        Returns:
            List of embeddings
        """
        last_error = None
        
        for attempt in range(self.retry_attempts):
            try:
                if isinstance(self.embedder, GeminiEmbedder):
                    return self.embedder.embed_batch(texts, chunk_ids)
                else:
                    # For other embedders that don't support chunk_ids
                    embeddings = []
                    for text, chunk_id in zip(texts, chunk_ids):
                        embedding = self.embedder.embed_single(text)
                        # Update chunk_id
                        embedding.chunk_id = chunk_id
                        embeddings.append(embedding)
                    return embeddings
                    
            except RateLimitError as e:
                last_error = e
                # Use suggested retry time if available
                wait_time = e.retry_after or (self.retry_delay * (2 ** attempt))
                logger.warning(
                    f"Rate limit hit. Waiting {wait_time:.1f}s before retry "
                    f"(attempt {attempt + 1}/{self.retry_attempts})"
                )
                time.sleep(wait_time)
                
            except Exception as e:
                last_error = e
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"Batch processing failed: {e}. Retrying in {wait_time:.1f}s "
                        f"(attempt {attempt + 1}/{self.retry_attempts})"
                    )
                    time.sleep(wait_time)
                else:
                    break
                    
        # All retries failed
        raise EmbeddingError(
            f"Failed to process batch after {self.retry_attempts} attempts: {last_error}"
        )