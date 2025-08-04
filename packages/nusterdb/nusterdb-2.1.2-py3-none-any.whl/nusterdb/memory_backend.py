"""
Memory Backend for NusterDB
===========================

In-memory vector storage backend optimized for speed.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union
import threading
from threading import RLock

class RWLock:
    """Simple read-write lock implementation."""
    def __init__(self):
        self._read_ready = threading.Condition()
        self._readers = 0
    
    def read_lock(self):
        return self
    
    def write_lock(self):
        return self
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
import time
from collections import defaultdict

from .config import NusterConfig
from .exceptions import NusterDBError

class MemoryBackend:
    """
    Fast in-memory vector storage backend.
    
    Optimized for maximum speed with minimal overhead.
    Data is lost when the process ends.
    """
    
    def __init__(self, config: NusterConfig, dimension: int):
        """Initialize memory backend."""
        self.config = config
        self.dimension = dimension
        
        # Storage
        self._vectors: Dict[Union[int, str], np.ndarray] = {}
        self._metadata: Dict[Union[int, str], Dict[str, Any]] = {}
        self._vector_matrix: Optional[np.ndarray] = None
        self._id_to_index: Dict[Union[int, str], int] = {}
        self._index_to_id: Dict[int, Union[int, str]] = {}
        
        # Thread safety
        self._lock = RLock()
        
        # Stats
        self._stats = {
            "searches": 0,
            "inserts": 0,
            "updates": 0,
            "deletes": 0,
        }
        
        # Index management
        self._needs_rebuild = False
        self._next_index = 0
    
    def _rebuild_matrix(self):
        """Rebuild the vector matrix for efficient search."""
        if not self._vectors:
            self._vector_matrix = None
            return
        
        # Create matrix
        ids = list(self._vectors.keys())
        vectors = [self._vectors[id] for id in ids]
        self._vector_matrix = np.vstack(vectors)
        
        # Update index mappings
        self._id_to_index = {id: i for i, id in enumerate(ids)}
        self._index_to_id = {i: id for i, id in enumerate(ids)}
        
        self._needs_rebuild = False
    
    def add(self, id: Union[int, str], vector: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Add a single vector."""
        with self._lock:
            try:
                # Store vector and metadata
                self._vectors[id] = vector.copy()
                self._metadata[id] = metadata.copy()
                
                # Mark for rebuild
                self._needs_rebuild = True
                self._stats["inserts"] += 1
                
                return True
                
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
                added_count = 0
                
                for i, (id, vector) in enumerate(zip(ids, vectors)):
                    meta = metadata[i] if metadata else {}
                    self._vectors[id] = vector.copy()
                    self._metadata[id] = meta.copy()
                    added_count += 1
                
                self._needs_rebuild = True
                self._stats["inserts"] += added_count
                
                return added_count
                
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
                if not self._vectors:
                    return []
                
                # Rebuild matrix if needed
                if self._needs_rebuild:
                    # Upgrade to write lock for rebuild
                    with self._lock:
                        if self._needs_rebuild:  # Double-check
                            self._rebuild_matrix()
                
                if self._vector_matrix is None:
                    return []
                
                # Calculate distances
                if self.config.distance_metric.value == "l2":
                    distances = np.linalg.norm(self._vector_matrix - query, axis=1)
                elif self.config.distance_metric.value == "cosine":
                    # Cosine similarity -> distance
                    query_norm = np.linalg.norm(query)
                    matrix_norms = np.linalg.norm(self._vector_matrix, axis=1)
                    similarities = np.dot(self._vector_matrix, query) / (matrix_norms * query_norm + 1e-8)
                    distances = 1 - similarities
                elif self.config.distance_metric.value == "inner_product":
                    distances = -np.dot(self._vector_matrix, query)  # Negative for sorting
                else:
                    # Default to L2
                    distances = np.linalg.norm(self._vector_matrix - query, axis=1)
                
                # Get top-k indices
                top_indices = np.argsort(distances)[:k]
                
                # Build results
                results = []
                for idx in top_indices:
                    id = self._index_to_id[idx]
                    
                    # Apply filters
                    if filters and not self._matches_filters(self._metadata.get(id, {}), filters):
                        continue
                    
                    result = {"id": id}
                    
                    if include_distances:
                        result["distance"] = float(distances[idx])
                    
                    if include_metadata:
                        result["metadata"] = self._metadata.get(id, {})
                    
                    results.append(result)
                
                self._stats["searches"] += 1
                return results[:k]  # Ensure we don't exceed k after filtering
                
            except Exception as e:
                raise NusterDBError(f"Search failed: {e}")
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters."""
        for key, expected_value in filters.items():
            if key not in metadata or metadata[key] != expected_value:
                return False
        return True
    
    def update(
        self,
        id: Union[int, str],
        vector: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing vector."""
        with self._lock:
            try:
                if id not in self._vectors:
                    return False
                
                if vector is not None:
                    self._vectors[id] = vector.copy()
                    self._needs_rebuild = True
                
                if metadata is not None:
                    self._metadata[id] = metadata.copy()
                
                self._stats["updates"] += 1
                return True
                
            except Exception as e:
                raise NusterDBError(f"Failed to update vector: {e}")
    
    def delete(self, id: Union[int, str]) -> bool:
        """Delete a vector by ID."""
        with self._lock:
            try:
                if id not in self._vectors:
                    return False
                
                del self._vectors[id]
                if id in self._metadata:
                    del self._metadata[id]
                
                self._needs_rebuild = True
                self._stats["deletes"] += 1
                
                return True
                
            except Exception as e:
                raise NusterDBError(f"Failed to delete vector: {e}")
    
    def get(self, id: Union[int, str], include_metadata: bool = True) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        with self._lock:
            try:
                if id not in self._vectors:
                    return None
                
                result = {
                    "id": id,
                    "vector": self._vectors[id].tolist()
                }
                
                if include_metadata:
                    result["metadata"] = self._metadata.get(id, {})
                
                return result
                
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
                self._vectors.clear()
                self._metadata.clear()
                self._vector_matrix = None
                self._id_to_index.clear()
                self._index_to_id.clear()
                self._needs_rebuild = False
                self._next_index = 0
                
                return True
                
            except Exception as e:
                raise NusterDBError(f"Failed to clear: {e}")
    
    def count(self) -> int:
        """Get total number of vectors."""
        with self._lock:
            return len(self._vectors)
    
    def stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        with self._lock:
            return {
                **self._stats,
                "vector_count": len(self._vectors),
                "memory_usage_vectors": len(self._vectors) * self.dimension * 4,  # 4 bytes per float32
                "needs_rebuild": self._needs_rebuild,
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "healthy": True,
            "backend": "memory",
            "vector_count": len(self._vectors),
            "dimension": self.dimension,
        }
    
    def close(self):
        """Close backend (no-op for memory backend)."""
        pass