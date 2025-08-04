"""Text chunking strategies for document processing."""

import re
import uuid
from typing import List, Optional

from vector_db_query.document_processor.base import ChunkingStrategy
from vector_db_query.document_processor.models import Chunk
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class SlidingWindowChunker(ChunkingStrategy):
    """Chunks text using a sliding window approach with sentence awareness."""
    
    def __init__(self, preserve_sentences: bool = True, min_chunk_size: int = 100):
        """Initialize the chunker.
        
        Args:
            preserve_sentences: Whether to try to preserve sentence boundaries
            min_chunk_size: Minimum size for a chunk
        """
        self.preserve_sentences = preserve_sentences
        self.min_chunk_size = min_chunk_size
        self._sentence_pattern = re.compile(r'[.!?]+\s+')
        
    def chunk(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs
    ) -> List[Chunk]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            **kwargs: Additional parameters (e.g., preserve_sentences)
            
        Returns:
            List of text chunks
        """
        self.validate_parameters(chunk_size, chunk_overlap)
        
        # Clean text
        text = text.strip()
        if not text:
            return []
            
        preserve_sentences = kwargs.get('preserve_sentences', self.preserve_sentences)
        chunks = []
        
        if preserve_sentences:
            chunks = self._chunk_with_sentences(text, chunk_size, chunk_overlap)
        else:
            chunks = self._chunk_simple(text, chunk_size, chunk_overlap)
            
        # Filter out chunks that are too small
        chunks = [c for c in chunks if len(c.text) >= self.min_chunk_size]
        
        logger.debug(f"Created {len(chunks)} chunks from {len(text)} characters")
        return chunks
        
    def _chunk_simple(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Chunk]:
        """Simple sliding window chunking without sentence awareness."""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_id = str(uuid.uuid4())
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        start_pos=start,
                        end_pos=end,
                        chunk_id=chunk_id,
                        chunk_index=chunk_index,
                        metadata={
                            'chunking_method': 'sliding_window_simple',
                            'chunk_size': chunk_size,
                            'overlap': chunk_overlap
                        }
                    )
                )
                chunk_index += 1
                
            # Move window
            if end >= len(text):
                break
            start = end - chunk_overlap
            
        return chunks
        
    def _chunk_with_sentences(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Chunk]:
        """Chunk text while trying to preserve sentence boundaries."""
        chunks = []
        current_pos = 0
        chunk_index = 0
        
        while current_pos < len(text):
            # Find the end position for this chunk
            end_pos = min(current_pos + chunk_size, len(text))
            
            # If we're not at the end of the text, try to find a sentence boundary
            if end_pos < len(text):
                # Look for sentence ending near the chunk boundary
                search_start = max(current_pos, end_pos - 100)  # Look back up to 100 chars
                search_end = min(len(text), end_pos + 50)  # Look ahead up to 50 chars
                search_text = text[search_start:search_end]
                
                # Find all sentence endings in the search area
                sentence_ends = list(self._sentence_pattern.finditer(search_text))
                
                if sentence_ends:
                    # Find the sentence ending closest to our target end position
                    best_end = None
                    best_distance = float('inf')
                    
                    for match in sentence_ends:
                        # Convert match position to absolute position
                        abs_pos = search_start + match.end()
                        distance = abs(abs_pos - end_pos)
                        
                        # Prefer positions that don't exceed chunk_size too much
                        if abs_pos - current_pos <= chunk_size * 1.1:  # Allow 10% overflow
                            if distance < best_distance:
                                best_distance = distance
                                best_end = abs_pos
                                
                    if best_end is not None:
                        end_pos = best_end
                        
            # Extract chunk text
            chunk_text = text[current_pos:end_pos].strip()
            
            if chunk_text:
                chunk_id = str(uuid.uuid4())
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        start_pos=current_pos,
                        end_pos=end_pos,
                        chunk_id=chunk_id,
                        chunk_index=chunk_index,
                        metadata={
                            'chunking_method': 'sliding_window_sentences',
                            'chunk_size': chunk_size,
                            'overlap': chunk_overlap
                        }
                    )
                )
                chunk_index += 1
                
            # Move to next chunk with overlap
            if end_pos >= len(text):
                break
                
            # For overlap, try to start at a sentence beginning
            overlap_start = max(current_pos, end_pos - chunk_overlap)
            
            # Look for sentence start in the overlap region
            search_text = text[overlap_start:end_pos]
            sentence_starts = list(self._sentence_pattern.finditer(search_text))
            
            if sentence_starts:
                # Use the first sentence start in the overlap region
                current_pos = overlap_start + sentence_starts[0].end()
            else:
                current_pos = overlap_start
                
        return chunks


class SemanticChunker(ChunkingStrategy):
    """Chunks text based on semantic boundaries (paragraphs, sections)."""
    
    def __init__(self, min_chunk_size: int = 100):
        """Initialize the semantic chunker.
        
        Args:
            min_chunk_size: Minimum size for a chunk
        """
        self.min_chunk_size = min_chunk_size
        self._paragraph_pattern = re.compile(r'\n\s*\n')
        self._section_pattern = re.compile(r'^#+\s+.*$', re.MULTILINE)
        
    def chunk(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs
    ) -> List[Chunk]:
        """Split text into semantic chunks based on structure.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap (less relevant for semantic)
            **kwargs: Additional parameters
            
        Returns:
            List of text chunks
        """
        self.validate_parameters(chunk_size, chunk_overlap)
        
        text = text.strip()
        if not text:
            return []
            
        # First, try to identify major sections (for markdown)
        sections = self._split_by_sections(text)
        
        chunks = []
        chunk_index = 0
        
        for section in sections:
            # Split each section by paragraphs
            paragraphs = self._split_by_paragraphs(section)
            
            # Combine paragraphs into chunks
            current_chunk_text = ""
            current_start_pos = 0
            
            for i, para in enumerate(paragraphs):
                para_text = para.strip()
                if not para_text:
                    continue
                    
                # If adding this paragraph would exceed chunk size, save current chunk
                if current_chunk_text and len(current_chunk_text) + len(para_text) + 2 > chunk_size:
                    if len(current_chunk_text) >= self.min_chunk_size:
                        chunk_id = str(uuid.uuid4())
                        chunks.append(
                            Chunk(
                                text=current_chunk_text,
                                start_pos=current_start_pos,
                                end_pos=current_start_pos + len(current_chunk_text),
                                chunk_id=chunk_id,
                                chunk_index=chunk_index,
                                metadata={
                                    'chunking_method': 'semantic',
                                    'chunk_size': chunk_size
                                }
                            )
                        )
                        chunk_index += 1
                        
                    current_chunk_text = para_text
                    current_start_pos = text.find(para_text, current_start_pos)
                else:
                    # Add paragraph to current chunk
                    if current_chunk_text:
                        current_chunk_text += "\n\n" + para_text
                    else:
                        current_chunk_text = para_text
                        current_start_pos = text.find(para_text)
                        
            # Don't forget the last chunk
            if current_chunk_text and len(current_chunk_text) >= self.min_chunk_size:
                chunk_id = str(uuid.uuid4())
                chunks.append(
                    Chunk(
                        text=current_chunk_text,
                        start_pos=current_start_pos,
                        end_pos=current_start_pos + len(current_chunk_text),
                        chunk_id=chunk_id,
                        chunk_index=chunk_index,
                        metadata={
                            'chunking_method': 'semantic',
                            'chunk_size': chunk_size
                        }
                    )
                )
                chunk_index += 1
                
        logger.debug(f"Created {len(chunks)} semantic chunks from {len(text)} characters")
        return chunks
        
    def _split_by_sections(self, text: str) -> List[str]:
        """Split text by section headers (markdown style)."""
        # Find all section headers
        headers = list(self._section_pattern.finditer(text))
        
        if not headers:
            return [text]
            
        sections = []
        
        # Add content before first header if any
        if headers[0].start() > 0:
            sections.append(text[:headers[0].start()].strip())
            
        # Extract sections between headers
        for i in range(len(headers)):
            start = headers[i].start()
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            section_text = text[start:end].strip()
            if section_text:
                sections.append(section_text)
                
        return sections
        
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs (double newlines)."""
        paragraphs = self._paragraph_pattern.split(text)
        return [p.strip() for p in paragraphs if p.strip()]