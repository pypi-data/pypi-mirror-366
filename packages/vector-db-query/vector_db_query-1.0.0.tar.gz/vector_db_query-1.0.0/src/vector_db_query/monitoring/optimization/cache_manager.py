"""
Advanced caching system for performance optimization.
"""

import os
import time
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, Union, Tuple, List
from threading import RLock
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import OrderedDict
import sqlite3


class CacheLevel(Enum):
    """Cache storage levels."""
    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"


class CacheStrategy(Enum):
    """Cache replacement strategies."""
    LRU = "lru"        # Least Recently Used
    LFU = "lfu"        # Least Frequently Used
    FIFO = "fifo"      # First In First Out
    TTL = "ttl"        # Time To Live based


@dataclass
class CacheEntry:
    """Individual cache entry."""
    key: str
    value: Any
    size_bytes: int
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry_time
    
    def access(self) -> None:
        """Record an access to this entry."""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'hit_rate': self.hit_rate,
            'total_size_bytes': self.total_size_bytes,
            'entry_count': self.entry_count
        }


class CacheManager:
    """
    Advanced caching system with multiple levels and strategies.
    """
    
    def __init__(self, 
                 data_dir: str = None,
                 max_memory_size_mb: int = 100,
                 max_disk_size_mb: int = 1000,
                 default_ttl_seconds: int = 3600,
                 strategy: CacheStrategy = CacheStrategy.LRU):
        """Initialize cache manager."""
        self._lock = RLock()
        self.data_dir = data_dir or os.path.join(os.getcwd(), ".data", "cache")
        self.max_memory_size = max_memory_size_mb * 1024 * 1024  # Convert to bytes
        self.max_disk_size = max_disk_size_mb * 1024 * 1024
        self.default_ttl_seconds = default_ttl_seconds
        self.strategy = strategy
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Memory cache (OrderedDict for LRU)
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Disk cache database
        self.db_path = os.path.join(self.data_dir, "cache.db")
        self._init_disk_cache()
        
        # Statistics
        self.stats = CacheStats()
        
        # Cache invalidation callbacks
        self._invalidation_callbacks: List[Callable[[str], None]] = []
    
    def _init_disk_cache(self) -> None:
        """Initialize disk cache database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER NOT NULL,
                    ttl_seconds INTEGER,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_cache_lru ON cache_entries (last_accessed)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_cache_size ON cache_entries (size_bytes)
            ''')
            
            conn.commit()
    
    def get(self, key: str, level: CacheLevel = CacheLevel.MEMORY) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            cache_key = self._generate_key(key)
            
            # Try memory cache first
            if level == CacheLevel.MEMORY or level == CacheLevel.DISTRIBUTED:
                entry = self.memory_cache.get(cache_key)
                if entry:
                    if not entry.is_expired():
                        entry.access()
                        # Move to end for LRU
                        if self.strategy == CacheStrategy.LRU:
                            self.memory_cache.move_to_end(cache_key)
                        self.stats.hits += 1
                        return entry.value
                    else:
                        # Remove expired entry
                        del self.memory_cache[cache_key]
                        self.stats.evictions += 1
            
            # Try disk cache
            if level in [CacheLevel.DISK, CacheLevel.DISTRIBUTED]:
                entry = self._get_from_disk(cache_key)
                if entry:
                    if not entry.is_expired():
                        self._update_disk_access(cache_key)
                        self.stats.hits += 1
                        
                        # Promote to memory cache if space available
                        if self._get_memory_usage() + entry.size_bytes <= self.max_memory_size:
                            self.memory_cache[cache_key] = entry
                        
                        return entry.value
                    else:
                        # Remove expired entry
                        self._delete_from_disk(cache_key)
                        self.stats.evictions += 1
            
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None,
            level: CacheLevel = CacheLevel.MEMORY, metadata: Dict[str, Any] = None) -> bool:
        """Set value in cache."""
        with self._lock:
            cache_key = self._generate_key(key)
            
            # Calculate size
            size_bytes = self._calculate_size(value)
            
            # Create entry
            entry = CacheEntry(
                key=cache_key,
                value=value,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds or self.default_ttl_seconds,
                metadata=metadata or {}
            )
            
            # Store in appropriate level
            if level == CacheLevel.MEMORY:
                # Check memory size and evict if needed
                self._ensure_memory_capacity(size_bytes)
                self.memory_cache[cache_key] = entry
                self.stats.entry_count += 1
                self.stats.total_size_bytes += size_bytes
                
            elif level == CacheLevel.DISK:
                # Check disk size and evict if needed
                self._ensure_disk_capacity(size_bytes)
                self._save_to_disk(entry)
                
            elif level == CacheLevel.DISTRIBUTED:
                # Store in both memory and disk
                self._ensure_memory_capacity(size_bytes)
                self._ensure_disk_capacity(size_bytes)
                self.memory_cache[cache_key] = entry
                self._save_to_disk(entry)
                self.stats.entry_count += 1
                self.stats.total_size_bytes += size_bytes
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self._lock:
            cache_key = self._generate_key(key)
            deleted = False
            
            # Delete from memory
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                del self.memory_cache[cache_key]
                self.stats.entry_count -= 1
                self.stats.total_size_bytes -= entry.size_bytes
                deleted = True
            
            # Delete from disk
            if self._delete_from_disk(cache_key):
                deleted = True
            
            # Notify callbacks
            if deleted:
                for callback in self._invalidation_callbacks:
                    try:
                        callback(key)
                    except Exception:
                        pass
            
            return deleted
    
    def clear(self, level: Optional[CacheLevel] = None) -> None:
        """Clear cache at specified level or all levels."""
        with self._lock:
            if level is None or level == CacheLevel.MEMORY:
                self.memory_cache.clear()
                self.stats.entry_count = 0
                self.stats.total_size_bytes = 0
            
            if level is None or level == CacheLevel.DISK:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM cache_entries")
                    conn.commit()
    
    def _generate_key(self, key: str) -> str:
        """Generate cache key hash."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes."""
        try:
            return len(pickle.dumps(value))
        except:
            # Fallback for non-picklable objects
            return len(str(value).encode())
    
    def _get_memory_usage(self) -> int:
        """Get current memory cache usage in bytes."""
        return sum(entry.size_bytes for entry in self.memory_cache.values())
    
    def _get_disk_usage(self) -> int:
        """Get current disk cache usage in bytes."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(size_bytes) FROM cache_entries")
            result = cursor.fetchone()[0]
            return result or 0
    
    def _ensure_memory_capacity(self, required_bytes: int) -> None:
        """Ensure memory cache has capacity for new entry."""
        current_usage = self._get_memory_usage()
        
        while current_usage + required_bytes > self.max_memory_size and self.memory_cache:
            # Evict based on strategy
            if self.strategy == CacheStrategy.LRU:
                # Remove least recently used (first item)
                key, entry = self.memory_cache.popitem(last=False)
            elif self.strategy == CacheStrategy.FIFO:
                # Remove oldest (first item)
                key, entry = self.memory_cache.popitem(last=False)
            elif self.strategy == CacheStrategy.LFU:
                # Remove least frequently used
                key = min(self.memory_cache, key=lambda k: self.memory_cache[k].access_count)
                entry = self.memory_cache.pop(key)
            else:  # TTL
                # Remove oldest expired or oldest overall
                expired_keys = [k for k, e in self.memory_cache.items() if e.is_expired()]
                if expired_keys:
                    key = expired_keys[0]
                else:
                    key, entry = self.memory_cache.popitem(last=False)
                entry = self.memory_cache.pop(key, None)
            
            if entry:
                current_usage -= entry.size_bytes
                self.stats.evictions += 1
                self.stats.entry_count -= 1
                self.stats.total_size_bytes -= entry.size_bytes
    
    def _ensure_disk_capacity(self, required_bytes: int) -> None:
        """Ensure disk cache has capacity for new entry."""
        current_usage = self._get_disk_usage()
        
        while current_usage + required_bytes > self.max_disk_size:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Select entry to evict based on strategy
                if self.strategy == CacheStrategy.LRU:
                    cursor.execute("""
                        SELECT key, size_bytes FROM cache_entries 
                        ORDER BY last_accessed ASC LIMIT 1
                    """)
                elif self.strategy == CacheStrategy.LFU:
                    cursor.execute("""
                        SELECT key, size_bytes FROM cache_entries 
                        ORDER BY access_count ASC LIMIT 1
                    """)
                else:  # FIFO or TTL
                    cursor.execute("""
                        SELECT key, size_bytes FROM cache_entries 
                        ORDER BY created_at ASC LIMIT 1
                    """)
                
                result = cursor.fetchone()
                if result:
                    key, size = result
                    cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                    conn.commit()
                    current_usage -= size
                    self.stats.evictions += 1
                else:
                    break
    
    def _save_to_disk(self, entry: CacheEntry) -> None:
        """Save entry to disk cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache_entries 
                (key, value, size_bytes, created_at, last_accessed, access_count, ttl_seconds, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.key,
                pickle.dumps(entry.value),
                entry.size_bytes,
                entry.created_at.isoformat(),
                entry.last_accessed.isoformat(),
                entry.access_count,
                entry.ttl_seconds,
                json.dumps(entry.metadata)
            ))
            
            conn.commit()
    
    def _get_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Get entry from disk cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value, size_bytes, created_at, last_accessed, access_count, ttl_seconds, metadata
                FROM cache_entries WHERE key = ?
            ''', (key,))
            
            result = cursor.fetchone()
            if result:
                value, size_bytes, created_at, last_accessed, access_count, ttl_seconds, metadata = result
                
                entry = CacheEntry(
                    key=key,
                    value=pickle.loads(value),
                    size_bytes=size_bytes,
                    created_at=datetime.fromisoformat(created_at),
                    last_accessed=datetime.fromisoformat(last_accessed),
                    access_count=access_count,
                    ttl_seconds=ttl_seconds,
                    metadata=json.loads(metadata) if metadata else {}
                )
                
                return entry
            
            return None
    
    def _update_disk_access(self, key: str) -> None:
        """Update access time and count for disk entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE cache_entries 
                SET last_accessed = ?, access_count = access_count + 1
                WHERE key = ?
            ''', (datetime.now().isoformat(), key))
            
            conn.commit()
    
    def _delete_from_disk(self, key: str) -> bool:
        """Delete entry from disk cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            return CacheStats(
                hits=self.stats.hits,
                misses=self.stats.misses,
                evictions=self.stats.evictions,
                total_size_bytes=self.stats.total_size_bytes,
                entry_count=self.stats.entry_count
            )
    
    def add_invalidation_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for cache invalidation events."""
        with self._lock:
            self._invalidation_callbacks.append(callback)
    
    def remove_invalidation_callback(self, callback: Callable[[str], None]) -> None:
        """Remove invalidation callback."""
        with self._lock:
            if callback in self._invalidation_callbacks:
                self._invalidation_callbacks.remove(callback)
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries."""
        with self._lock:
            cleaned = 0
            
            # Clean memory cache
            expired_keys = [k for k, e in self.memory_cache.items() if e.is_expired()]
            for key in expired_keys:
                entry = self.memory_cache.pop(key)
                self.stats.entry_count -= 1
                self.stats.total_size_bytes -= entry.size_bytes
                self.stats.evictions += 1
                cleaned += 1
            
            # Clean disk cache
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find expired entries
                cursor.execute('''
                    SELECT key FROM cache_entries 
                    WHERE ttl_seconds IS NOT NULL 
                    AND datetime(created_at, '+' || ttl_seconds || ' seconds') < datetime('now')
                ''')
                
                expired_disk_keys = [row[0] for row in cursor.fetchall()]
                
                if expired_disk_keys:
                    placeholders = ','.join(['?' for _ in expired_disk_keys])
                    cursor.execute(f"DELETE FROM cache_entries WHERE key IN ({placeholders})", expired_disk_keys)
                    conn.commit()
                    cleaned += len(expired_disk_keys)
                    self.stats.evictions += len(expired_disk_keys)
            
            return cleaned


# Global cache manager instance
_cache_manager = None
_cache_lock = RLock()


def get_cache_manager(data_dir: str = None, **kwargs) -> CacheManager:
    """
    Get the global cache manager instance (singleton).
    
    Args:
        data_dir: Optional data directory
        **kwargs: Additional configuration parameters
    
    Returns:
        Global cache manager instance
    """
    global _cache_manager
    with _cache_lock:
        if _cache_manager is None:
            _cache_manager = CacheManager(data_dir=data_dir, **kwargs)
        return _cache_manager


def reset_cache_manager() -> None:
    """Reset the global cache manager (mainly for testing)."""
    global _cache_manager
    with _cache_lock:
        if _cache_manager:
            _cache_manager.clear()
        _cache_manager = None