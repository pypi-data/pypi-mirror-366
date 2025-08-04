"""Universal Vector Database Reader - reads from any collection regardless of dimensions."""

from typing import Dict, List, Optional, Union, Generator
from pathlib import Path
import json

from vector_db_query.multi_dim_query import MultiDimensionQuerySystem
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class UniversalVDBReader:
    """Universal reader for vector databases with multi-dimension support."""
    
    def __init__(self):
        """Initialize the universal reader."""
        self.query_system = MultiDimensionQuerySystem()
        
    def read_all_documents(
        self,
        collection_name: str,
        batch_size: int = 100
    ) -> Generator[Dict, None, None]:
        """Read all documents from a collection in batches.
        
        Args:
            collection_name: Name of the collection to read
            batch_size: Number of documents per batch
            
        Yields:
            Document dictionaries
        """
        offset = None
        total_read = 0
        
        try:
            dimension = self.query_system.get_collection_dimension(collection_name)
            logger.info(f"Reading from {collection_name} (dimension={dimension})")
            
            while True:
                documents, next_offset = self.query_system.read_collection(
                    collection_name,
                    limit=batch_size,
                    offset=offset
                )
                
                if not documents:
                    break
                    
                for doc in documents:
                    yield self._format_document(doc)
                    
                total_read += len(documents)
                logger.info(f"Read {total_read} documents so far...")
                
                if next_offset is None:
                    break
                    
                offset = next_offset
                
            logger.info(f"Finished reading {total_read} documents from {collection_name}")
            
        except Exception as e:
            logger.error(f"Error reading collection {collection_name}: {e}")
            raise
            
    def _format_document(self, doc: Dict) -> Dict:
        """Format a document for output."""
        payload = doc.get('payload', {})
        
        # Extract key fields
        formatted = {
            'id': doc.get('id'),
            'collection': doc.get('collection'),
            'content': (
                payload.get('chunk_text') or 
                payload.get('content') or 
                payload.get('text', '')
            ),
            'source': (
                payload.get('source_file') or 
                payload.get('source') or 
                payload.get('file_path', 'Unknown')
            ),
            'metadata': {}
        }
        
        # Add relevant metadata
        metadata_fields = [
            'file_name', 'file_type', 'chunk_index', 'created_at',
            'embedding_model', 'embedding_dimensions'
        ]
        
        for field in metadata_fields:
            if field in payload:
                formatted['metadata'][field] = payload[field]
                
        # Add any custom metadata
        for key, value in payload.items():
            if key not in ['content', 'chunk_text', 'text', 'source', 'source_file']:
                if key not in formatted['metadata']:
                    formatted['metadata'][key] = value
                    
        return formatted
        
    def search_unified(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        limit: int = 5
    ) -> Dict[str, List[Dict]]:
        """Search across collections with unified results.
        
        Args:
            query: Search query
            collections: List of collections to search (None = all)
            limit: Results per collection
            
        Returns:
            Dictionary mapping collection names to results
        """
        if collections:
            # Search specific collections
            results = {}
            for collection in collections:
                try:
                    search_results = self.query_system.search_collection(
                        collection, query, limit
                    )
                    results[collection] = [
                        self._format_search_result(r) for r in search_results
                    ]
                except Exception as e:
                    logger.error(f"Error searching {collection}: {e}")
                    results[collection] = []
        else:
            # Search all collections
            all_results = self.query_system.search_all_collections(query, limit)
            results = {}
            for collection, collection_results in all_results.items():
                if isinstance(collection_results, list) and collection_results:
                    if 'error' not in collection_results[0]:
                        results[collection] = [
                            self._format_search_result(r) for r in collection_results
                        ]
                        
        return results
        
    def _format_search_result(self, result: Dict) -> Dict:
        """Format a search result."""
        formatted = self._format_document(result)
        formatted['score'] = result.get('score', 0.0)
        formatted['dimension'] = result.get('dimension')
        return formatted
        
    def export_collection(
        self,
        collection_name: str,
        output_path: Path,
        format: str = "jsonl"
    ) -> int:
        """Export a collection to a file.
        
        Args:
            collection_name: Collection to export
            output_path: Output file path
            format: Export format (jsonl, json, csv)
            
        Returns:
            Number of documents exported
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        count = 0
        
        if format == "jsonl":
            with open(output_path, 'w', encoding='utf-8') as f:
                for doc in self.read_all_documents(collection_name):
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')
                    count += 1
                    
        elif format == "json":
            documents = list(self.read_all_documents(collection_name))
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False)
            count = len(documents)
            
        elif format == "csv":
            import csv
            documents = list(self.read_all_documents(collection_name))
            if documents:
                # Get all unique keys
                all_keys = set()
                for doc in documents:
                    all_keys.update(doc.keys())
                    if 'metadata' in doc:
                        all_keys.update(f"metadata.{k}" for k in doc['metadata'].keys())
                        
                # Remove metadata from top-level keys
                all_keys.discard('metadata')
                fieldnames = sorted(all_keys)
                
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for doc in documents:
                        row = {k: v for k, v in doc.items() if k != 'metadata'}
                        # Flatten metadata
                        if 'metadata' in doc:
                            for k, v in doc['metadata'].items():
                                row[f"metadata.{k}"] = v
                        writer.writerow(row)
                        count += 1
                        
        logger.info(f"Exported {count} documents to {output_path}")
        return count
        
    def get_statistics(self) -> Dict[str, Dict]:
        """Get statistics for all collections."""
        stats = {}
        collections = self.query_system.get_all_collections()
        
        for collection_name, dimension in collections:
            try:
                info = self.query_system.get_collection_info(collection_name)
                stats[collection_name] = {
                    'dimension': dimension,
                    'vectors_count': info.vectors_count,
                    'points_count': info.points_count,
                    'status': info.status,
                    'indexed_vectors': getattr(info, 'indexed_vectors_count', None)
                }
            except Exception as e:
                logger.error(f"Failed to get stats for {collection_name}: {e}")
                stats[collection_name] = {'error': str(e)}
                
        return stats