"""
NusterDB Core - Unified Vector Database Interface
================================================

A single, unified interface for all vector database operations with multiple modes.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple, Iterator
import tempfile
import os
import json
import threading
import time
from pathlib import Path

from .config import NusterConfig, Algorithm, SecurityLevel, StorageMode, DistanceMetric
from .exceptions import NusterDBError, SecurityError, IndexError, ConfigurationError
from .client import NusterClient
from .memory_backend import MemoryBackend
from .persistent_backend import PersistentBackend
from .cache_backend import CacheBackend
from .utils import validate_vectors, normalize_vector

class NusterDB:
    """
    Unified NusterDB interface supporting all storage modes and algorithms.
    
    This single class handles:
    - Memory-only storage (fastest)
    - Persistent storage (durable)
    - Cache-based storage (balanced)
    - API-based storage (distributed)
    
    Examples:
        # Memory mode - fastest for temporary data
        >>> db = NusterDB(mode="memory", dimension=128)
        
        # Persistent mode - durable storage
        >>> db = NusterDB(mode="persistent", path="./vectors", dimension=768)
        
        # Cache mode - balanced performance  
        >>> db = NusterDB(mode="cache", cache_size="1GB", dimension=512)
        
        # API mode - connect to server
        >>> db = NusterDB(mode="api", url="http://localhost:7878")
        
        # Advanced configuration
        >>> db = NusterDB(
        ...     mode="persistent",
        ...     path="./secure_vectors", 
        ...     dimension=1024,
        ...     algorithm="ivf",
        ...     security_level="government",
        ...     use_gpu=True,
        ...     parallel_processing=True
        ... )
    """
    
    def __init__(
        self,
        mode: Union[str, StorageMode] = "memory",
        dimension: Optional[int] = None,
        path: Optional[str] = None,
        url: Optional[str] = None,
        algorithm: Union[str, Algorithm] = "flat",
        security_level: Union[str, SecurityLevel] = "none",
        distance_metric: Union[str, DistanceMetric] = "l2",
        use_simd: bool = True,
        use_gpu: bool = True,
        parallel_processing: bool = True,
        cache_size: str = "512MB",
        compression: bool = False,
        **kwargs
    ):
        """
        Initialize NusterDB with unified configuration.
        
        Args:
            mode: Storage mode ("memory", "persistent", "cache", "api")
            dimension: Vector dimension (required for new databases)
            path: Path for persistent storage
            url: Server URL for API mode
            algorithm: Indexing algorithm ("flat", "ivf", "pq", "lsh", "sq", "hnsw")
            security_level: Security level ("none", "basic", "enterprise", "government")  
            distance_metric: Distance metric ("l2", "cosine", "inner_product", "l1")
            use_simd: Enable SIMD optimizations
            use_gpu: Enable GPU acceleration
            parallel_processing: Enable parallel processing
            cache_size: Cache size (e.g., "1GB", "512MB")
            compression: Enable compression
            **kwargs: Additional configuration options
        """
        
        # Normalize inputs
        if isinstance(mode, str):
            mode = StorageMode(mode)
        if isinstance(algorithm, str):
            algorithm = Algorithm(algorithm)
        if isinstance(security_level, str):
            security_level = SecurityLevel(security_level)
        if isinstance(distance_metric, str):
            distance_metric = DistanceMetric(distance_metric)
        
        # Store configuration
        self.mode = mode
        self.dimension = dimension
        self.path = path
        self.url = url
        self.algorithm = algorithm
        self.security_level = security_level
        self.distance_metric = distance_metric
        
        # Create unified configuration
        self.config = NusterConfig(
            algorithm=algorithm,
            security_level=security_level,
            distance_metric=distance_metric,
            use_simd=use_simd,
            use_gpu=use_gpu,
            parallel_processing=parallel_processing,
            cache_size=cache_size,
            compression=compression,
            **kwargs
        )
        
        # State tracking
        self._vector_count = 0
        self._is_trained = False
        self._lock = threading.RLock()
        self._stats = {
            "queries": 0,
            "inserts": 0,
            "updates": 0,
            "deletes": 0,
            "build_time": 0.0,
            "total_query_time": 0.0,
        }
        
        # Initialize backend based on mode
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the appropriate backend based on mode."""
        try:
            if self.mode == StorageMode.API:
                if not self.url:
                    raise ConfigurationError("URL required for API mode")
                self._backend = NusterClient(self.url)
                
            elif self.mode == StorageMode.MEMORY:
                if not self.dimension:
                    raise ConfigurationError("Dimension required for memory mode")
                self._backend = MemoryBackend(self.config, self.dimension)
                
            elif self.mode == StorageMode.PERSISTENT:
                if not self.path or not self.dimension:
                    raise ConfigurationError("Path and dimension required for persistent mode")
                self._backend = PersistentBackend(self.config, self.path, self.dimension)
                
            elif self.mode == StorageMode.CACHE:
                if not self.dimension:
                    raise ConfigurationError("Dimension required for cache mode")
                self._backend = CacheBackend(self.config, self.dimension)
                
            else:
                raise ConfigurationError(f"Unsupported storage mode: {self.mode}")
                
        except Exception as e:
            raise NusterDBError(f"Failed to initialize {self.mode.value} backend: {e}")
    
    # Core Operations
    
    def add(
        self, 
        id: Union[int, str], 
        vector: Union[List[float], np.ndarray],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a single vector to the database.
        
        Args:
            id: Unique identifier
            vector: Vector data
            metadata: Optional metadata
            
        Returns:
            Success status
            
        Example:
            >>> db.add(1, [0.1, 0.2, 0.3], {"category": "document"})
        """
        with self._lock:
            try:
                # Validate vector
                vector = validate_vectors([vector], self.dimension)[0]
                
                # Add to backend
                success = self._backend.add(id, vector, metadata or {})
                
                if success:
                    self._vector_count += 1
                    self._stats["inserts"] += 1
                
                return success
                
            except Exception as e:
                raise NusterDBError(f"Failed to add vector {id}: {e}")
    
    def bulk_add(
        self,
        ids: List[Union[int, str]],
        vectors: Union[List[List[float]], np.ndarray],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        Add multiple vectors efficiently.
        
        Args:
            ids: List of unique identifiers
            vectors: List of vectors or numpy array
            metadata: Optional list of metadata dicts
            
        Returns:
            Number of vectors successfully added
            
        Example:
            >>> ids = [1, 2, 3]
            >>> vectors = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
            >>> db.bulk_add(ids, vectors)
        """
        with self._lock:
            try:
                # Validate inputs
                if len(ids) != len(vectors):
                    raise ValueError("IDs and vectors must have same length")
                
                vectors = validate_vectors(vectors, self.dimension)
                
                if metadata and len(metadata) != len(ids):
                    raise ValueError("Metadata must have same length as IDs")
                
                # Add to backend
                start_time = time.time()
                added_count = self._backend.bulk_add(ids, vectors, metadata or [])
                
                self._vector_count += added_count
                self._stats["inserts"] += added_count
                self._stats["build_time"] += time.time() - start_time
                
                return added_count
                
            except Exception as e:
                raise NusterDBError(f"Failed to bulk add vectors: {e}")
    
    def search(
        self,
        query: Union[List[float], np.ndarray],
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_distances: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query: Query vector
            k: Number of results to return
            filters: Optional metadata filters
            include_metadata: Include metadata in results
            include_distances: Include distances in results
            
        Returns:
            List of search results
            
        Example:
            >>> results = db.search([0.1, 0.2, 0.3], k=5)
            >>> for result in results:
            ...     print(f"ID: {result['id']}, Distance: {result['distance']}")
        """
        try:
            # Validate query
            query = validate_vectors([query], self.dimension)[0]
            
            # Search
            start_time = time.time()
            results = self._backend.search(
                query, k, filters, include_metadata, include_distances
            )
            
            self._stats["queries"] += 1
            self._stats["total_query_time"] += time.time() - start_time
            
            return results
            
        except Exception as e:
            raise NusterDBError(f"Search failed: {e}")
    
    def update(
        self,
        id: Union[int, str],
        vector: Optional[Union[List[float], np.ndarray]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing vector.
        
        Args:
            id: Vector ID to update
            vector: New vector data (optional)
            metadata: New metadata (optional)
            
        Returns:
            Success status
        """
        with self._lock:
            try:
                if vector is not None:
                    vector = validate_vectors([vector], self.dimension)[0]
                
                success = self._backend.update(id, vector, metadata)
                
                if success:
                    self._stats["updates"] += 1
                
                return success
                
            except Exception as e:
                raise NusterDBError(f"Failed to update vector {id}: {e}")
    
    def delete(self, id: Union[int, str]) -> bool:
        """
        Delete a vector by ID.
        
        Args:
            id: Vector ID to delete
            
        Returns:
            Success status
        """
        with self._lock:
            try:
                success = self._backend.delete(id)
                
                if success:
                    self._vector_count -= 1
                    self._stats["deletes"] += 1
                
                return success
                
            except Exception as e:
                raise NusterDBError(f"Failed to delete vector {id}: {e}")
    
    def get(
        self, 
        id: Union[int, str],
        include_metadata: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get a vector by ID.
        
        Args:
            id: Vector ID
            include_metadata: Include metadata in result
            
        Returns:
            Vector data or None if not found
        """
        try:
            return self._backend.get(id, include_metadata)
        except Exception as e:
            raise NusterDBError(f"Failed to get vector {id}: {e}")
    
    def batch_search(
        self,
        queries: Union[List[List[float]], np.ndarray],
        k: int = 10,
        filters: Optional[List[Dict[str, Any]]] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Search with multiple queries efficiently.
        
        Args:
            queries: List of query vectors
            k: Number of results per query
            filters: Optional filters per query
            
        Returns:
            List of result lists
        """
        try:
            queries = validate_vectors(queries, self.dimension)
            
            start_time = time.time()
            results = self._backend.batch_search(queries, k, filters)
            
            self._stats["queries"] += len(queries)
            self._stats["total_query_time"] += time.time() - start_time
            
            return results
            
        except Exception as e:
            raise NusterDBError(f"Batch search failed: {e}")
    
    # Management Operations
    
    def train(self, training_vectors: Optional[Union[List[List[float]], np.ndarray]] = None) -> bool:
        """
        Train the index (required for some algorithms).
        
        Args:
            training_vectors: Training data (optional, uses existing data if None)
            
        Returns:
            Success status
        """
        with self._lock:
            try:
                if hasattr(self._backend, 'train'):
                    success = self._backend.train(training_vectors)
                    self._is_trained = success
                    return success
                else:
                    self._is_trained = True
                    return True
                    
            except Exception as e:
                raise NusterDBError(f"Training failed: {e}")
    
    def optimize(self) -> bool:
        """
        Optimize the index for better performance.
        
        Returns:
            Success status
        """
        with self._lock:
            try:
                if hasattr(self._backend, 'optimize'):
                    return self._backend.optimize()
                return True
                
            except Exception as e:
                raise NusterDBError(f"Optimization failed: {e}")
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save the database to disk.
        
        Args:
            path: Save path (uses default if None)
            
        Returns:
            Success status
        """
        try:
            if hasattr(self._backend, 'save'):
                return self._backend.save(path)
            return True
            
        except Exception as e:
            raise NusterDBError(f"Save failed: {e}")
    
    def load(self, path: str) -> bool:
        """
        Load database from disk.
        
        Args:
            path: Load path
            
        Returns:
            Success status
        """
        with self._lock:
            try:
                if hasattr(self._backend, 'load'):
                    success = self._backend.load(path)
                    if success:
                        self._vector_count = self._backend.count()
                    return success
                return False
                
            except Exception as e:
                raise NusterDBError(f"Load failed: {e}")
    
    def clear(self) -> bool:
        """
        Clear all vectors from the database.
        
        Returns:
            Success status
        """
        with self._lock:
            try:
                success = self._backend.clear()
                if success:
                    self._vector_count = 0
                    self._is_trained = False
                return success
                
            except Exception as e:
                raise NusterDBError(f"Clear failed: {e}")
    
    # Information and Statistics
    
    def count(self) -> int:
        """Get total number of vectors."""
        return self._vector_count
    
    def size(self) -> int:
        """Alias for count()."""
        return self.count()
    
    def stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats.update({
            "vector_count": self._vector_count,
            "is_trained": self._is_trained,
            "mode": self.mode.value,
            "algorithm": self.algorithm.value,
            "dimension": self.dimension,
            "security_level": self.security_level.value,
            "avg_query_time": (
                self._stats["total_query_time"] / max(1, self._stats["queries"])
            ),
        })
        
        if hasattr(self._backend, 'stats'):
            stats.update(self._backend.stats())
            
        return stats
    
    def info(self) -> Dict[str, Any]:
        """
        Get database information.
        
        Returns:
            Information dictionary
        """
        return {
            "version": "2.1.1",
            "mode": self.mode.value,
            "algorithm": self.algorithm.value,
            "dimension": self.dimension,
            "vector_count": self._vector_count,
            "security_level": self.security_level.value,
            "distance_metric": self.distance_metric.value,
            "is_trained": self._is_trained,
            "config": self.config.to_dict(),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Health status
        """
        try:
            backend_healthy = True
            if hasattr(self._backend, 'health_check'):
                backend_status = self._backend.health_check()
                backend_healthy = backend_status.get('healthy', True)
            
            return {
                "healthy": backend_healthy,
                "mode": self.mode.value,
                "vector_count": self._vector_count,
                "is_trained": self._is_trained,
                "timestamp": time.time(),
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }
    
    # Context Manager Support
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the database and cleanup resources."""
        with self._lock:
            if hasattr(self._backend, 'close'):
                self._backend.close()
    
    # Iterator Support
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over all vectors."""
        if hasattr(self._backend, '__iter__'):
            return iter(self._backend)
        else:
            raise NotImplementedError(f"Iteration not supported for {self.mode.value} mode")
    
    def __len__(self) -> int:
        """Get number of vectors."""
        return self.count()
    
    def __contains__(self, id: Union[int, str]) -> bool:
        """Check if vector ID exists."""
        try:
            return self.get(id) is not None
        except:
            return False
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"NusterDB(mode={self.mode.value}, algorithm={self.algorithm.value}, "
            f"dimension={self.dimension}, vectors={self._vector_count})"
        )