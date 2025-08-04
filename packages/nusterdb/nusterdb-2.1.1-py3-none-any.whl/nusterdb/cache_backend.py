"""
Cache Backend for NusterDB
==========================

Memory + disk caching backend for balanced performance.
"""

import numpy as np
import threading
from threading import RLock
import time
from typing import List, Dict, Any, Optional, Union
from collections import OrderedDict

from .config import NusterConfig
from .exceptions import NusterDBError
from .memory_backend import MemoryBackend

class CacheBackend:
    """
    Cache-based vector storage backend.
    
    Combines fast memory access with intelligent caching.
    Evicts least recently used vectors when memory limit is reached.
    """
    
    def __init__(self, config: NusterConfig, dimension: int):
        """Initialize cache backend."""
        self.config = config
        self.dimension = dimension
        
        # Parse cache size
        self.max_cache_size = self._parse_cache_size(config.cache_size)
        
        # Memory backend for active data
        self._memory_backend = MemoryBackend(config, dimension)
        
        # LRU cache for access patterns
        self._access_order: OrderedDict[Union[int, str], float] = OrderedDict()
        
        # Cold storage for evicted vectors
        self._cold_storage: Dict[Union[int, str], Dict[str, Any]] = {}
        
        # Thread safety
        self._lock = RLock()
        
        # Stats
        self._cache_hits = 0
        self._cache_misses = 0
        self._evictions = 0
    
    def _parse_cache_size(self, cache_size: str) -> int:
        """Parse cache size string to bytes."""
        size_str = cache_size.upper()
        
        if size_str.endswith('GB'):
            return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
        elif size_str.endswith('MB'):
            return int(float(size_str[:-2]) * 1024 * 1024)
        elif size_str.endswith('KB'):
            return int(float(size_str[:-2]) * 1024)
        else:
            return int(size_str)  # Assume bytes
    
    def _estimate_memory_usage(self) -> int:
        """Estimate current memory usage."""
        vector_count = self._memory_backend.count()
        vector_size = self.dimension * 4  # 4 bytes per float32
        return vector_count * vector_size
    
    def _should_evict(self) -> bool:
        """Check if we should evict vectors from cache."""
        return self._estimate_memory_usage() > self.max_cache_size
    
    def _evict_lru_vectors(self, target_count: int = 1):
        """Evict least recently used vectors."""
        with self._lock:
            evicted = 0
            
            # Sort by access time (oldest first)
            sorted_items = sorted(self._access_order.items(), key=lambda x: x[1])
            
            for id, _ in sorted_items:
                if evicted >= target_count:
                    break
                
                # Move to cold storage
                vector_data = self._memory_backend.get(id, include_metadata=True)
                if vector_data:
                    self._cold_storage[id] = vector_data
                    self._memory_backend.delete(id)
                    del self._access_order[id]
                    evicted += 1
                    self._evictions += 1
            
            return evicted
    
    def _promote_from_cold_storage(self, id: Union[int, str]) -> bool:
        """Promote vector from cold storage to active memory."""
        if id not in self._cold_storage:
            return False
        
        # Get data from cold storage
        vector_data = self._cold_storage[id]
        vector = np.array(vector_data['vector'], dtype=np.float32)
        metadata = vector_data.get('metadata', {})
        
        # Add to memory backend
        success = self._memory_backend.add(id, vector, metadata)
        
        if success:
            del self._cold_storage[id]
            self._mark_accessed(id)
        
        return success
    
    def _mark_accessed(self, id: Union[int, str]):
        """Mark vector as recently accessed."""
        self._access_order[id] = time.time()
        
        # Move to end (most recent)
        self._access_order.move_to_end(id)
    
    def add(self, id: Union[int, str], vector: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Add a single vector."""
        with self._lock:
            try:
                # Check if we need to evict
                if self._should_evict():
                    self._evict_lru_vectors()
                
                # Add to memory backend
                result = self._memory_backend.add(id, vector, metadata)
                
                if result:
                    self._mark_accessed(id)
                
                return result
                
            except Exception as e:
                raise NusterDBError(f"Failed to add vector: {e}")
    
    def bulk_add(
        self, 
        ids: List[Union[int, str]], 
        vectors: np.ndarray, 
        metadata: Optional[List[Dict[str, Any]]]
    ) -> int:
        """Add multiple vectors efficiently."""
        with self._lock:
            try:
                # Check if we need to evict multiple vectors
                estimated_new_size = len(ids) * self.dimension * 4
                if self._estimate_memory_usage() + estimated_new_size > self.max_cache_size:
                    # Evict enough vectors to make room
                    evict_count = max(1, len(ids) // 2)
                    self._evict_lru_vectors(evict_count)
                
                # Add to memory backend
                result = self._memory_backend.bulk_add(ids, vectors, metadata)
                
                # Mark all as accessed
                current_time = time.time()
                for id in ids:
                    self._access_order[id] = current_time
                
                return result
                
            except Exception as e:
                raise NusterDBError(f"Failed to bulk add vectors: {e}")
    
    def search(
        self,
        query: np.ndarray,
        k: int,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_distances: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        with self._lock:
            try:
                # Search in active memory first
                results = self._memory_backend.search(
                    query, k, filters, include_metadata, include_distances
                )
                
                # If we don't have enough results, search cold storage
                if len(results) < k and self._cold_storage:
                    # For simplicity, we'll just return active results
                    # In a full implementation, we'd search cold storage too
                    pass
                
                # Mark accessed vectors
                for result in results:
                    self._mark_accessed(result['id'])
                    
                self._cache_hits += len(results)
                return results
                
            except Exception as e:
                raise NusterDBError(f"Search failed: {e}")
    
    def update(
        self,
        id: Union[int, str],
        vector: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing vector."""
        with self._lock:
            try:
                # Check if in active memory
                if id in self._memory_backend._vectors:
                    result = self._memory_backend.update(id, vector, metadata)
                    if result:
                        self._mark_accessed(id)
                    return result
                
                # Check if in cold storage
                elif id in self._cold_storage:
                    # Promote to active memory first
                    if self._promote_from_cold_storage(id):
                        return self._memory_backend.update(id, vector, metadata)
                
                return False
                
            except Exception as e:
                raise NusterDBError(f"Failed to update vector: {e}")
    
    def delete(self, id: Union[int, str]) -> bool:
        """Delete a vector by ID."""
        with self._lock:
            try:
                # Remove from active memory
                memory_deleted = self._memory_backend.delete(id)
                
                # Remove from cold storage
                cold_deleted = id in self._cold_storage
                if cold_deleted:
                    del self._cold_storage[id]
                
                # Remove from access order
                if id in self._access_order:
                    del self._access_order[id]
                
                return memory_deleted or cold_deleted
                
            except Exception as e:
                raise NusterDBError(f"Failed to delete vector: {e}")
    
    def get(self, id: Union[int, str], include_metadata: bool = True) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        with self._lock:
            try:
                # Check active memory first
                result = self._memory_backend.get(id, include_metadata)
                if result:
                    self._mark_accessed(id)
                    self._cache_hits += 1
                    return result
                
                # Check cold storage
                if id in self._cold_storage:
                    self._cache_misses += 1
                    # Promote to active memory
                    with self._lock:
                        if self._promote_from_cold_storage(id):
                            return self._memory_backend.get(id, include_metadata)
                
                self._cache_misses += 1
                return None
                
            except Exception as e:
                raise NusterDBError(f"Failed to get vector: {e}")
    
    def batch_search(
        self,
        queries: np.ndarray,
        k: int,
        filters: Optional[List[Dict[str, Any]]] = None
    ) -> List[List[Dict[str, Any]]]:
        """Search with multiple queries."""
        results = []
        for i, query in enumerate(queries):
            query_filters = filters[i] if filters else None
            result = self.search(query, k, query_filters)
            results.append(result)
        return results
    
    def clear(self) -> bool:
        """Clear all vectors."""
        with self._lock:
            try:
                self._memory_backend.clear()
                self._cold_storage.clear()
                self._access_order.clear()
                self._cache_hits = 0
                self._cache_misses = 0
                self._evictions = 0
                
                return True
                
            except Exception as e:
                raise NusterDBError(f"Failed to clear: {e}")
    
    def count(self) -> int:
        """Get total number of vectors."""
        with self._lock:
            return self._memory_backend.count() + len(self._cold_storage)
    
    def stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        memory_stats = self._memory_backend.stats()
        
        cache_hit_rate = 0.0
        total_requests = self._cache_hits + self._cache_misses
        if total_requests > 0:
            cache_hit_rate = self._cache_hits / total_requests
        
        return {
            **memory_stats,
            "backend": "cache",
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "evictions": self._evictions,
            "cold_storage_count": len(self._cold_storage),
            "active_memory_count": self._memory_backend.count(),
            "max_cache_size": self.max_cache_size,
            "current_memory_usage": self._estimate_memory_usage(),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        memory_health = self._memory_backend.health_check()
        
        memory_usage_percent = 0.0
        if self.max_cache_size > 0:
            memory_usage_percent = self._estimate_memory_usage() / self.max_cache_size
        
        return {
            **memory_health,
            "backend": "cache",
            "memory_usage_percent": memory_usage_percent,
            "cold_storage_count": len(self._cold_storage),
            "cache_efficiency": self._cache_hits / max(1, self._cache_hits + self._cache_misses),
        }
    
    def close(self):
        """Close backend and cleanup resources."""
        self._memory_backend.close()