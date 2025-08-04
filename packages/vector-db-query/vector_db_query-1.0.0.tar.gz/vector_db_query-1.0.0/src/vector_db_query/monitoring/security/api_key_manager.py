"""
API Key Manager for secure key management and authentication.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from threading import RLock
from pathlib import Path

from .api_key_models import APIKey, APIKeyStatus, APIKeyScope, APIKeyPermission, PERMISSION_SETS
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class APIKeyManager:
    """
    Manages API keys for secure access to monitoring dashboard.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize API key manager."""
        self._lock = RLock()
        self.data_dir = data_dir or os.path.join(os.getcwd(), ".data", "monitoring")
        self.db_path = os.path.join(self.data_dir, "api_keys.db")
        self.change_tracker = get_change_tracker()
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # In-memory cache for active keys
        self._key_cache: Dict[str, APIKey] = {}
        self._load_active_keys()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for API keys."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    key_hash TEXT NOT NULL,
                    key_prefix TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    last_used_at TEXT,
                    revoked_at TEXT,
                    revoked_by TEXT,
                    revoked_reason TEXT,
                    created_by TEXT NOT NULL,
                    owner_email TEXT,
                    owner_name TEXT,
                    data_json TEXT NOT NULL
                )
            ''')
            
            # Usage statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_key_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_id TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    response_time_ms INTEGER,
                    bytes_transferred INTEGER DEFAULT 0,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (key_id) REFERENCES api_keys (key_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_keys_status ON api_keys (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_keys_created_by ON api_keys (created_by)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_key_id ON api_key_usage (key_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON api_key_usage (timestamp)')
            
            conn.commit()
    
    def _load_active_keys(self) -> None:
        """Load active API keys into memory cache."""
        with self._lock:
            active_keys = self.list_api_keys(status_filter=APIKeyStatus.ACTIVE)
            self._key_cache = {key.key_hash: key for key in active_keys}
    
    def create_api_key(self,
                      name: str,
                      description: str = "",
                      scopes: List[APIKeyScope] = None,
                      permissions: List[APIKeyPermission] = None,
                      permission_set: str = None,
                      expires_days: int = 90,
                      owner_email: str = None,
                      owner_name: str = None,
                      allowed_ips: List[str] = None,
                      created_by: str = "system") -> Tuple[APIKey, str]:
        """
        Create a new API key.
        
        Args:
            name: Human-readable name for the key
            description: Description of the key's purpose
            scopes: List of scopes to grant
            permissions: List of specific permissions
            permission_set: Predefined permission set ('read_only', 'operator', 'developer', 'admin')
            expires_days: Number of days until expiration (0 = never expires)
            owner_email: Email of the key owner
            owner_name: Name of the key owner
            allowed_ips: List of allowed IP addresses
            created_by: Who created the key
            
        Returns:
            Tuple of (APIKey instance, actual key string)
        """
        with self._lock:
            # Generate the actual API key
            api_key_string = APIKey.generate_key()
            
            # Create API key instance
            api_key = APIKey(
                name=name,
                description=description,
                scopes=set(scopes or []),
                permissions=set(permissions or []),
                owner_email=owner_email,
                owner_name=owner_name,
                allowed_ips=allowed_ips or [],
                created_by=created_by
            )
            
            # Set the key (this hashes it and sets prefix)
            api_key.set_key(api_key_string)
            
            # Apply permission set if specified
            if permission_set and permission_set in PERMISSION_SETS:
                api_key.permissions.update(PERMISSION_SETS[permission_set])
            
            # Set expiration
            if expires_days > 0:
                api_key.expires_at = datetime.now() + timedelta(days=expires_days)
            
            # Save to database
            self._save_api_key(api_key)
            
            # Add to cache
            self._key_cache[api_key.key_hash] = api_key
            
            # Track change
            self.change_tracker.track_change(
                change_type=ChangeType.CREATE,
                category=ChangeCategory.SECURITY,
                entity_id=api_key.key_id,
                description=f"Created API key: {name}",
                metadata={
                    'key_name': name,
                    'created_by': created_by,
                    'scopes': [s.value for s in api_key.scopes],
                    'permission_count': len(api_key.permissions)
                }
            )
            
            return api_key, api_key_string
    
    def _save_api_key(self, api_key: APIKey) -> None:
        """Save API key to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO api_keys (
                    key_id, name, description, key_hash, key_prefix,
                    status, created_at, expires_at, last_used_at,
                    revoked_at, revoked_by, revoked_reason,
                    created_by, owner_email, owner_name, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                api_key.key_id,
                api_key.name,
                api_key.description,
                api_key.key_hash,
                api_key.key_prefix,
                api_key.status.value,
                api_key.created_at.isoformat(),
                api_key.expires_at.isoformat() if api_key.expires_at else None,
                api_key.last_used_at.isoformat() if api_key.last_used_at else None,
                api_key.revoked_at.isoformat() if api_key.revoked_at else None,
                api_key.revoked_by,
                api_key.revoked_reason,
                api_key.created_by,
                api_key.owner_email,
                api_key.owner_name,
                json.dumps(api_key.to_dict())
            ))
            
            conn.commit()
    
    def authenticate_api_key(self, api_key_string: str, ip_address: str = None) -> Optional[APIKey]:
        """
        Authenticate an API key and return the APIKey instance if valid.
        
        Args:
            api_key_string: The raw API key string
            ip_address: Client IP address for IP restrictions
            
        Returns:
            APIKey instance if valid, None otherwise
        """
        with self._lock:
            key_hash = APIKey.hash_key(api_key_string)
            
            # Check cache first
            if key_hash in self._key_cache:
                api_key = self._key_cache[key_hash]
                
                # Verify key is still active
                if not api_key.is_active():
                    # Remove from cache if no longer active
                    del self._key_cache[key_hash]
                    return None
                
                # Check IP restrictions
                if ip_address and not api_key.can_access_ip(ip_address):
                    return None
                
                # Update last used
                api_key.last_used_at = datetime.now()
                self._save_api_key(api_key)
                
                return api_key
            
            # If not in cache, try to load from database
            api_key = self.get_api_key_by_hash(key_hash)
            if api_key and api_key.is_active():
                # Add to cache
                self._key_cache[key_hash] = api_key
                
                # Check IP restrictions
                if ip_address and not api_key.can_access_ip(ip_address):
                    return None
                
                # Update last used
                api_key.last_used_at = datetime.now()
                self._save_api_key(api_key)
                
                return api_key
            
            return None
    
    def get_api_key_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """Get API key by hash."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT data_json FROM api_keys WHERE key_hash = ?', (key_hash,))
            row = cursor.fetchone()
            
            if row:
                data = json.loads(row[0])
                return APIKey.from_dict(data)
            
            return None
    
    def get_api_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT data_json FROM api_keys WHERE key_id = ?', (key_id,))
            row = cursor.fetchone()
            
            if row:
                data = json.loads(row[0])
                return APIKey.from_dict(data)
            
            return None
    
    def list_api_keys(self,
                     status_filter: APIKeyStatus = None,
                     created_by: str = None,
                     owner_email: str = None,
                     limit: int = 100) -> List[APIKey]:
        """List API keys with optional filters."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT data_json FROM api_keys WHERE 1=1'
            params = []
            
            if status_filter:
                query += ' AND status = ?'
                params.append(status_filter.value)
            
            if created_by:
                query += ' AND created_by = ?'
                params.append(created_by)
            
            if owner_email:
                query += ' AND owner_email = ?'
                params.append(owner_email)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [APIKey.from_dict(json.loads(row[0])) for row in rows]
    
    def revoke_api_key(self, key_id: str, revoked_by: str, reason: str = "Manual revocation") -> bool:
        """Revoke an API key."""
        with self._lock:
            api_key = self.get_api_key(key_id)
            if not api_key:
                return False
            
            api_key.revoke(revoked_by, reason)
            self._save_api_key(api_key)
            
            # Remove from cache
            if api_key.key_hash in self._key_cache:
                del self._key_cache[api_key.key_hash]
            
            # Track change
            self.change_tracker.track_change(
                change_type=ChangeType.DELETE,
                category=ChangeCategory.SECURITY,
                entity_id=key_id,
                description=f"Revoked API key: {api_key.name}",
                metadata={
                    'revoked_by': revoked_by,
                    'reason': reason
                }
            )
            
            return True
    
    def suspend_api_key(self, key_id: str, reason: str = "Suspended by admin") -> bool:
        """Suspend an API key."""
        with self._lock:
            api_key = self.get_api_key(key_id)
            if not api_key:
                return False
            
            api_key.suspend(reason)
            self._save_api_key(api_key)
            
            # Remove from cache
            if api_key.key_hash in self._key_cache:
                del self._key_cache[api_key.key_hash]
            
            # Track change
            self.change_tracker.track_change(
                change_type=ChangeType.UPDATE,
                category=ChangeCategory.SECURITY,
                entity_id=key_id,
                description=f"Suspended API key: {api_key.name}",
                metadata={'reason': reason}
            )
            
            return True
    
    def activate_api_key(self, key_id: str) -> bool:
        """Activate a suspended API key."""
        with self._lock:
            api_key = self.get_api_key(key_id)
            if not api_key:
                return False
            
            api_key.activate()
            self._save_api_key(api_key)
            
            # Add to cache if active
            if api_key.is_active():
                self._key_cache[api_key.key_hash] = api_key
            
            # Track change
            self.change_tracker.track_change(
                change_type=ChangeType.UPDATE,
                category=ChangeCategory.SECURITY,
                entity_id=key_id,
                description=f"Activated API key: {api_key.name}"
            )
            
            return True
    
    def update_api_key(self, key_id: str, **updates) -> bool:
        """Update API key properties."""
        with self._lock:
            api_key = self.get_api_key(key_id)
            if not api_key:
                return False
            
            # Track what changed
            changes = []
            
            # Update allowed fields
            if 'name' in updates:
                api_key.name = updates['name']
                changes.append('name')
            
            if 'description' in updates:
                api_key.description = updates['description']
                changes.append('description')
            
            if 'owner_email' in updates:
                api_key.owner_email = updates['owner_email']
                changes.append('owner_email')
            
            if 'owner_name' in updates:
                api_key.owner_name = updates['owner_name']
                changes.append('owner_name')
            
            if 'allowed_ips' in updates:
                api_key.allowed_ips = updates['allowed_ips']
                changes.append('allowed_ips')
            
            if 'allowed_origins' in updates:
                api_key.allowed_origins = updates['allowed_origins']
                changes.append('allowed_origins')
            
            if 'scopes' in updates:
                api_key.scopes = set(updates['scopes'])
                changes.append('scopes')
            
            if 'permissions' in updates:
                api_key.permissions = set(updates['permissions'])
                changes.append('permissions')
            
            if 'expires_at' in updates:
                api_key.expires_at = updates['expires_at']
                changes.append('expires_at')
            
            if changes:
                self._save_api_key(api_key)
                
                # Update cache
                if api_key.key_hash in self._key_cache:
                    self._key_cache[api_key.key_hash] = api_key
                
                # Track change
                self.change_tracker.track_change(
                    change_type=ChangeType.UPDATE,
                    category=ChangeCategory.SECURITY,
                    entity_id=key_id,
                    description=f"Updated API key: {api_key.name}",
                    metadata={'fields_changed': changes}
                )
            
            return True
    
    def record_usage(self,
                    key_id: str,
                    endpoint: str,
                    method: str,
                    status_code: int,
                    response_time_ms: int = 0,
                    bytes_transferred: int = 0,
                    ip_address: str = None,
                    user_agent: str = None) -> None:
        """Record API key usage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_key_usage (
                    key_id, endpoint, method, status_code,
                    response_time_ms, bytes_transferred,
                    ip_address, user_agent, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                key_id, endpoint, method, status_code,
                response_time_ms, bytes_transferred,
                ip_address, user_agent,
                datetime.now().isoformat()
            ))
            
            conn.commit()
        
        # Update API key usage stats
        api_key = self.get_api_key(key_id)
        if api_key:
            api_key.usage_stats.add_request(
                endpoint, 
                status_code < 400, 
                bytes_transferred
            )
            self._save_api_key(api_key)
            
            # Update cache
            if api_key.key_hash in self._key_cache:
                self._key_cache[api_key.key_hash] = api_key
    
    def get_usage_statistics(self, key_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for an API key."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get usage for the last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as failed_requests,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(bytes_transferred) as total_bytes,
                    endpoint,
                    COUNT(*) as endpoint_requests
                FROM api_key_usage 
                WHERE key_id = ? AND timestamp >= ?
                GROUP BY endpoint
                ORDER BY endpoint_requests DESC
            ''', (key_id, cutoff_date.isoformat()))
            
            endpoint_stats = cursor.fetchall()
            
            # Get overall stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as failed_requests,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(bytes_transferred) as total_bytes
                FROM api_key_usage 
                WHERE key_id = ? AND timestamp >= ?
            ''', (key_id, cutoff_date.isoformat()))
            
            overall_stats = cursor.fetchone()
            
            return {
                'key_id': key_id,
                'period_days': days,
                'overall': {
                    'total_requests': overall_stats[0] or 0,
                    'successful_requests': overall_stats[1] or 0,
                    'failed_requests': overall_stats[2] or 0,
                    'success_rate': (overall_stats[1] / overall_stats[0] * 100) if overall_stats[0] else 0,
                    'avg_response_time_ms': overall_stats[3] or 0,
                    'total_bytes_transferred': overall_stats[4] or 0
                },
                'by_endpoint': [
                    {
                        'endpoint': row[5],
                        'requests': row[6],
                        'success_rate': (row[1] / row[0] * 100) if row[0] else 0
                    }
                    for row in endpoint_stats
                ]
            }
    
    def cleanup_expired_keys(self) -> int:
        """Clean up expired API keys."""
        with self._lock:
            now = datetime.now()
            expired_count = 0
            
            # Get all expired keys
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT key_id FROM api_keys 
                    WHERE expires_at IS NOT NULL 
                    AND expires_at < ? 
                    AND status = ?
                ''', (now.isoformat(), APIKeyStatus.ACTIVE.value))
                
                expired_key_ids = [row[0] for row in cursor.fetchall()]
            
            # Update status to expired
            for key_id in expired_key_ids:
                api_key = self.get_api_key(key_id)
                if api_key:
                    api_key.status = APIKeyStatus.EXPIRED
                    self._save_api_key(api_key)
                    
                    # Remove from cache
                    if api_key.key_hash in self._key_cache:
                        del self._key_cache[api_key.key_hash]
                    
                    expired_count += 1
            
            if expired_count > 0:
                self.change_tracker.track_change(
                    change_type=ChangeType.DELETE,
                    category=ChangeCategory.SECURITY,
                    entity_id="system",
                    description=f"Cleaned up {expired_count} expired API keys"
                )
            
            return expired_count
    
    def get_api_key_statistics(self) -> Dict[str, Any]:
        """Get overall API key statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count by status
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM api_keys 
                GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # Total usage in last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            cursor.execute('''
                SELECT COUNT(*) 
                FROM api_key_usage 
                WHERE timestamp >= ?
            ''', (cutoff_date.isoformat(),))
            recent_usage = cursor.fetchone()[0]
            
            # Most active keys
            cursor.execute('''
                SELECT ak.name, ak.key_id, COUNT(aku.id) as request_count
                FROM api_keys ak
                LEFT JOIN api_key_usage aku ON ak.key_id = aku.key_id
                WHERE aku.timestamp >= ?
                GROUP BY ak.key_id
                ORDER BY request_count DESC
                LIMIT 10
            ''', (cutoff_date.isoformat(),))
            most_active = [
                {'name': row[0], 'key_id': row[1], 'requests': row[2]}
                for row in cursor.fetchall()
            ]
            
            return {
                'total_keys': sum(status_counts.values()),
                'by_status': status_counts,
                'active_keys': status_counts.get(APIKeyStatus.ACTIVE.value, 0),
                'recent_usage_30_days': recent_usage,
                'most_active_keys': most_active
            }


# Global manager instance
_api_key_manager = None
_manager_lock = RLock()


def get_api_key_manager() -> APIKeyManager:
    """
    Get the global API key manager instance (singleton).
    
    Returns:
        Global API key manager instance
    """
    global _api_key_manager
    with _manager_lock:
        if _api_key_manager is None:
            _api_key_manager = APIKeyManager()
        return _api_key_manager


def reset_api_key_manager() -> None:
    """Reset the global API key manager (mainly for testing)."""
    global _api_key_manager
    with _manager_lock:
        _api_key_manager = None