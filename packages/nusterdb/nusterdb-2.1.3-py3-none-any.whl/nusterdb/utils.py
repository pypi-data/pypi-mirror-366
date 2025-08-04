"""
NusterDB Utilities
=================

Utility functions for vector operations, validation, and migration.
"""

import numpy as np
import json
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path

from .exceptions import ValidationError, NusterDBError

def validate_vectors(
    vectors: Union[List[List[float]], np.ndarray], 
    expected_dimension: Optional[int] = None
) -> np.ndarray:
    """
    Validate and normalize vector data.
    
    Args:
        vectors: Input vectors
        expected_dimension: Expected vector dimension
        
    Returns:
        Validated numpy array
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Convert to numpy array
        if isinstance(vectors, list):
            vectors = np.array(vectors, dtype=np.float32)
        elif isinstance(vectors, np.ndarray):
            vectors = vectors.astype(np.float32)
        else:
            raise ValidationError(f"Unsupported vector type: {type(vectors)}")
        
        # Ensure 2D array
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        elif vectors.ndim != 2:
            raise ValidationError(f"Vectors must be 1D or 2D array, got {vectors.ndim}D")
        
        # Check dimension consistency
        if expected_dimension is not None:
            if vectors.shape[1] != expected_dimension:
                raise ValidationError(
                    f"Vector dimension mismatch: expected {expected_dimension}, got {vectors.shape[1]}"
                )
        
        # Check for invalid values
        if np.any(np.isnan(vectors)):
            raise ValidationError("Vectors contain NaN values")
        
        if np.any(np.isinf(vectors)):
            raise ValidationError("Vectors contain infinite values")
        
        return vectors
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Vector validation failed: {e}")

def normalize_vector(vector: np.ndarray, method: str = "l2") -> np.ndarray:
    """
    Normalize a vector using specified method.
    
    Args:
        vector: Input vector
        method: Normalization method ("l2", "l1", "max")
        
    Returns:
        Normalized vector
    """
    if method == "l2":
        norm = np.linalg.norm(vector, ord=2)
        return vector / (norm + 1e-8)  # Add small epsilon to avoid division by zero
    elif method == "l1":
        norm = np.linalg.norm(vector, ord=1)
        return vector / (norm + 1e-8)
    elif method == "max":
        max_val = np.max(np.abs(vector))
        return vector / (max_val + 1e-8)
    else:
        raise ValueError(f"Unsupported normalization method: {method}")

def create_random_vectors(
    count: int, 
    dimension: int, 
    distribution: str = "normal",
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Create random vectors for testing.
    
    Args:
        count: Number of vectors
        dimension: Vector dimension
        distribution: Distribution type ("normal", "uniform", "clustered")
        seed: Random seed for reproducibility
        
    Returns:
        Random vector array
    """
    if seed is not None:
        np.random.seed(seed)
    
    if distribution == "normal":
        vectors = np.random.normal(0, 1, (count, dimension)).astype(np.float32)
    elif distribution == "uniform":
        vectors = np.random.uniform(-1, 1, (count, dimension)).astype(np.float32)
    elif distribution == "clustered":
        # Create clustered data
        num_clusters = min(10, count // 10)
        cluster_centers = np.random.normal(0, 2, (num_clusters, dimension))
        
        vectors = []
        for i in range(count):
            cluster_id = i % num_clusters
            center = cluster_centers[cluster_id]
            noise = np.random.normal(0, 0.5, dimension)
            vector = center + noise
            vectors.append(vector)
        
        vectors = np.array(vectors, dtype=np.float32)
    else:
        raise ValueError(f"Unsupported distribution: {distribution}")
    
    return vectors

def benchmark_performance(
    db,
    num_vectors: int = 1000,
    dimension: int = 128,
    num_queries: int = 100,
    k: int = 10
) -> Dict[str, float]:
    """
    Benchmark database performance.
    
    Args:
        db: Database instance
        num_vectors: Number of vectors to insert
        dimension: Vector dimension
        num_queries: Number of search queries
        k: Number of results per query
        
    Returns:
        Performance metrics
    """
    print(f"🔬 Benchmarking performance with {num_vectors} vectors...")
    
    # Generate test data
    vectors = create_random_vectors(num_vectors, dimension, seed=42)
    queries = create_random_vectors(num_queries, dimension, seed=123)
    
    # Benchmark insertion
    print("  📝 Testing bulk insertion...")
    start_time = time.time()
    ids = list(range(num_vectors))
    db.bulk_add(ids, vectors)
    insert_time = time.time() - start_time
    
    # Benchmark search
    print("  🔍 Testing search performance...")
    start_time = time.time()
    for query in queries:
        results = db.search(query, k=k)
    search_time = time.time() - start_time
    
    # Calculate metrics
    insert_rate = num_vectors / insert_time
    search_rate = num_queries / search_time
    avg_search_time = search_time / num_queries * 1000  # milliseconds
    
    metrics = {
        "insert_rate_per_sec": insert_rate,
        "search_rate_qps": search_rate,
        "insert_time_total": insert_time,
        "search_time_total": search_time,
        "avg_search_time_ms": avg_search_time,
        "vectors_tested": num_vectors,
        "queries_tested": num_queries,
    }
    
    print(f"  ✅ Results: {insert_rate:.0f} inserts/sec, {search_rate:.0f} QPS")
    return metrics

def migrate_from_faiss(
    faiss_index,
    nusterdb_instance,
    batch_size: int = 1000,
    include_ids: bool = True
) -> Dict[str, Any]:
    """
    Migrate data from FAISS index to NusterDB.
    
    Args:
        faiss_index: FAISS index instance
        nusterdb_instance: NusterDB instance
        batch_size: Batch size for migration
        include_ids: Whether to preserve FAISS IDs
        
    Returns:
        Migration statistics
    """
    try:
        import faiss
    except ImportError:
        raise ImportError("FAISS not installed. Install with: pip install faiss-cpu")
    
    print(f"🔄 Migrating {faiss_index.ntotal} vectors from FAISS...")
    
    total_vectors = faiss_index.ntotal
    migrated_count = 0
    start_time = time.time()
    
    # Migrate in batches
    for start_idx in range(0, total_vectors, batch_size):
        end_idx = min(start_idx + batch_size, total_vectors)
        batch_size_actual = end_idx - start_idx
        
        # Extract vectors from FAISS
        vectors = faiss_index.reconstruct_batch(list(range(start_idx, end_idx)))
        
        # Generate IDs
        if include_ids:
            ids = list(range(start_idx, end_idx))
        else:
            ids = [f"faiss_{i}" for i in range(start_idx, end_idx)]
        
        # Add to NusterDB
        added = nusterdb_instance.bulk_add(ids, vectors)
        migrated_count += added
        
        print(f"  📦 Migrated batch {start_idx//batch_size + 1}: {added}/{batch_size_actual} vectors")
    
    migration_time = time.time() - start_time
    
    stats = {
        "total_vectors": total_vectors,
        "migrated_vectors": migrated_count,
        "migration_time": migration_time,
        "migration_rate": migrated_count / migration_time,
        "success_rate": migrated_count / total_vectors,
    }
    
    print(f"  ✅ Migration complete: {migrated_count}/{total_vectors} vectors in {migration_time:.2f}s")
    return stats

def load_vectors_from_file(
    file_path: Union[str, Path],
    format: str = "auto"
) -> Tuple[List, np.ndarray, Optional[List[Dict]]]:
    """
    Load vectors from various file formats.
    
    Args:
        file_path: Path to vector file
        format: File format ("auto", "npy", "json", "csv", "hdf5")
        
    Returns:
        Tuple of (ids, vectors, metadata)
    """
    file_path = Path(file_path)
    
    if format == "auto":
        format = file_path.suffix.lower().lstrip('.')
    
    if format == "npy":
        vectors = np.load(file_path)
        ids = list(range(len(vectors)))
        metadata = None
        
    elif format == "json":
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            ids = list(data.keys())
            vectors = np.array(list(data.values()), dtype=np.float32)
            metadata = None
        elif isinstance(data, list):
            ids = [item.get('id', i) for i, item in enumerate(data)]
            vectors = np.array([item['vector'] for item in data], dtype=np.float32)
            metadata = [item.get('metadata') for item in data]
        else:
            raise ValueError("Unsupported JSON format")
    
    elif format == "csv":
        import pandas as pd
        df = pd.read_csv(file_path)
        
        ids = df.iloc[:, 0].tolist()
        vectors = df.iloc[:, 1:].values.astype(np.float32)
        metadata = None
        
    elif format == "hdf5" or format == "h5":
        try:
            import h5py
        except ImportError:
            raise ImportError("h5py not installed. Install with: pip install h5py")
        
        with h5py.File(file_path, 'r') as f:
            vectors = f['vectors'][:]
            ids = f['ids'][:].tolist() if 'ids' in f else list(range(len(vectors)))
            metadata = None
    
    else:
        raise ValueError(f"Unsupported file format: {format}")
    
    return ids, vectors, metadata

def save_vectors_to_file(
    file_path: Union[str, Path],
    ids: List,
    vectors: np.ndarray,
    metadata: Optional[List[Dict]] = None,
    format: str = "auto"
):
    """
    Save vectors to various file formats.
    
    Args:
        file_path: Output file path  
        ids: Vector IDs
        vectors: Vector data
        metadata: Optional metadata
        format: File format ("auto", "npy", "json", "csv", "hdf5")
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == "auto":
        format = file_path.suffix.lower().lstrip('.')
    
    if format == "npy":
        np.save(file_path, vectors)
        
    elif format == "json":
        if metadata:
            data = [
                {"id": id_val, "vector": vector.tolist(), "metadata": meta}
                for id_val, vector, meta in zip(ids, vectors, metadata)
            ]
        else:
            data = [
                {"id": id_val, "vector": vector.tolist()}
                for id_val, vector in zip(ids, vectors)
            ]
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    elif format == "csv":
        import pandas as pd
        
        df_data = {"id": ids}
        for i in range(vectors.shape[1]):
            df_data[f"dim_{i}"] = vectors[:, i]
        
        df = pd.DataFrame(df_data)
        df.to_csv(file_path, index=False)
        
    elif format == "hdf5" or format == "h5":
        try:
            import h5py
        except ImportError:
            raise ImportError("h5py not installed. Install with: pip install h5py")
        
        with h5py.File(file_path, 'w') as f:
            f.create_dataset('vectors', data=vectors)
            f.create_dataset('ids', data=ids)
            if metadata:
                # Store metadata as JSON strings
                metadata_json = [json.dumps(meta) for meta in metadata]
                f.create_dataset('metadata', data=metadata_json)
    
    else:
        raise ValueError(f"Unsupported file format: {format}")

def calculate_recall(
    ground_truth: List[List[int]],
    search_results: List[List[Dict[str, Any]]],
    k: Optional[int] = None
) -> float:
    """
    Calculate recall@k for search results.
    
    Args:
        ground_truth: Ground truth nearest neighbors
        search_results: Search results from database
        k: Number of results to consider (default: all)
        
    Returns:
        Recall score
    """
    if len(ground_truth) != len(search_results):
        raise ValueError("Ground truth and results must have same length")
    
    total_recall = 0.0
    
    for gt, results in zip(ground_truth, search_results):
        if k is not None:
            gt = gt[:k]
            results = results[:k]
        
        # Extract IDs from results
        result_ids = [r.get('id') for r in results]
        
        # Calculate recall for this query
        correct = sum(1 for gt_id in gt if gt_id in result_ids)
        recall = correct / len(gt) if gt else 0.0
        total_recall += recall
    
    return total_recall / len(ground_truth)

def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging."""
    import platform
    import psutil
    
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2),
    }