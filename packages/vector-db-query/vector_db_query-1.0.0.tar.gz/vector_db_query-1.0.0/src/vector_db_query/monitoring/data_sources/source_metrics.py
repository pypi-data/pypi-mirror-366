"""Metrics collection for data sources."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import json

from ...data_sources.models import SourceType, SyncStatus
from ...data_sources.database import get_db_manager
from ...data_sources.orchestrator import DataSourceOrchestrator
from ...utils.logger import get_logger

logger = get_logger(__name__)


class DataSourceMetrics:
    """Collects and provides metrics for data sources."""
    
    def __init__(self, orchestrator: Optional[DataSourceOrchestrator] = None):
        """Initialize metrics collector.
        
        Args:
            orchestrator: Data source orchestrator instance
        """
        self.orchestrator = orchestrator
        self.db_manager = get_db_manager()
        self._metrics_cache = {}
        self._cache_ttl = 60  # Cache for 60 seconds
        self._last_cache_update = None
    
    async def get_source_metrics(self, source_type: Optional[SourceType] = None) -> Dict[str, Any]:
        """Get metrics for data sources.
        
        Args:
            source_type: Specific source type or None for all
            
        Returns:
            Dict containing metrics
        """
        # Check cache
        if self._should_use_cache():
            return self._metrics_cache
        
        metrics = {}
        
        # Get metrics from database
        async with self.db_manager.get_async_session() as session:
            # Overall statistics
            overall_stats = await self._get_overall_stats(session)
            metrics['overall'] = overall_stats
            
            # Per-source metrics
            if source_type:
                source_metrics = await self._get_source_stats(session, source_type)
                metrics[source_type.value] = source_metrics
            else:
                # Get metrics for all source types
                for st in SourceType:
                    source_metrics = await self._get_source_stats(session, st)
                    metrics[st.value] = source_metrics
        
        # Get runtime metrics from orchestrator if available
        if self.orchestrator:
            try:
                runtime_metrics = await self.orchestrator.get_metrics()
                for source, data in runtime_metrics.items():
                    if source in metrics:
                        metrics[source].update(data)
                    else:
                        metrics[source] = data
            except Exception as e:
                logger.error(f"Failed to get runtime metrics: {e}")
        
        # Update cache
        self._metrics_cache = metrics
        self._last_cache_update = datetime.utcnow()
        
        return metrics
    
    def _should_use_cache(self) -> bool:
        """Check if cache is still valid."""
        if not self._last_cache_update:
            return False
        
        age = (datetime.utcnow() - self._last_cache_update).total_seconds()
        return age < self._cache_ttl
    
    async def _get_overall_stats(self, session) -> Dict[str, Any]:
        """Get overall statistics across all sources."""
        # Use raw SQL for efficiency
        query = """
        SELECT 
            COUNT(*) as total_items,
            COUNT(DISTINCT source_type) as active_sources,
            SUM(CASE WHEN process_status = 'completed' THEN 1 ELSE 0 END) as completed_items,
            SUM(CASE WHEN process_status = 'failed' THEN 1 ELSE 0 END) as failed_items,
            SUM(CASE WHEN process_status = 'pending' THEN 1 ELSE 0 END) as pending_items,
            MIN(created_at) as first_sync,
            MAX(created_at) as last_sync
        FROM data_sources
        """
        
        result = await session.execute(query)
        row = result.first()
        
        return {
            'total_items': row.total_items or 0,
            'active_sources': row.active_sources or 0,
            'completed_items': row.completed_items or 0,
            'failed_items': row.failed_items or 0,
            'pending_items': row.pending_items or 0,
            'first_sync': row.first_sync.isoformat() if row.first_sync else None,
            'last_sync': row.last_sync.isoformat() if row.last_sync else None,
            'success_rate': (row.completed_items / row.total_items * 100) if row.total_items > 0 else 0
        }
    
    async def _get_source_stats(self, session, source_type: SourceType) -> Dict[str, Any]:
        """Get statistics for a specific source."""
        # Get item counts
        item_query = """
        SELECT 
            COUNT(*) as total_items,
            SUM(CASE WHEN process_status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN process_status = 'failed' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN process_status = 'pending' THEN 1 ELSE 0 END) as pending,
            MAX(fetch_timestamp) as last_fetch
        FROM data_sources
        WHERE source_type = :source_type
        """
        
        result = await session.execute(
            item_query,
            {"source_type": source_type.value}
        )
        item_stats = result.first()
        
        # Get sync state
        sync_query = """
        SELECT 
            last_sync_timestamp,
            is_active,
            error_count,
            last_error,
            configuration
        FROM sync_state
        WHERE source_type = :source_type
        """
        
        result = await session.execute(
            sync_query,
            {"source_type": source_type.value}
        )
        sync_state = result.first()
        
        # Get recent activity (last 24 hours)
        recent_query = """
        SELECT 
            DATE_TRUNC('hour', fetch_timestamp) as hour,
            COUNT(*) as count
        FROM data_sources
        WHERE source_type = :source_type
          AND fetch_timestamp > :since
        GROUP BY hour
        ORDER BY hour
        """
        
        since = datetime.utcnow() - timedelta(hours=24)
        result = await session.execute(
            recent_query,
            {"source_type": source_type.value, "since": since}
        )
        
        activity_by_hour = [
            {"hour": row.hour.isoformat(), "count": row.count}
            for row in result
        ]
        
        return {
            'total_items': item_stats.total_items or 0,
            'completed': item_stats.completed or 0,
            'failed': item_stats.failed or 0,
            'pending': item_stats.pending or 0,
            'last_fetch': item_stats.last_fetch.isoformat() if item_stats.last_fetch else None,
            'sync_state': {
                'last_sync': sync_state.last_sync_timestamp.isoformat() if sync_state and sync_state.last_sync_timestamp else None,
                'is_active': sync_state.is_active if sync_state else False,
                'error_count': sync_state.error_count if sync_state else 0,
                'last_error': sync_state.last_error if sync_state else None
            } if sync_state else None,
            'activity_24h': activity_by_hour,
            'success_rate': (item_stats.completed / item_stats.total_items * 100) if item_stats.total_items > 0 else 0
        }
    
    async def get_sync_history(self, source_type: SourceType, hours: int = 24) -> List[Dict[str, Any]]:
        """Get sync history for a source.
        
        Args:
            source_type: Source to get history for
            hours: Number of hours to look back
            
        Returns:
            List of sync events
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        async with self.db_manager.get_async_session() as session:
            query = """
            SELECT 
                fetch_timestamp,
                process_status,
                COUNT(*) as item_count
            FROM data_sources
            WHERE source_type = :source_type
              AND fetch_timestamp > :since
            GROUP BY fetch_timestamp, process_status
            ORDER BY fetch_timestamp DESC
            """
            
            result = await session.execute(
                query,
                {"source_type": source_type.value, "since": since}
            )
            
            return [
                {
                    "timestamp": row.fetch_timestamp.isoformat(),
                    "status": row.process_status,
                    "items": row.item_count
                }
                for row in result
            ]
    
    async def get_error_summary(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get summary of recent errors across all sources.
        
        Returns:
            Dict mapping source types to error lists
        """
        errors = defaultdict(list)
        
        async with self.db_manager.get_async_session() as session:
            # Get recent failed items
            query = """
            SELECT 
                source_type,
                source_id,
                metadata,
                updated_at
            FROM data_sources
            WHERE process_status = 'failed'
              AND updated_at > :since
            ORDER BY updated_at DESC
            LIMIT 50
            """
            
            since = datetime.utcnow() - timedelta(hours=24)
            result = await session.execute(query, {"since": since})
            
            for row in result:
                error_info = {
                    "source_id": row.source_id,
                    "timestamp": row.updated_at.isoformat(),
                    "error": row.metadata.get("error", "Unknown error") if row.metadata else "Unknown error"
                }
                errors[row.source_type].append(error_info)
            
            # Get sync errors
            sync_query = """
            SELECT 
                source_type,
                last_error,
                last_error_timestamp
            FROM sync_state
            WHERE last_error IS NOT NULL
              AND last_error_timestamp > :since
            """
            
            result = await session.execute(sync_query, {"since": since})
            
            for row in result:
                error_info = {
                    "source_id": "sync_error",
                    "timestamp": row.last_error_timestamp.isoformat(),
                    "error": row.last_error
                }
                errors[row.source_type].append(error_info)
        
        return dict(errors)
    
    def format_metrics_summary(self, metrics: Dict[str, Any]) -> str:
        """Format metrics into a human-readable summary.
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            Formatted summary string
        """
        lines = []
        
        # Overall summary
        if 'overall' in metrics:
            overall = metrics['overall']
            lines.append("=== Overall Summary ===")
            lines.append(f"Total Items: {overall.get('total_items', 0):,}")
            lines.append(f"Active Sources: {overall.get('active_sources', 0)}")
            lines.append(f"Success Rate: {overall.get('success_rate', 0):.1f}%")
            lines.append("")
        
        # Per-source summary
        for source_type in SourceType:
            if source_type.value in metrics:
                source_data = metrics[source_type.value]
                lines.append(f"=== {source_type.value.title()} ===")
                lines.append(f"Total: {source_data.get('total_items', 0):,}")
                lines.append(f"Completed: {source_data.get('completed', 0):,}")
                lines.append(f"Failed: {source_data.get('failed', 0):,}")
                lines.append(f"Pending: {source_data.get('pending', 0):,}")
                
                if source_data.get('sync_state'):
                    sync = source_data['sync_state']
                    status = "Active" if sync.get('is_active') else "Inactive"
                    lines.append(f"Status: {status}")
                    if sync.get('error_count', 0) > 0:
                        lines.append(f"Errors: {sync['error_count']}")
                
                lines.append("")
        
        return "\n".join(lines)