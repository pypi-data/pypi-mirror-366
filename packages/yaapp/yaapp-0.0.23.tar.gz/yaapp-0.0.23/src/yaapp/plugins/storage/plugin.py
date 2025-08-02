"""
Storage plugin for YAAPP framework.
Provides unified storage interface configured through yaapp configuration.
"""

import hashlib
import json
import pickle
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import (Any, Dict, List, Optional, Protocol, Tuple, Union,
                    runtime_checkable)

from yaapp import yaapp


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for storage backends."""
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key."""
        ...
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store value with optional TTL."""
        ...
    
    def delete(self, key: str) -> bool:
        """Delete value by key."""
        ...
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...
    
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """List keys, optionally matching pattern."""
        ...
    
    def clear(self) -> int:
        """Clear all data, return count of items removed."""
        ...
    
    def cleanup_expired(self) -> int:
        """Remove expired items, return count removed."""
        ...


class MemoryStorageBackend:
    """High-performance in-memory storage with TTL support."""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key."""
        with self._lock:
            # Check if expired
            if key in self._expiry:
                if time.time() > self._expiry[key]:
                    self.delete(key)
                    return None
            
            return self._data.get(key)
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store value with optional TTL."""
        with self._lock:
            self._data[key] = value
            
            if ttl_seconds:
                self._expiry[key] = time.time() + ttl_seconds
            elif key in self._expiry:
                del self._expiry[key]
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete value by key."""
        with self._lock:
            existed = key in self._data
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            return existed
    
    def exists(self, key: str) -> bool:
        """Check if key exists and not expired."""
        return self.get(key) is not None
    
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """List keys, optionally matching pattern."""
        with self._lock:
            # Cleanup expired keys first
            now = time.time()
            expired_keys = [k for k, exp in self._expiry.items() if now > exp]
            for key in expired_keys:
                self.delete(key)
            
            keys = list(self._data.keys())
            
            if pattern:
                import fnmatch
                keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]
            
            return keys
    
    def clear(self) -> int:
        """Clear all data, return count of items removed."""
        with self._lock:
            count = len(self._data)
            self._data.clear()
            self._expiry.clear()
            return count
    
    def cleanup_expired(self) -> int:
        """Remove expired items, return count removed."""
        with self._lock:
            now = time.time()
            expired_keys = [k for k, exp in self._expiry.items() if now > exp]
            
            for key in expired_keys:
                self.delete(key)
            
            return len(expired_keys)


class FileStorageBackend:
    """File-based storage with JSON/pickle serialization."""
    
    def __init__(self, storage_dir: str = "./storage", use_pickle: bool = False):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.use_pickle = use_pickle
        self._lock = threading.RLock()
        self.extension = ".pkl" if use_pickle else ".json"
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for key."""
        # Hash key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.storage_dir / f"{key_hash}{self.extension}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value to bytes."""
        if self.use_pickle:
            return pickle.dumps(value)
        else:
            return json.dumps(value, default=str).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to value."""
        if self.use_pickle:
            return pickle.loads(data)
        else:
            return json.loads(data.decode('utf-8'))
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key."""
        with self._lock:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                return None
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Check for metadata (TTL)
                if data.startswith(b'YAPP_META:'):
                    # Extract metadata
                    meta_end = data.find(b'\n')
                    meta_json = data[10:meta_end].decode('utf-8')
                    metadata = json.loads(meta_json)
                    
                    # Check TTL
                    if 'expires_at' in metadata:
                        if time.time() > metadata['expires_at']:
                            self.delete(key)
                            return None
                    
                    # Extract actual data
                    actual_data = data[meta_end + 1:]
                else:
                    actual_data = data
                
                return self._deserialize(actual_data)
            
            except (json.JSONDecodeError, pickle.PickleError, IOError):
                return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store value with optional TTL."""
        with self._lock:
            file_path = self._get_file_path(key)
            
            try:
                data = self._serialize(value)
                
                # Add metadata if TTL specified
                if ttl_seconds:
                    metadata = {
                        'created_at': time.time(),
                        'expires_at': time.time() + ttl_seconds
                    }
                    meta_bytes = f"YAPP_META:{json.dumps(metadata)}\n".encode('utf-8')
                    data = meta_bytes + data
                
                with open(file_path, 'wb') as f:
                    f.write(data)
                
                return True
            
            except (json.JSONEncodeError, pickle.PickleError, IOError):
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value by key."""
        with self._lock:
            file_path = self._get_file_path(key)
            
            if file_path.exists():
                try:
                    file_path.unlink()
                    return True
                except IOError:
                    return False
            
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and not expired."""
        return self.get(key) is not None
    
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """List keys, optionally matching pattern."""
        with self._lock:
            # Note: This is expensive for file storage as we need to read metadata
            # In production, consider maintaining an index
            keys = []
            
            for file_path in self.storage_dir.glob(f"*{self.extension}"):
                # Try to extract original key from file (simplified approach)
                # In practice, you'd maintain a key->hash mapping
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    
                    # Check if expired
                    if data.startswith(b'YAPP_META:'):
                        meta_end = data.find(b'\n')
                        meta_json = data[10:meta_end].decode('utf-8')
                        metadata = json.loads(meta_json)
                        
                        if 'expires_at' in metadata:
                            if time.time() > metadata['expires_at']:
                                file_path.unlink()  # Cleanup expired
                                continue
                    
                    # For simplicity, use filename as key representation
                    key_representation = file_path.stem
                    
                    if pattern:
                        import fnmatch
                        if fnmatch.fnmatch(key_representation, pattern):
                            keys.append(key_representation)
                    else:
                        keys.append(key_representation)
                
                except (json.JSONDecodeError, IOError):
                    pass
            
            return keys
    
    def clear(self) -> int:
        """Clear all data, return count of items removed."""
        with self._lock:
            count = 0
            
            for file_path in self.storage_dir.glob(f"*{self.extension}"):
                try:
                    file_path.unlink()
                    count += 1
                except IOError:
                    pass
            
            return count
    
    def cleanup_expired(self) -> int:
        """Remove expired items, return count removed."""
        with self._lock:
            count = 0
            now = time.time()
            
            for file_path in self.storage_dir.glob(f"*{self.extension}"):
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    
                    if data.startswith(b'YAPP_META:'):
                        meta_end = data.find(b'\n')
                        meta_json = data[10:meta_end].decode('utf-8')
                        metadata = json.loads(meta_json)
                        
                        if 'expires_at' in metadata and now > metadata['expires_at']:
                            file_path.unlink()
                            count += 1
                
                except (json.JSONDecodeError, IOError):
                    pass
            
            return count


class SQLiteStorage:
    """SQLite-based storage for persistent, queryable data."""
    
    def __init__(self, db_path: str = "./storage.db"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at REAL,
                    expires_at REAL NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON storage(expires_at)")
            conn.commit()
            conn.close()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            
            # Check if expired and cleanup
            now = time.time()
            conn.execute("DELETE FROM storage WHERE expires_at IS NOT NULL AND expires_at < ?", (now,))
            
            cursor = conn.execute("SELECT value FROM storage WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                try:
                    return pickle.loads(row[0])
                except pickle.PickleError:
                    return None
            
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store value with optional TTL."""
        with self._lock:
            try:
                serialized_value = pickle.dumps(value)
                now = time.time()
                expires_at = now + ttl_seconds if ttl_seconds else None
                
                conn = sqlite3.connect(self.db_path)
                conn.execute(
                    "INSERT OR REPLACE INTO storage (key, value, created_at, expires_at) VALUES (?, ?, ?, ?)",
                    (key, serialized_value, now, expires_at)
                )
                conn.commit()
                conn.close()
                
                return True
            
            except (pickle.PickleError, sqlite3.Error):
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value by key."""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute("DELETE FROM storage WHERE key = ?", (key,))
                deleted = cursor.rowcount > 0
                conn.commit()
                conn.close()
                
                return deleted
            
            except sqlite3.Error:
                return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and not expired."""
        return self.get(key) is not None
    
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """List keys, optionally matching pattern."""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                
                # Cleanup expired first
                now = time.time()
                conn.execute("DELETE FROM storage WHERE expires_at IS NOT NULL AND expires_at < ?", (now,))
                
                if pattern:
                    cursor = conn.execute("SELECT key FROM storage WHERE key GLOB ?", (pattern,))
                else:
                    cursor = conn.execute("SELECT key FROM storage")
                
                keys = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                return keys
            
            except sqlite3.Error:
                return []
    
    def clear(self) -> int:
        """Clear all data, return count of items removed."""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute("SELECT COUNT(*) FROM storage")
                count = cursor.fetchone()[0]
                conn.execute("DELETE FROM storage")
                conn.commit()
                conn.close()
                
                return count
            
            except sqlite3.Error:
                return 0
    
    def cleanup_expired(self) -> int:
        """Remove expired items, return count removed."""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                now = time.time()
                cursor = conn.execute("DELETE FROM storage WHERE expires_at IS NOT NULL AND expires_at < ?", (now,))
                count = cursor.rowcount
                conn.commit()
                conn.close()
                
                return count
            
            except sqlite3.Error:
                return 0

@yaapp.expose('storage')
class Storage:
    """Storage manager with single backend configured through yaapp config."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
        
        # Get backend configuration
        backend_type = self.config.get('backend', 'memory')
        
        # Create the configured backend
        if backend_type == 'memory':
            self.backend = MemoryStorageBackend()
        elif backend_type == 'file':
            storage_dir = self.config.get('storage_dir', './storage')
            use_pickle = self.config.get('use_pickle', False)
            self.backend = FileStorageBackend(storage_dir, use_pickle)
        elif backend_type == 'sqlite':
            db_path = self.config.get('db_path', './storage.db')
            self.backend = SQLiteStorageBackend(db_path)
        else:
            print(f"Warning: Unknown storage backend '{backend_type}', using memory")
            self.backend = MemoryStorageBackend()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_worker(self):
        """Background cleanup worker."""
        while True:
            try:
                if hasattr(self.backend, 'cleanup_expired'):
                    removed = self.backend.cleanup_expired()
                    if removed > 0:
                        print(f"Storage cleanup: removed {removed} expired items")
            except Exception as e:
                print(f"Storage cleanup error: {e}")
            
            time.sleep(300)  # Cleanup every 5 minutes
    
    def get(self, key: str, namespace: Optional[str] = None) -> Optional[Any]:
        """Retrieve value by key."""
        full_key = f"{namespace}:{key}" if namespace else key
        return self.backend.get(full_key)
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, namespace: Optional[str] = None) -> bool:
        """Store value."""
        full_key = f"{namespace}:{key}" if namespace else key
        return self.backend.set(full_key, value, ttl_seconds)
    
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Delete value."""
        full_key = f"{namespace}:{key}" if namespace else key
        return self.backend.delete(full_key)
    
    def exists(self, key: str, namespace: Optional[str] = None) -> bool:
        """Check if key exists."""
        full_key = f"{namespace}:{key}" if namespace else key
        return self.backend.exists(full_key)
    
    def keys(self, pattern: Optional[str] = None, namespace: Optional[str] = None) -> List[str]:
        """List keys."""
        if namespace:
            namespace_pattern = f"{namespace}:{pattern or '*'}"
            keys = self.backend.keys(namespace_pattern)
            # Remove namespace prefix from returned keys
            return [key[len(namespace)+1:] for key in keys if key.startswith(f"{namespace}:")]
        else:
            return self.backend.keys(pattern)
    
    def clear(self, namespace: Optional[str] = None) -> int:
        """Clear data."""
        if namespace:
            # Clear only keys in namespace
            keys = self.keys(namespace=namespace)
            count = 0
            for key in keys:
                if self.delete(key, namespace=namespace):
                    count += 1
            return count
        else:
            return self.backend.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = {
            'backend_type': type(self.backend).__name__,
            'config': self.config
        }
        
        # Try to get backend-specific stats
        if hasattr(self.backend, '_data'):
            stats['items'] = len(self.backend._data)
        
        if hasattr(self.backend, '_expiry'):
            now = time.time()
            expired_count = sum(1 for exp in self.backend._expiry.values() if now > exp)
            stats['expired_items'] = expired_count
        
        return stats
