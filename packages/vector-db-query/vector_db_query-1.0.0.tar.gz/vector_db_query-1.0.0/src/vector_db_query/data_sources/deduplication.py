"""Content deduplication system for data sources."""

import hashlib
import re
from typing import Dict, Any, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import json

from .models import ProcessedDocument, DeduplicationResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ContentDeduplicator:
    """Handles content deduplication across data sources."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize deduplicator.
        
        Args:
            cache_dir: Directory for caching deduplication data
        """
        self.cache_dir = cache_dir or Path(".cache/deduplication")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory caches
        self._content_hashes: Dict[str, Set[str]] = {}  # source -> set of hashes
        self._document_index: Dict[str, Dict[str, Any]] = {}  # hash -> document info
        self._similarity_cache: Dict[str, float] = {}  # pair hash -> similarity
        
        # Load persisted cache
        self._load_cache()
    
    def check_duplicate(self, 
                       document: ProcessedDocument,
                       source_type: Optional[str] = None,
                       threshold: float = 0.95) -> DeduplicationResult:
        """Check if a document is a duplicate.
        
        Args:
            document: Document to check
            source_type: Optionally limit check to specific source
            threshold: Similarity threshold for fuzzy matching (0.0-1.0)
            
        Returns:
            DeduplicationResult with duplicate information
        """
        # Generate content hash
        content_hash = self._generate_content_hash(document.content)
        
        # Check for exact duplicate
        if content_hash in self._document_index:
            existing = self._document_index[content_hash]
            return DeduplicationResult(
                is_duplicate=True,
                similarity=1.0,
                duplicate_of=existing['source_id'],
                duplicate_source=existing['source_type'],
                match_type='exact',
                metadata={
                    'existing_title': existing['title'],
                    'existing_date': existing['processed_at']
                }
            )
        
        # Check for near duplicates using fuzzy matching
        similar_docs = self._find_similar_documents(
            document,
            source_type=source_type,
            threshold=threshold
        )
        
        if similar_docs:
            best_match = similar_docs[0]  # Sorted by similarity
            return DeduplicationResult(
                is_duplicate=True,
                similarity=best_match['similarity'],
                duplicate_of=best_match['source_id'],
                duplicate_source=best_match['source_type'],
                match_type='fuzzy',
                metadata={
                    'existing_title': best_match['title'],
                    'existing_date': best_match['processed_at'],
                    'match_details': best_match.get('match_details', {})
                }
            )
        
        # No duplicate found
        return DeduplicationResult(
            is_duplicate=False,
            similarity=0.0,
            duplicate_of=None,
            duplicate_source=None,
            match_type='none'
        )
    
    def register_document(self, document: ProcessedDocument):
        """Register a document in the deduplication system.
        
        Args:
            document: Document to register
        """
        # Generate content hash
        content_hash = self._generate_content_hash(document.content)
        
        # Add to source-specific hash set
        source_type = document.source_type
        if source_type not in self._content_hashes:
            self._content_hashes[source_type] = set()
        self._content_hashes[source_type].add(content_hash)
        
        # Add to document index
        self._document_index[content_hash] = {
            'source_id': document.source_id,
            'source_type': document.source_type,
            'title': document.title,
            'processed_at': document.processed_at.isoformat(),
            'content_length': len(document.content),
            'metadata': self._extract_key_metadata(document)
        }
        
        # Persist cache periodically
        if len(self._document_index) % 100 == 0:
            self._save_cache()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content.
        
        Args:
            content: Content to hash
            
        Returns:
            SHA-256 hash of normalized content
        """
        # Normalize content for consistent hashing
        normalized = self._normalize_content(content)
        
        # Generate SHA-256 hash
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for consistent comparison.
        
        Args:
            content: Content to normalize
            
        Returns:
            Normalized content
        """
        # Convert to lowercase
        normalized = content.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove timestamps (various formats)
        normalized = re.sub(r'\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?', '', normalized)
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}', '', normalized)
        
        # Remove common variations
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        
        return normalized.strip()
    
    def _find_similar_documents(self,
                              document: ProcessedDocument,
                              source_type: Optional[str] = None,
                              threshold: float = 0.95) -> List[Dict[str, Any]]:
        """Find similar documents using fuzzy matching.
        
        Args:
            document: Document to compare
            source_type: Optionally limit to specific source
            threshold: Similarity threshold
            
        Returns:
            List of similar documents sorted by similarity
        """
        similar_docs = []
        
        # Determine which sources to check
        sources_to_check = [source_type] if source_type else list(self._content_hashes.keys())
        
        # Extract key features from the document
        doc_features = self._extract_features(document)
        
        # Check against existing documents
        for source in sources_to_check:
            for content_hash in self._content_hashes.get(source, set()):
                existing_info = self._document_index.get(content_hash, {})
                
                # Skip if same document
                if existing_info.get('source_id') == document.source_id:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(
                    doc_features,
                    existing_info,
                    document.metadata,
                    existing_info.get('metadata', {})
                )
                
                if similarity >= threshold:
                    similar_docs.append({
                        'source_id': existing_info['source_id'],
                        'source_type': existing_info['source_type'],
                        'title': existing_info['title'],
                        'processed_at': existing_info['processed_at'],
                        'similarity': similarity,
                        'match_details': {
                            'content_length_ratio': (
                                len(document.content) / existing_info['content_length']
                                if existing_info.get('content_length', 0) > 0 else 0
                            )
                        }
                    })
        
        # Sort by similarity descending
        similar_docs.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_docs
    
    def _extract_features(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Extract key features from a document for comparison.
        
        Args:
            document: Document to analyze
            
        Returns:
            Feature dictionary
        """
        content = document.content
        metadata = document.metadata
        
        features = {
            'length': len(content),
            'word_count': len(content.split()),
            'title_words': set(document.title.lower().split()),
            'content_preview': content[:500].lower(),
            'has_attachments': bool(metadata.get('attachments')),
            'source_type': document.source_type
        }
        
        # Extract type-specific features
        if document.source_type == 'gmail':
            features['sender'] = metadata.get('sender', '').lower()
            features['subject_keywords'] = set(
                re.findall(r'\w+', metadata.get('subject', '').lower())
            )
        
        elif document.source_type == 'fireflies':
            features['meeting_id'] = metadata.get('meeting_id')
            features['duration'] = metadata.get('duration')
            features['participants'] = set(
                p.lower() for p in metadata.get('participants', [])
            )
        
        elif document.source_type == 'google_drive':
            features['file_type'] = metadata.get('transcript_type')
            features['tab_count'] = metadata.get('tab_count', 0)
            features['has_action_items'] = bool(
                metadata.get('structured_data', {}).get('action_items')
            )
        
        return features
    
    def _calculate_similarity(self,
                            doc1_features: Dict[str, Any],
                            doc2_info: Dict[str, Any],
                            doc1_metadata: Dict[str, Any],
                            doc2_metadata: Dict[str, Any]) -> float:
        """Calculate similarity between two documents.
        
        Args:
            doc1_features: Features of first document
            doc2_info: Info about second document
            doc1_metadata: Metadata of first document
            doc2_metadata: Metadata of second document
            
        Returns:
            Similarity score (0.0-1.0)
        """
        scores = []
        
        # Content length similarity
        if doc2_info.get('content_length'):
            length_ratio = min(
                doc1_features['length'] / doc2_info['content_length'],
                doc2_info['content_length'] / doc1_features['length']
            )
            scores.append(length_ratio)
        
        # Title similarity
        if 'title_words' in doc1_features and doc2_info.get('title'):
            title2_words = set(doc2_info['title'].lower().split())
            if title2_words:
                jaccard = len(doc1_features['title_words'] & title2_words) / len(
                    doc1_features['title_words'] | title2_words
                )
                scores.append(jaccard)
        
        # Source-specific similarity
        if doc1_features.get('source_type') == doc2_info.get('source_type'):
            source_score = self._calculate_source_specific_similarity(
                doc1_features, doc1_metadata, doc2_metadata
            )
            if source_score is not None:
                scores.append(source_score)
        
        # Return average similarity
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_source_specific_similarity(self,
                                            features: Dict[str, Any],
                                            metadata1: Dict[str, Any],
                                            metadata2: Dict[str, Any]) -> Optional[float]:
        """Calculate source-specific similarity.
        
        Args:
            features: Features of document 1
            metadata1: Metadata of document 1
            metadata2: Metadata of document 2
            
        Returns:
            Similarity score or None
        """
        source_type = features.get('source_type')
        
        if source_type == 'gmail':
            # Check sender and subject similarity
            if (metadata1.get('sender', '').lower() == metadata2.get('sender', '').lower() and
                'subject_keywords' in features):
                subject2_words = set(
                    re.findall(r'\w+', metadata2.get('subject', '').lower())
                )
                if subject2_words:
                    return len(features['subject_keywords'] & subject2_words) / len(
                        features['subject_keywords'] | subject2_words
                    )
        
        elif source_type == 'fireflies':
            # Check meeting ID and participants
            if features.get('meeting_id') == metadata2.get('meeting_id'):
                return 1.0
            
            # Check participant overlap
            if 'participants' in features and metadata2.get('participants'):
                participants2 = set(p.lower() for p in metadata2['participants'])
                if participants2:
                    return len(features['participants'] & participants2) / len(
                        features['participants'] | participants2
                    )
        
        elif source_type == 'google_drive':
            # Check structured data similarity
            struct1 = metadata1.get('structured_data', {})
            struct2 = metadata2.get('structured_data', {})
            
            if struct1.get('meeting_title') == struct2.get('meeting_title'):
                return 0.95
            
            # Check action items overlap
            actions1 = set(str(a) for a in struct1.get('action_items', []))
            actions2 = set(str(a) for a in struct2.get('action_items', []))
            if actions1 and actions2:
                return len(actions1 & actions2) / len(actions1 | actions2)
        
        return None
    
    def _extract_key_metadata(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Extract key metadata for storage.
        
        Args:
            document: Document to process
            
        Returns:
            Key metadata dictionary
        """
        metadata = {}
        
        if document.source_type == 'gmail':
            metadata['sender'] = document.metadata.get('sender')
            metadata['subject'] = document.metadata.get('subject')
            metadata['date'] = document.metadata.get('date')
        
        elif document.source_type == 'fireflies':
            metadata['meeting_id'] = document.metadata.get('meeting_id')
            metadata['participants'] = document.metadata.get('participants', [])
            metadata['duration'] = document.metadata.get('duration')
        
        elif document.source_type == 'google_drive':
            metadata['file_id'] = document.metadata.get('file_id')
            metadata['transcript_type'] = document.metadata.get('transcript_type')
            metadata['tab_count'] = document.metadata.get('tab_count')
            
            # Extract key structured data
            structured = document.metadata.get('structured_data', {})
            if structured:
                metadata['structured_data'] = {
                    'meeting_title': structured.get('meeting_title'),
                    'action_items': structured.get('action_items', [])[:5]  # First 5
                }
        
        return metadata
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get deduplication statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_documents': len(self._document_index),
            'sources': {}
        }
        
        # Per-source statistics
        for source, hashes in self._content_hashes.items():
            stats['sources'][source] = {
                'unique_documents': len(hashes),
                'total_registered': sum(
                    1 for doc in self._document_index.values()
                    if doc['source_type'] == source
                )
            }
        
        # Cache statistics
        stats['cache'] = {
            'similarity_cache_size': len(self._similarity_cache),
            'cache_directory': str(self.cache_dir)
        }
        
        return stats
    
    def _load_cache(self):
        """Load persisted cache from disk."""
        cache_file = self.cache_dir / "dedup_cache.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Restore document index
                self._document_index = cache_data.get('document_index', {})
                
                # Rebuild content hashes by source
                for doc_hash, doc_info in self._document_index.items():
                    source_type = doc_info['source_type']
                    if source_type not in self._content_hashes:
                        self._content_hashes[source_type] = set()
                    self._content_hashes[source_type].add(doc_hash)
                
                logger.info(f"Loaded deduplication cache with {len(self._document_index)} documents")
                
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")
    
    def _save_cache(self):
        """Save cache to disk."""
        cache_file = self.cache_dir / "dedup_cache.json"
        
        try:
            cache_data = {
                'document_index': self._document_index,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Saved deduplication cache with {len(self._document_index)} documents")
            
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def cleanup_old_entries(self, days: int = 90):
        """Remove old entries from the cache.
        
        Args:
            days: Remove entries older than this many days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        removed_count = 0
        
        # Find entries to remove
        to_remove = []
        for doc_hash, doc_info in self._document_index.items():
            try:
                processed_at = datetime.fromisoformat(doc_info['processed_at'])
                if processed_at < cutoff_date:
                    to_remove.append((doc_hash, doc_info['source_type']))
            except:
                pass
        
        # Remove old entries
        for doc_hash, source_type in to_remove:
            del self._document_index[doc_hash]
            if source_type in self._content_hashes:
                self._content_hashes[source_type].discard(doc_hash)
            removed_count += 1
        
        # Save updated cache
        if removed_count > 0:
            self._save_cache()
            logger.info(f"Cleaned up {removed_count} old entries from deduplication cache")
        
        return removed_count