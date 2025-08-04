import json
import os
import time
import pickle
from typing import Any, Dict, Optional, Union
from pathlib import Path
from collections import OrderedDict
import threading
import hashlib

class LRUCache:
    """In-memory LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = None):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.access_times = {}
        self.lock = threading.RLock()
    
    def _is_expired(self, key: str) -> bool:
        if self.ttl_seconds is None:
            return False
        if key not in self.access_times:
            return True
        return time.time() - self.access_times[key] > self.ttl_seconds
    
    def _cleanup_expired(self):
        expired_keys = [k for k in self.cache.keys() if self._is_expired(k)]
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            self._cleanup_expired()
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.access_times[key] = time.time()
                return value
            return None
    
    def set(self, key: str, value: Any):
        with self.lock:
            self._cleanup_expired()
            
            if key in self.cache:
                # Update existing
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                oldest_key = next(iter(self.cache))
                self.cache.pop(oldest_key)
                if oldest_key in self.access_times:
                    del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def exists(self, key: str) -> bool:
        with self.lock:
            self._cleanup_expired()
            return key in self.cache
    
    def flush(self):
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def size(self) -> int:
        with self.lock:
            self._cleanup_expired()
            return len(self.cache)

class LFUCache:
    """In-memory LFU cache with frequency counting"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = None):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.frequencies = {}
        self.access_times = {}
        self.lock = threading.RLock()
    
    def _is_expired(self, key: str) -> bool:
        if self.ttl_seconds is None:
            return False
        if key not in self.access_times:
            return True
        return time.time() - self.access_times[key] > self.ttl_seconds
    
    def _cleanup_expired(self):
        expired_keys = [k for k in self.cache.keys() if self._is_expired(k)]
        for key in expired_keys:
            del self.cache[key]
            if key in self.frequencies:
                del self.frequencies[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def _evict_least_frequent(self):
        if not self.cache:
            return
        
        min_freq = min(self.frequencies.values())
        candidates = [k for k, v in self.frequencies.items() if v == min_freq]
        
        # If multiple candidates, remove the oldest
        if len(candidates) > 1:
            oldest_key = min(candidates, key=lambda k: self.access_times.get(k, 0))
            key_to_remove = oldest_key
        else:
            key_to_remove = candidates[0]
        
        del self.cache[key_to_remove]
        del self.frequencies[key_to_remove]
        if key_to_remove in self.access_times:
            del self.access_times[key_to_remove]
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            self._cleanup_expired()
            if key in self.cache:
                self.frequencies[key] = self.frequencies.get(key, 0) + 1
                self.access_times[key] = time.time()
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any):
        with self.lock:
            self._cleanup_expired()
            
            if key in self.cache:
                # Update existing
                self.cache[key] = value
                self.frequencies[key] = self.frequencies.get(key, 0) + 1
            else:
                if len(self.cache) >= self.max_size:
                    self._evict_least_frequent()
                
                self.cache[key] = value
                self.frequencies[key] = 1
            
            self.access_times[key] = time.time()
    
    def exists(self, key: str) -> bool:
        with self.lock:
            self._cleanup_expired()
            return key in self.cache
    
    def flush(self):
        with self.lock:
            self.cache.clear()
            self.frequencies.clear()
            self.access_times.clear()
    
    def size(self) -> int:
        with self.lock:
            self._cleanup_expired()
            return len(self.cache)

class DiskKVStore:
    """Disk-based KV store with TTL support"""
    
    def __init__(self, cache_dir: str = ".cache", ttl_seconds: Optional[int] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.lock = threading.RLock()
    
    def _get_file_path(self, key: str) -> Path:
        # Use hash to avoid filesystem issues with special characters
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"
    
    def _is_expired(self, file_path: Path) -> bool:
        if self.ttl_seconds is None:
            return False
        if not file_path.exists():
            return True
        return time.time() - file_path.stat().st_mtime > self.ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            file_path = self._get_file_path(key)
            if not file_path.exists() or self._is_expired(file_path):
                return None
            
            try:
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            except (pickle.PickleError, EOFError):
                # Corrupted file, remove it
                file_path.unlink(missing_ok=True)
                return None
    
    def set(self, key: str, value: Any):
        with self.lock:
            file_path = self._get_file_path(key)
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(value, f)
            except Exception:
                # Clean up on error
                file_path.unlink(missing_ok=True)
                raise
    
    def exists(self, key: str) -> bool:
        with self.lock:
            file_path = self._get_file_path(key)
            return file_path.exists() and not self._is_expired(file_path)
    
    def flush(self):
        with self.lock:
            for file_path in self.cache_dir.glob("*.pkl"):
                file_path.unlink()
    
    def size(self) -> int:
        with self.lock:
            return len([f for f in self.cache_dir.glob("*.pkl") if not self._is_expired(f)])

class MultiLayerKVStore:
    """Multi-layer KV store with RAM, disk, and Redis support"""
    
    def __init__(self, 
                 memory_cache_type: str = "lru",
                 memory_max_size: int = 1000,
                 memory_ttl: Optional[int] = None,
                 disk_cache_dir: str = ".cache",
                 disk_ttl: Optional[int] = None,
                 redis_config: Optional[Dict] = None,
                 redis_ttl: Optional[int] = None):
        
        # Memory layer
        if memory_cache_type.lower() == "lru":
            self.memory_cache = LRUCache(memory_max_size, memory_ttl)
        elif memory_cache_type.lower() == "lfu":
            self.memory_cache = LFUCache(memory_max_size, memory_ttl)
        else:
            raise ValueError("memory_cache_type must be 'lru' or 'lfu'")
        
        # Disk layer
        self.disk_cache = DiskKVStore(disk_cache_dir, disk_ttl)
        
        # Redis layer (optional)
        self.redis_cache = None
        if redis_config:
            try:
                from .redis_store import RedisKVStore
                self.redis_cache = RedisKVStore(ttl_seconds=redis_ttl, redis_config=redis_config)
            except ImportError:
                print("Warning: Redis not available, skipping Redis layer")
    
    def get(self, key: str) -> Optional[Any]:
        # Try memory first
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # Try disk
        value = self.disk_cache.get(key)
        if value is not None:
            # Promote to memory
            self.memory_cache.set(key, value)
            return value
        
        # Try Redis
        if self.redis_cache:
            value = self.redis_cache.get(key)
            if value is not None:
                # Promote to memory and disk
                self.memory_cache.set(key, value)
                self.disk_cache.set(key, value)
                return value
        
        return None
    
    def set(self, key: str, value: Any):
        # Set in all layers
        self.memory_cache.set(key, value)
        self.disk_cache.set(key, value)
        if self.redis_cache:
            self.redis_cache.set(key, value)
    
    def exists(self, key: str) -> bool:
        return (self.memory_cache.exists(key) or 
                self.disk_cache.exists(key) or 
                (self.redis_cache and self.redis_cache.exists(key)))
    
    def flush(self):
        self.memory_cache.flush()
        self.disk_cache.flush()
        if self.redis_cache:
            self.redis_cache.flush()
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "memory_size": self.memory_cache.size(),
            "disk_size": self.disk_cache.size(),
        }
        if self.redis_cache:
            stats["redis_available"] = True
        else:
            stats["redis_available"] = False
        return stats
