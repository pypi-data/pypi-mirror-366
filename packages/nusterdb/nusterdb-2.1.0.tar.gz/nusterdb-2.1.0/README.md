# NusterDB - High-Performance Vector Database with Enterprise Security

[![PyPI version](https://badge.fury.io/py/nusterdb.svg)](https://badge.fury.io/py/nusterdb)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## The Complete Vector Database Solution

NusterDB provides **complete FAISS algorithm compatibility** with enterprise-grade security, persistence, and production features that FAISS lacks. It's the only vector database combining competitive performance with comprehensive security compliance.

### All FAISS Algorithms + Enterprise Features

| Feature | NusterDB | FAISS | Other Vector DBs |
|---------|----------|-------|------------------|
| **FAISS Algorithms** | All (IVF, PQ, LSH, SQ, Flat, HNSW) | Yes | Limited |
| **Enterprise Security** | FIPS, Quantum-resistant | No | No |
| **Production APIs** | Complete REST + Python | Library only | Yes |
| **Persistence** | Built-in | Memory-only | Yes |
| **CRUD Operations** | Full database | Add/Search only | Yes |
| **Multiple Storage Modes** | Memory/Persistent/Cache | No | Limited |

## Quick Start

### Installation

```bash
pip install nusterdb
```

### Simple Usage

```python
import nusterdb

# Create database - choose your mode
db = nusterdb.NusterDB(mode="memory", dimension=128)

# Add vectors
db.add(1, [0.1, 0.2, 0.3, ...])  # Single vector
db.bulk_add([1,2,3], vectors, metadata)  # Multiple vectors

# Search
results = db.search([0.1, 0.2, 0.3, ...], k=5)
for result in results:
    print(f"ID: {result['id']}, Distance: {result['distance']}")
```

### Production Setup

```python
import nusterdb

# Production-ready configuration
db = nusterdb.NusterDB(
    mode="persistent",                    # Durable storage
    path="./secure_vectors",             # Storage location
    dimension=768,                       # Vector dimension
    algorithm="ivf",                     # FAISS IVF algorithm
    security_level="enterprise",         # Enhanced security
    use_simd=True,                      # Hardware acceleration
    parallel_processing=True            # Multi-threading
)

# Bulk operations with metadata
ids = [1, 2, 3, 4, 5]
vectors = [[0.1, 0.2, ...], [0.3, 0.4, ...], ...]
metadata = [{"category": "doc"}, {"category": "image"}, ...]

# Add vectors with metadata
db.bulk_add(ids, vectors, metadata)

# Advanced search with filters
results = db.search(
    query=[0.1, 0.2, 0.3, ...],
    k=10,
    filters={"category": "doc"},      # Metadata filtering
    include_metadata=True,
    include_distances=True
)

# Update and manage
db.update(1, new_vector, new_metadata)
db.delete(2)
print(f"Total vectors: {db.count()}")
```

## Storage Modes - Choose What Fits Your Needs

### Memory Mode (Fastest)
```python
# For temporary, high-speed operations
db = nusterdb.NusterDB(mode="memory", dimension=128)
# Best for: Testing, temporary data, maximum speed
```

### Persistent Mode (Production Ready)
```python
# For production with data persistence
db = nusterdb.NusterDB(
    mode="persistent", 
    path="./my_vectors",
    dimension=768
)
# Best for: Production data, long-term storage, reliability
```

### Cache Mode (Balanced Performance)
```python
# For large datasets with intelligent caching
db = nusterdb.NusterDB(
    mode="cache",
    cache_size="2GB",
    dimension=512
)
# Best for: Large datasets, memory optimization, balanced performance
```

### API Mode (Distributed)
```python
# Connect to NusterDB server
db = nusterdb.NusterDB(mode="api", url="http://localhost:7878")
# Best for: Microservices, distributed systems, scalability
```

## Enterprise Security Features

### Standard Security
```python
# Basic encryption and security
db = nusterdb.NusterDB(
    mode="persistent",
    path="./secure_vectors",
    security_level="basic",           # Standard security
    encryption_at_rest=True          # Data encryption
)
```

### Advanced Security (Enterprise)
```python
# Maximum security for sensitive data
db = nusterdb.NusterDB(
    mode="persistent",
    path="./classified_vectors",
    security_level="enterprise",      # Enhanced security
    encryption_at_rest=True,         # AES-256 encryption
    audit_logging=True,              # Security event tracking
    access_control=True,             # Role-based permissions
    quantum_resistant=True           # Future-proof encryption
)
```

### Security Features Available
- **FIPS 140-2 Ready** - Federal cryptographic standards compliance
- **AES-256 Encryption** - Industry-standard data protection
- **Quantum-Resistant** - Post-quantum cryptography algorithms
- **Audit Logging** - Comprehensive security event tracking
- **Access Control** - Multi-level security permissions
- **Key Management** - Secure key derivation and rotation

## All FAISS Algorithms Supported

```python
# Choose your algorithm based on needs
algorithms = {
    "accuracy": {"algorithm": "flat"},      # Exact search, highest accuracy
    "speed": {"algorithm": "lsh"},          # Fastest approximate search
    "balanced": {"algorithm": "ivf"},       # Good speed + accuracy balance
    "memory": {"algorithm": "pq"},          # Compressed storage
    "advanced": {"algorithm": "hnsw"},      # Graph-based search
    "hybrid": {"algorithm": "hybrid"}       # Multi-algorithm approach
}

db = nusterdb.NusterDB(dimension=768, **algorithms["balanced"])
```

## Performance Optimizations

### Speed-Optimized Setup
```python
# Maximum performance configuration
db = nusterdb.NusterDB(
    mode="memory",               # Fastest storage
    dimension=768,
    algorithm="lsh",            # Fast approximate search
    use_simd=True,              # CPU optimization
    parallel_processing=True,    # Multi-threading
    cache_size="4GB"            # Large cache
)
```

### Memory-Optimized Setup
```python
# Minimal memory usage
db = nusterdb.NusterDB(
    mode="cache",
    dimension=768,
    algorithm="pq",             # Compressed vectors
    compression=True,           # Additional compression
    cache_size="256MB"          # Small cache
)
```

## Realistic Performance Data

Based on **actual benchmarking** on Apple M2 Pro:

### NusterDB Performance
- **Memory Mode**: 15K-30K QPS (competitive with FAISS Flat)
- **Persistent Mode**: 8K-15K QPS (with durability)
- **Insertion Rate**: 10K+ vectors/sec with persistence
- **Memory Efficiency**: Zero-copy access, optimized storage

### vs FAISS (Library Only)
- **FAISS Flat L2**: 8K-68K QPS (memory-only, no persistence)
- **FAISS IVF**: 400-202K QPS (algorithm dependent)
- **FAISS LSH**: 139K-361K QPS (fastest, lower accuracy)

**Our Value**: Competitive performance **+ complete database features + enterprise security**

## Utilities and Migration

### FAISS Migration
```python
import nusterdb
import faiss

# Migrate from existing FAISS index
faiss_index = faiss.read_index("my_faiss.index")
db = nusterdb.NusterDB(mode="persistent", path="./migrated")

# One-line migration with progress tracking
stats = nusterdb.migrate_from_faiss(faiss_index, db)
print(f"Migrated {stats['migrated_vectors']} vectors in {stats['migration_time']:.2f}s")
```

### Performance Benchmarking
```python
# Benchmark your specific setup
metrics = nusterdb.benchmark_performance(
    db, 
    num_vectors=10000, 
    dimension=768,
    num_queries=1000
)
print(f"Search performance: {metrics['search_rate_qps']:.0f} QPS")
print(f"Insert performance: {metrics['insert_rate_per_sec']:.0f} vectors/sec")
```

### Vector Utilities
```python
# Create test data
vectors = nusterdb.create_random_vectors(1000, 768, seed=42)

# Validate vectors
validated = nusterdb.validate_vectors(vectors, expected_dimension=768)

# Load from files
ids, vectors, metadata = nusterdb.load_vectors_from_file("data.json")

# Save to files
nusterdb.save_vectors_to_file("backup.json", ids, vectors, metadata)
```

## Production Features

### Context Manager Support
```python
with nusterdb.NusterDB(mode="persistent", path="./vectors") as db:
    db.add(1, vector)
    results = db.search(query)
    # Automatically saved and closed
```

### Health Monitoring
```python
# System health checks
health = db.health_check()
print(f"Status: {'OK' if health['healthy'] else 'ERROR'}")
print(f"Vector count: {health.get('vector_count', 'Unknown')}")

# Detailed performance statistics
stats = db.stats()
print(f"Average query time: {stats['avg_query_time']:.3f}ms")
print(f"Memory usage: {stats.get('memory_usage_mb', 'N/A')} MB")
print(f"Cache hit rate: {stats.get('cache_hit_rate', 'N/A')}")
```

### Batch Operations
```python
# Efficient bulk processing
results = db.batch_search(
    queries=multiple_query_vectors,
    k=10
)

# Bulk updates with error handling
for id, new_vector in updates:
    try:
        db.update(id, new_vector)
    except nusterdb.NusterDBError as e:
        print(f"Update failed for {id}: {e}")
```

### Configuration Management
```python
from nusterdb import create_config

# Predefined configurations for common use cases
config = create_config("production_speed")     # Speed-optimized
config = create_config("production_accuracy")  # Accuracy-optimized  
config = create_config("memory_constrained")   # Memory-optimized
config = create_config("secure")              # Security-focused

db = nusterdb.NusterDB(config=config, dimension=768)
```

## Why Choose NusterDB?

### Complete FAISS Compatibility
- All FAISS algorithms (IVF, PQ, LSH, SQ, Flat, HNSW)
- All distance metrics (L2, Cosine, Inner Product, L1)
- Easy migration from existing FAISS indexes
- Performance competitive with FAISS Flat L2

### Unique Security Features
- **Only** vector database with enterprise-grade security
- FIPS 140-2 compliance ready
- Quantum-resistant cryptography
- Comprehensive audit logging and access control

### Production Ready
- Complete CRUD operations vs FAISS library-only
- Built-in persistence and durability
- Comprehensive APIs and monitoring
- Multiple storage modes for different use cases

### High Performance
- Competitive with FAISS (15K-30K QPS)
- Hardware acceleration (SIMD, multi-threading)
- Memory-efficient with zero-copy access
- Intelligent caching for large datasets

### Developer Friendly
- Single unified API for all storage modes
- Simple installation with pip
- Extensive documentation and examples
- Type hints and comprehensive error handling

## Performance Comparison

| Database | Search QPS | Features | Security | Use Case |
|----------|-----------|----------|----------|----------|
| **NusterDB** | **15K-30K** | Complete database | Enterprise-grade | **Production + Security** |
| FAISS | 8K-361K* | Library only | None | Research/Library |
| Pinecone | ~1K | Managed service | Standard | Managed cloud |
| Qdrant | 12K | Database | Basic | General purpose |

*FAISS performance varies widely by algorithm (8K Flat to 361K LSH)

## When to Choose NusterDB

### Choose NusterDB When:
- Need a **complete vector database** (not just a library)
- Require **enterprise security** and compliance
- Want **production APIs** and persistence out of the box
- Need **comprehensive monitoring** and operational tools
- Working with **sensitive or regulated data**
- Prefer **simple, unified Python interface**

### Consider FAISS When:
- Need **absolute maximum speed** (100K+ QPS) for research
- Building **custom systems** with library integration
- Have **memory-only** requirements with no persistence
- Working in **pure research/scientific** environments

## Links & Resources

- [Documentation](https://docs.nusterai.com/nusterdb)
- [Issues](https://github.com/NusterAI/nusterdb/issues)
- [Discussions](https://github.com/NusterAI/nusterdb/discussions)
- [Performance Benchmarks](https://github.com/NusterAI/nusterdb/blob/main/docs/PERFORMANCE_ANALYSIS.md)
- [Security Guide](https://github.com/NusterAI/nusterdb/blob/main/docs/SECURITY.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Ready to upgrade from FAISS or other vector databases?**

```bash
pip install nusterdb
```

Get all FAISS algorithms + enterprise security + production features in one simple package!