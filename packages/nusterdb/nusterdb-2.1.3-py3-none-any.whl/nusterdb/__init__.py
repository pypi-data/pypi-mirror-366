"""
NusterDB - High-Performance Government-Grade Vector Database
===========================================================

A complete vector database solution with advanced indexing algorithms,
government-grade security, and production-ready features.

Key Features:
- Advanced algorithms (IVF, PQ, LSH, SQ, Flat, HNSW)
- Government-grade security (FIPS 140-2, Common Criteria)
- Multiple storage modes (memory, persistent, cache)
- Production APIs and monitoring
- Cross-platform GPU acceleration

Example Usage:
    >>> import nusterdb
    >>> 
    >>> # Simple in-memory usage
    >>> db = nusterdb.NusterDB(mode="memory", dimension=128)
    >>> db.add([1, 2, 3], [0.1, 0.2, 0.3, ...])  # id, vector
    >>> results = db.search([0.1, 0.2, 0.3, ...], k=5)
    >>> 
    >>> # Persistent storage with advanced indexing
    >>> db = nusterdb.NusterDB(
    ...     mode="persistent", 
    ...     path="./my_vectors",
    ...     algorithm="ivf",
    ...     dimension=768,
    ...     security_level="government"
    ... )
    >>> db.bulk_add(ids, vectors, metadata)
    >>> results = db.search(query_vector, k=10, filters={"category": "documents"})
"""

# Version information
__version__ = "2.1.3"
__author__ = "NusterAI Team"
__email__ = "info@nusterai.com"

# Main imports
from .core import NusterDB
from .client import NusterClient
from .config import (
    Algorithm,
    SecurityLevel,
    StorageMode,
    DistanceMetric,
    NusterConfig,
)
from .exceptions import (
    NusterDBError,
    ConnectionError,
    SecurityError,
    IndexError,
    ConfigurationError,
)

# Utility imports
from .utils import (
    create_random_vectors,
    benchmark_performance,
    migrate_from_faiss,
    validate_vectors,
)

# Type hints
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np

# Public API
__all__ = [
    # Main classes
    "NusterDB",
    "NusterClient", 
    
    # Configuration
    "Algorithm",
    "SecurityLevel", 
    "StorageMode",
    "DistanceMetric",
    "NusterConfig",
    
    # Exceptions
    "NusterDBError",
    "ConnectionError",
    "SecurityError", 
    "IndexError",
    "ConfigurationError",
    
    # Utilities
    "create_random_vectors",
    "benchmark_performance",
    "migrate_from_faiss",
    "validate_vectors",
    
    # Version
    "__version__",
]

# Backward compatibility aliases
VectorDB = NusterDB  # Legacy name
Database = NusterDB  # Alternative name

def quick_start(dimension: int, mode: str = "memory") -> 'NusterDB':
    """
    Quick start helper for common use cases.
    
    Args:
        dimension: Vector dimension
        mode: Storage mode ("memory", "persistent", "cache")
        
    Returns:
        Configured NusterDB instance
        
    Example:
        >>> db = nusterdb.quick_start(128, "memory")
        >>> db.add(1, [0.1, 0.2, ...])
        >>> results = db.search([0.1, 0.2, ...])
    """
    return NusterDB(mode=mode, dimension=dimension)

# Module-level convenience functions
def connect(url: str = "http://localhost:7878", **kwargs) -> 'NusterClient':
    """
    Connect to a NusterDB server.
    
    Args:
        url: Server URL
        **kwargs: Additional connection parameters
        
    Returns:
        Connected client instance
    """
    return NusterClient(url=url, **kwargs)

def create_database(path: str, dimension: int, **kwargs) -> 'NusterDB':
    """
    Create a new persistent database.
    
    Args:
        path: Database path
        dimension: Vector dimension
        **kwargs: Additional configuration
        
    Returns:
        New database instance
    """
    return NusterDB(mode="persistent", path=path, dimension=dimension, **kwargs)

# Performance hints
def optimize_for_speed() -> Dict[str, Any]:
    """Get configuration optimized for maximum speed."""
    return {
        "algorithm": "lsh",
        "use_simd": True,
        "use_gpu": True,
        "parallel_processing": True,
        "cache_size": "1GB",
    }

def optimize_for_accuracy() -> Dict[str, Any]:
    """Get configuration optimized for highest accuracy."""
    return {
        "algorithm": "flat", 
        "use_simd": True,
        "precision": "high",
        "cache_size": "2GB",
    }

def optimize_for_memory() -> Dict[str, Any]:
    """Get configuration optimized for minimal memory usage."""
    return {
        "algorithm": "pq",
        "compression": True,
        "cache_size": "256MB",
        "use_mmap": True,
    }

# Package info
def info() -> Dict[str, Any]:
    """Get package information."""
    return {
        "version": __version__,
        "algorithms": ["flat", "ivf", "pq", "lsh", "sq", "hnsw", "hybrid"],
        "security_levels": ["none", "basic", "enterprise", "government"],
        "storage_modes": ["memory", "persistent", "cache", "hybrid"],
        "distance_metrics": ["l2", "cosine", "inner_product", "l1", "hamming"],
        "platforms": ["linux", "macos", "windows"],
        "gpu_support": ["metal", "cuda", "opencl", "wgpu"],
        "features": [
            "Advanced indexing algorithms",
            "Government-grade security", 
            "FIPS 140-2 compliance",
            "Real-time updates",
            "Production APIs",
            "Cross-platform GPU acceleration",
        ]
    }

# Initialization
try:
    # Try to import the compiled extension
    from . import _core
    _has_native_backend = True
except ImportError:
    _has_native_backend = False
    import warnings
    warnings.warn(
        "Native backend not available. Using Python fallback mode. "
        "Performance will be significantly reduced. "
        "Please reinstall with: pip install --no-cache-dir nusterdb",
        RuntimeWarning
    )

def _check_dependencies():
    """Check for optional dependencies and provide helpful messages."""
    try:
        import numpy
    except ImportError:
        raise ImportError(
            "NumPy is required but not installed. Install with: pip install numpy"
        )

# Initialize on import
_check_dependencies()