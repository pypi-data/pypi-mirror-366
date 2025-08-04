# NusterDB - High-Performance Vector Database with Enterprise Security

[![PyPI version](https://badge.fury.io/py/nusterdb.svg)](https://badge.fury.io/py/nusterdb)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## The Complete Vector Database Solution

NusterDB is a high-performance vector database designed for production workloads with enterprise-grade security, persistence, and comprehensive features. Built for AI/ML applications requiring fast similarity search with reliability and security.

### Core Features

| Feature | Description |
|---------|-------------|
| **Advanced Algorithms** | Multiple search algorithms: IVF, PQ, LSH, SQ, Flat, HNSW |
| **Enterprise Security** | FIPS 140-2 compliance, quantum-resistant encryption |
| **Production APIs** | Complete REST APIs and Python SDK |
| **Data Persistence** | Built-in durable storage with transaction support |
| **Full CRUD Operations** | Complete database operations: Create, Read, Update, Delete |
| **Multiple Storage Modes** | Memory, Persistent, Cache, and API modes |

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

## Complete API Reference

### Core Classes

#### `NusterDB`

The main database class supporting all storage modes and algorithms.

```python
class NusterDB:
    """
    Unified NusterDB interface supporting all storage modes and algorithms.
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
```

**Parameters:**
- `mode`: Storage mode ("memory", "persistent", "cache", "api")
- `dimension`: Vector dimension (required for new databases)
- `path`: Path for persistent storage
- `url`: Server URL for API mode
- `algorithm`: Indexing algorithm ("flat", "ivf", "pq", "lsh", "sq", "hnsw")
- `security_level`: Security level ("none", "basic", "enterprise", "government")
- `distance_metric`: Distance metric ("l2", "cosine", "inner_product", "l1")
- `use_simd`: Enable SIMD optimizations
- `use_gpu`: Enable GPU acceleration
- `parallel_processing`: Enable parallel processing
- `cache_size`: Cache size (e.g., "1GB", "512MB")
- `compression`: Enable compression

#### Core Database Operations

##### `add(id, vector, metadata=None)`

Add a single vector to the database.

```python
def add(
    self, 
    id: Union[int, str], 
    vector: Union[List[float], np.ndarray],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
```

**Parameters:**
- `id`: Unique identifier
- `vector`: Vector data (list or numpy array)
- `metadata`: Optional metadata dictionary

**Returns:** `bool` - Success status

**Example:**
```python
# Add vector with metadata
success = db.add(1, [0.1, 0.2, 0.3], {"category": "document", "type": "text"})

# Add numpy vector
import numpy as np
vector = np.random.random(128)
db.add("doc_001", vector, {"source": "research_paper"})
```

##### `bulk_add(ids, vectors, metadata=None)`

Add multiple vectors efficiently.

```python
def bulk_add(
    self,
    ids: List[Union[int, str]],
    vectors: Union[List[List[float]], np.ndarray],
    metadata: Optional[List[Dict[str, Any]]] = None
) -> int:
```

**Parameters:**
- `ids`: List of unique identifiers
- `vectors`: List of vectors or 2D numpy array
- `metadata`: Optional list of metadata dictionaries

**Returns:** `int` - Number of vectors successfully added

**Example:**
```python
# Bulk add with metadata
ids = [1, 2, 3, 4, 5]
vectors = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8], [0.9, 1.0]]
metdata = [
    {"category": "A", "score": 0.95},
    {"category": "B", "score": 0.87},
    {"category": "A", "score": 0.92},
    {"category": "C", "score": 0.78},
    {"category": "B", "score": 0.89}
]
added_count = db.bulk_add(ids, vectors, metadata)
print(f"Added {added_count} vectors")

# Bulk add numpy arrays
import numpy as np
vectors = np.random.random((1000, 128))
ids = [f"vec_{i}" for i in range(1000)]
db.bulk_add(ids, vectors)
```

##### `search(query, k=10, filters=None, include_metadata=True, include_distances=True)`

Search for similar vectors.

```python
def search(
    self,
    query: Union[List[float], np.ndarray],
    k: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    include_metadata: bool = True,
    include_distances: bool = True
) -> List[Dict[str, Any]]:
```

**Parameters:**
- `query`: Query vector
- `k`: Number of results to return
- `filters`: Optional metadata filters
- `include_metadata`: Include metadata in results
- `include_distances`: Include distances in results

**Returns:** `List[Dict[str, Any]]` - List of search results

**Example:**
```python
# Basic search
results = db.search([0.1, 0.2, 0.3], k=5)
for result in results:
    print(f"ID: {result['id']}, Distance: {result['distance']}")

# Search with filters
results = db.search(
    query=[0.1, 0.2, 0.3],
    k=10,
    filters={"category": "document"},
    include_metadata=True,
    include_distances=True
)

# Process results
for result in results:
    print(f"ID: {result['id']}")
    print(f"Distance: {result['distance']:.4f}")
    print(f"Metadata: {result['metadata']}")
```

##### `update(id, vector=None, metadata=None)`

Update an existing vector.

```python
def update(
    self,
    id: Union[int, str],
    vector: Optional[Union[List[float], np.ndarray]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
```

**Parameters:**
- `id`: Vector ID to update
- `vector`: New vector data (optional)
- `metadata`: New metadata (optional)

**Returns:** `bool` - Success status

**Example:**
```python
# Update vector only
db.update(1, [0.2, 0.3, 0.4])

# Update metadata only
db.update(1, metadata={"category": "updated", "version": 2})

# Update both
db.update(1, [0.2, 0.3, 0.4], {"category": "updated", "version": 2})
```

##### `delete(id)`

Delete a vector by ID.

```python
def delete(self, id: Union[int, str]) -> bool:
```

**Parameters:**
- `id`: Vector ID to delete

**Returns:** `bool` - Success status

**Example:**
```python
# Delete by ID
success = db.delete(1)
if success:
    print("Vector deleted successfully")

# Delete multiple vectors
ids_to_delete = [1, 2, 3, 4, 5]
for vec_id in ids_to_delete:
    db.delete(vec_id)
```

##### `get(id, include_metadata=True)`

Get a vector by ID.

```python
def get(
    self, 
    id: Union[int, str],
    include_metadata: bool = True
) -> Optional[Dict[str, Any]]:
```

**Parameters:**
- `id`: Vector ID
- `include_metadata`: Include metadata in result

**Returns:** `Optional[Dict[str, Any]]` - Vector data or None if not found

**Example:**
```python
# Get vector with metadata
vector_data = db.get(1)
if vector_data:
    print(f"Vector: {vector_data['vector']}")
    print(f"Metadata: {vector_data['metadata']}")

# Get vector without metadata
vector_data = db.get(1, include_metadata=False)
```

##### `batch_search(queries, k=10, filters=None)`

Search with multiple queries efficiently.

```python
def batch_search(
    self,
    queries: Union[List[List[float]], np.ndarray],
    k: int = 10,
    filters: Optional[List[Dict[str, Any]]] = None
) -> List[List[Dict[str, Any]]]:
```

**Parameters:**
- `queries`: List of query vectors
- `k`: Number of results per query
- `filters`: Optional filters per query

**Returns:** `List[List[Dict[str, Any]]]` - List of result lists

**Example:**
```python
# Batch search multiple queries
queries = [
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6],
    [0.7, 0.8, 0.9]
]
all_results = db.batch_search(queries, k=5)

for i, results in enumerate(all_results):
    print(f"Query {i} results:")
    for result in results:
        print(f"  ID: {result['id']}, Distance: {result['distance']}")
```

#### Management Operations

##### `train(training_vectors=None)`

Train the index (required for some algorithms).

```python
def train(self, training_vectors: Optional[Union[List[List[float]], np.ndarray]] = None) -> bool:
```

**Parameters:**
- `training_vectors`: Training data (optional, uses existing data if None)

**Returns:** `bool` - Success status

**Example:**
```python
# Train with existing data
db.train()

# Train with specific training data
training_data = np.random.random((10000, 128))
db.train(training_data)
```

##### `optimize()`

Optimize the index for better performance.

```python
def optimize(self) -> bool:
```

**Returns:** `bool` - Success status

**Example:**
```python
# Optimize after bulk inserts
db.bulk_add(ids, vectors)
db.optimize()  # Rebuild index for better performance
```

##### `save(path=None)`

Save the database to disk.

```python
def save(self, path: Optional[str] = None) -> bool:
```

**Parameters:**
- `path`: Save path (uses default if None)

**Returns:** `bool` - Success status

##### `load(path)`

Load database from disk.

```python
def load(self, path: str) -> bool:
```

**Parameters:**
- `path`: Load path

**Returns:** `bool` - Success status

##### `clear()`

Clear all vectors from the database.

```python
def clear(self) -> bool:
```

**Returns:** `bool` - Success status

#### Information and Statistics

##### `count()` / `size()`

Get total number of vectors.

```python
def count(self) -> int:
def size(self) -> int:  # Alias for count()
```

**Returns:** `int` - Number of vectors

**Example:**
```python
total_vectors = db.count()
print(f"Database contains {total_vectors} vectors")
```

##### `stats()`

Get database statistics.

```python
def stats(self) -> Dict[str, Any]:
```

**Returns:** `Dict[str, Any]` - Statistics dictionary

**Example:**
```python
stats = db.stats()
print(f"Vector count: {stats['vector_count']}")
print(f"Average query time: {stats['avg_query_time']:.3f}ms")
print(f"Algorithm: {stats['algorithm']}")
print(f"Security level: {stats['security_level']}")
```

##### `info()`

Get database information.

```python
def info(self) -> Dict[str, Any]:
```

**Returns:** `Dict[str, Any]` - Information dictionary

##### `health_check()`

Perform health check.

```python
def health_check(self) -> Dict[str, Any]:
```

**Returns:** `Dict[str, Any]` - Health status

**Example:**
```python
health = db.health_check()
if health['healthy']:
    print("Database is healthy")
    print(f"Vector count: {health['vector_count']}")
else:
    print(f"Database issue: {health.get('error')}")
```

#### Context Manager Support

```python
# Automatic resource management
with nusterdb.NusterDB(mode="persistent", path="./vectors") as db:
    db.add(1, [0.1, 0.2, 0.3])
    results = db.search([0.1, 0.2, 0.3])
    # Database automatically saved and closed
```

#### Iterator Support

```python
# Iterate over all vectors (if supported by backend)
for vector_data in db:
    print(f"ID: {vector_data['id']}")
    print(f"Vector: {vector_data['vector']}")

# Check if ID exists
if 1 in db:
    print("Vector with ID 1 exists")

# Get length
print(f"Database has {len(db)} vectors")
```

### Configuration Classes

#### `NusterConfig`

Complete configuration for all NusterDB aspects.

```python
@dataclass
class NusterConfig:
    # Core settings
    algorithm: Algorithm = Algorithm.FLAT
    security_level: SecurityLevel = SecurityLevel.NONE
    distance_metric: DistanceMetric = DistanceMetric.L2
    
    # Performance settings
    use_simd: bool = True
    use_gpu: bool = True
    parallel_processing: bool = True
    cache_size: str = "512MB"
    compression: bool = False
```

**Methods:**
- `to_dict()` - Convert to dictionary
- `to_json()` - Convert to JSON string
- `from_dict(config_dict)` - Create from dictionary
- `from_json(json_str)` - Create from JSON
- `update(**kwargs)` - Create updated configuration
- `optimize_for_speed()` - Speed-optimized configuration
- `optimize_for_accuracy()` - Accuracy-optimized configuration
- `optimize_for_memory()` - Memory-optimized configuration

#### Configuration Enums

```python
class Algorithm(Enum):
    FLAT = "flat"              # Exact search
    IVF = "ivf"               # Inverted File Index
    PQ = "pq"                 # Product Quantization
    LSH = "lsh"               # Locality Sensitive Hashing
    SQ = "sq"                 # Scalar Quantization
    HNSW = "hnsw"             # Hierarchical NSW
    HYBRID = "hybrid"         # Multi-algorithm approach

class SecurityLevel(Enum):
    NONE = "none"                   # No special security
    BASIC = "basic"                 # Basic encryption
    ENTERPRISE = "enterprise"       # Enterprise-grade security
    GOVERNMENT = "government"       # Government-grade (FIPS 140-2)

class StorageMode(Enum):
    MEMORY = "memory"               # In-memory only (fastest)
    PERSISTENT = "persistent"       # Disk-based storage (durable)
    CACHE = "cache"                # Memory + disk caching
    API = "api"                    # Remote API connection

class DistanceMetric(Enum):
    L2 = "l2"                      # Euclidean distance
    COSINE = "cosine"              # Cosine similarity
    INNER_PRODUCT = "inner_product" # Inner product
    L1 = "l1"                      # Manhattan distance
    HAMMING = "hamming"            # Hamming distance
```

### Client Class

#### `NusterClient`

Client for connecting to NusterDB server instances.

```python
class NusterClient:
    def __init__(
        self,
        url: str = "http://localhost:7878",
        timeout: int = 30,
        retry_attempts: int = 3,
        api_key: Optional[str] = None,
        verify_ssl: bool = True
    ):
```

**Parameters:**
- `url`: Server URL
- `timeout`: Request timeout in seconds
- `retry_attempts`: Number of retry attempts
- `api_key`: Optional API key for authentication
- `verify_ssl`: Verify SSL certificates

**Methods:** Same interface as `NusterDB` but operates over HTTP/REST API.

**Example:**
```python
# Connect to server
client = nusterdb.NusterClient("http://localhost:7878", api_key="your-key")

# Use same interface as local database
client.add(1, [0.1, 0.2, 0.3])
results = client.search([0.1, 0.2, 0.3], k=5)
```

### Utility Functions

#### `create_random_vectors(count, dimension, distribution="normal", seed=None)`

Create random vectors for testing.

```python
def create_random_vectors(
    count: int, 
    dimension: int, 
    distribution: str = "normal",
    seed: Optional[int] = None
) -> np.ndarray:
```

**Parameters:**
- `count`: Number of vectors
- `dimension`: Vector dimension
- `distribution`: Distribution type ("normal", "uniform", "clustered")
- `seed`: Random seed for reproducibility

**Example:**
```python
# Create test vectors
vectors = nusterdb.create_random_vectors(1000, 128, distribution="normal", seed=42)

# Create clustered data
clustered = nusterdb.create_random_vectors(500, 64, distribution="clustered")
```

#### `benchmark_performance(db, num_vectors=1000, dimension=128, num_queries=100, k=10)`

Benchmark database performance.

```python
def benchmark_performance(
    db,
    num_vectors: int = 1000,
    dimension: int = 128,
    num_queries: int = 100,
    k: int = 10
) -> Dict[str, float]:
```

**Returns:** Performance metrics dictionary

**Example:**
```python
# Benchmark your database
metrics = nusterdb.benchmark_performance(db, num_vectors=5000, dimension=768)
print(f"Insert rate: {metrics['insert_rate_per_sec']:.0f} vectors/sec")
print(f"Search rate: {metrics['search_rate_qps']:.0f} QPS")
print(f"Average search time: {metrics['avg_search_time_ms']:.2f} ms")
```

#### `validate_vectors(vectors, expected_dimension=None)`

Validate and normalize vector data.

```python
def validate_vectors(
    vectors: Union[List[List[float]], np.ndarray], 
    expected_dimension: Optional[int] = None
) -> np.ndarray:
```

**Example:**
```python
# Validate vectors before adding
vectors = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
validated = nusterdb.validate_vectors(vectors, expected_dimension=2)
```

#### `load_vectors_from_file(file_path, format="auto")` / `save_vectors_to_file(...)`

Load and save vectors from various file formats.

```python
# Load from file
ids, vectors, metadata = nusterdb.load_vectors_from_file("data.json")
db.bulk_add(ids, vectors, metadata)

# Save to file
ids = list(range(100))
vectors = nusterdb.create_random_vectors(100, 128)
nusterdb.save_vectors_to_file("backup.json", ids, vectors)
```

**Supported formats:** JSON, NumPy (.npy), CSV, HDF5 (.h5)

### Exception Classes

```python
class NusterDBError(Exception):
    """Base exception for all NusterDB errors."""
    
class ConnectionError(NusterDBError):
    """Connection to server failed."""
    
class SecurityError(NusterDBError):
    """Security validation failed."""
    
class IndexError(NusterDBError):
    """Index operations failed."""
    
class ConfigurationError(NusterDBError):
    """Configuration is invalid."""
    
class ValidationError(NusterDBError):
    """Input validation failed."""
```

### Module-Level Convenience Functions

#### `quick_start(dimension, mode="memory")`

Quick start helper for common use cases.

```python
# Quick setup
db = nusterdb.quick_start(128, "memory")
db.add(1, [0.1, 0.2, ...])
```

#### `connect(url="http://localhost:7878", **kwargs)`

Connect to NusterDB server.

```python
# Connect to server
client = nusterdb.connect("http://localhost:7878", api_key="key")
```

#### `create_database(path, dimension, **kwargs)`

Create a new persistent database.

```python
# Create persistent database
db = nusterdb.create_database("./vectors", 128, algorithm="ivf")
```

#### Configuration Helpers

```python
# Get optimized configurations
speed_config = nusterdb.optimize_for_speed()
accuracy_config = nusterdb.optimize_for_accuracy()
memory_config = nusterdb.optimize_for_memory()

# Use with database
db = nusterdb.NusterDB(dimension=128, **speed_config)
```

#### `info()`

Get package information.

```python
package_info = nusterdb.info()
print(f"Version: {package_info['version']}")
print(f"Algorithms: {package_info['algorithms']}")
print(f"Features: {package_info['features']}")
```

## Storage Modes

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

## Vector Search Algorithms

### Algorithm Details

- **Flat**: Exact brute-force search for highest accuracy
- **IVF**: Inverted file structure for balanced performance
- **LSH**: Locality-sensitive hashing for speed
- **PQ**: Product quantization for memory efficiency
- **HNSW**: Hierarchical navigable small world graphs
- **SQ**: Scalar quantization for reduced memory usage

```python
# Algorithm-specific configuration
db = nusterdb.NusterDB(
    dimension=768,
    algorithm="ivf",
    # IVF-specific parameters
    ivf_clusters=256,
    ivf_probe_lists=32
)

# PQ configuration
db = nusterdb.NusterDB(
    dimension=768,
    algorithm="pq",
    pq_subvectors=8,
    pq_centroids=256
)
```

## Performance Benchmarks

Based on internal benchmarking on enterprise hardware:

### NusterDB Performance
- **Memory Mode**: 15K-30K queries per second
- **Persistent Mode**: 8K-15K QPS with full durability
- **Insertion Rate**: 10K+ vectors/sec with persistence
- **Memory Efficiency**: Zero-copy access, optimized storage
- **Latency**: Sub-millisecond response times for most queries

### Distance Metrics Supported
- **L2 (Euclidean)**: Standard Euclidean distance
- **Cosine**: Cosine similarity for normalized vectors
- **Inner Product**: Dot product similarity
- **L1 (Manhattan)**: Manhattan distance

## Configuration Management

### Predefined Configurations

```python
from nusterdb import create_config

# Predefined configurations for common use cases
config = create_config("production_speed")     # Speed-optimized
config = create_config("production_accuracy")  # Accuracy-optimized  
config = create_config("memory_constrained")   # Memory-optimized
config = create_config("secure")              # Security-focused

db = nusterdb.NusterDB(config=config, dimension=768)
```

### Available Presets
- `"development"` / `"dev"` - Development and testing
- `"production_speed"` / `"prod_speed"` - Speed-optimized production
- `"production_accuracy"` / `"prod_accuracy"` - Accuracy-optimized production
- `"government"` / `"secure"` - Government-grade security
- `"memory_constrained"` / `"low_memory"` - Memory-optimized
- `"high_throughput"` / `"throughput"` - High-throughput applications

### Custom Configurations

```python
# Create custom configuration
config = nusterdb.NusterConfig(
    algorithm=nusterdb.Algorithm.IVF,
    security_level=nusterdb.SecurityLevel.ENTERPRISE,
    distance_metric=nusterdb.DistanceMetric.COSINE,
    use_gpu=True,
    cache_size="4GB"
)

# Use configuration
db = nusterdb.NusterDB(config=config, dimension=768)

# Update configuration
updated_config = config.update(use_simd=False, parallel_processing=False)
```

## Advanced Examples

### Large-Scale Production Setup

```python
import nusterdb
import numpy as np

# Production configuration with security
db = nusterdb.NusterDB(
    mode="persistent",
    path="/secure/vectors",
    dimension=1536,                    # OpenAI embeddings
    algorithm="ivf",
    security_level="enterprise",
    distance_metric="cosine",
    use_gpu=True,
    parallel_processing=True,
    cache_size="8GB",
    
    # IVF-specific tuning
    ivf_clusters=1024,
    ivf_probe_lists=64,
    
    # Security settings
    encryption_at_rest=True,
    audit_logging=True,
    access_control=True
)

# Bulk data loading with progress tracking
def load_embeddings(file_path, batch_size=1000):
    ids, vectors, metadata = nusterdb.load_vectors_from_file(file_path)
    
    total_batches = len(ids) // batch_size + 1
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_vectors = vectors[i:i+batch_size]
        batch_metadata = metadata[i:i+batch_size] if metadata else None
        
        added = db.bulk_add(batch_ids, batch_vectors, batch_metadata)
        print(f"Batch {i//batch_size + 1}/{total_batches}: Added {added} vectors")
    
    # Optimize after bulk loading
    print("Optimizing index...")
    db.optimize()

# Advanced search with multiple filters
def semantic_search(query_text, filters=None, k=10):
    # Convert text to embedding (pseudo-code)
    query_embedding = get_text_embedding(query_text)
    
    results = db.search(
        query=query_embedding,
        k=k,
        filters=filters or {},
        include_metadata=True,
        include_distances=True
    )
    
    # Post-process results
    processed_results = []
    for result in results:
        processed_results.append({
            'id': result['id'],
            'similarity': 1 - result['distance'],  # Convert distance to similarity
            'metadata': result['metadata'],
            'confidence': result['distance'] < 0.5  # Confidence threshold
        })
    
    return processed_results

# Usage
results = semantic_search(
    "machine learning algorithms",
    filters={"category": "research", "year": 2023},
    k=20
)
```

### Multi-Modal Search System

```python
import nusterdb

class MultiModalSearchSystem:
    def __init__(self, base_path: str):
        # Separate databases for different modalities
        self.text_db = nusterdb.NusterDB(
            mode="persistent",
            path=f"{base_path}/text",
            dimension=768,
            algorithm="hnsw",
            distance_metric="cosine"
        )
        
        self.image_db = nusterdb.NusterDB(
            mode="persistent", 
            path=f"{base_path}/images",
            dimension=2048,
            algorithm="ivf",
            distance_metric="l2"
        )
        
        self.audio_db = nusterdb.NusterDB(
            mode="persistent",
            path=f"{base_path}/audio", 
            dimension=512,
            algorithm="lsh",
            distance_metric="cosine"
        )
    
    def add_content(self, content_id: str, embeddings: dict, metadata: dict):
        """Add multi-modal content."""
        if 'text' in embeddings:
            self.text_db.add(content_id, embeddings['text'], metadata)
        
        if 'image' in embeddings:
            self.image_db.add(content_id, embeddings['image'], metadata)
            
        if 'audio' in embeddings:
            self.audio_db.add(content_id, embeddings['audio'], metadata)
    
    def search_all_modalities(self, query_embeddings: dict, k: int = 10):
        """Search across all modalities and combine results."""
        all_results = {}
        
        if 'text' in query_embeddings:
            text_results = self.text_db.search(query_embeddings['text'], k=k)
            all_results['text'] = text_results
            
        if 'image' in query_embeddings:
            image_results = self.image_db.search(query_embeddings['image'], k=k)
            all_results['image'] = image_results
            
        if 'audio' in query_embeddings:
            audio_results = self.audio_db.search(query_embeddings['audio'], k=k)
            all_results['audio'] = audio_results
        
        return self._combine_results(all_results)
    
    def _combine_results(self, results_by_modality):
        """Combine and rank results from multiple modalities."""
        # Implementation depends on your fusion strategy
        combined = {}
        for modality, results in results_by_modality.items():
            for result in results:
                content_id = result['id']
                if content_id not in combined:
                    combined[content_id] = {
                        'id': content_id,
                        'metadata': result['metadata'],
                        'scores': {}
                    }
                combined[content_id]['scores'][modality] = 1 - result['distance']
        
        # Sort by combined score
        for item in combined.values():
            item['combined_score'] = sum(item['scores'].values()) / len(item['scores'])
        
        return sorted(combined.values(), key=lambda x: x['combined_score'], reverse=True)

# Usage
search_system = MultiModalSearchSystem("/data/multimodal")

# Add content
search_system.add_content(
    "doc_001",
    embeddings={
        'text': text_embedding,
        'image': image_embedding
    },
    metadata={'title': 'Research Paper', 'type': 'academic'}
)

# Search
results = search_system.search_all_modalities({
    'text': query_text_embedding,
    'image': query_image_embedding
})
```

### Real-Time Recommendation System

```python
import nusterdb
from collections import defaultdict
import time

class RecommendationSystem:
    def __init__(self):
        self.user_db = nusterdb.NusterDB(
            mode="cache",
            dimension=256,
            algorithm="lsh",
            cache_size="1GB"
        )
        
        self.item_db = nusterdb.NusterDB(
            mode="persistent",
            path="./items",
            dimension=256,
            algorithm="ivf"
        )
        
        # Track user interactions
        self.user_interactions = defaultdict(list)
    
    def add_user_profile(self, user_id: str, profile_vector: list, metadata: dict):
        """Add or update user profile."""
        self.user_db.add(user_id, profile_vector, metadata)
    
    def add_item(self, item_id: str, feature_vector: list, metadata: dict):
        """Add item to catalog."""
        self.item_db.add(item_id, feature_vector, metadata)
    
    def record_interaction(self, user_id: str, item_id: str, interaction_type: str, rating: float = None):
        """Record user-item interaction."""
        interaction = {
            'item_id': item_id,
            'type': interaction_type,
            'rating': rating,
            'timestamp': time.time()
        }
        self.user_interactions[user_id].append(interaction)
        
        # Update user profile based on interaction
        self._update_user_profile(user_id, item_id, interaction_type, rating)
    
    def get_recommendations(self, user_id: str, k: int = 10, exclude_seen: bool = True):
        """Get personalized recommendations."""
        # Get user profile
        user_profile = self.user_db.get(user_id)
        if not user_profile:
            return self._get_popular_items(k)
        
        # Find similar items
        recommendations = self.item_db.search(
            user_profile['vector'],
            k=k * 2,  # Get more to account for filtering
            include_metadata=True
        )
        
        # Filter out already seen items
        if exclude_seen:
            seen_items = {interaction['item_id'] for interaction in self.user_interactions[user_id]}
            recommendations = [r for r in recommendations if r['id'] not in seen_items]
        
        return recommendations[:k]
    
    def get_similar_users(self, user_id: str, k: int = 5):
        """Find similar users for collaborative filtering."""
        user_profile = self.user_db.get(user_id)
        if not user_profile:
            return []
        
        similar_users = self.user_db.search(
            user_profile['vector'],
            k=k + 1,  # +1 to exclude self
            include_metadata=True
        )
        
        # Remove self from results
        return [u for u in similar_users if u['id'] != user_id]
    
    def _update_user_profile(self, user_id: str, item_id: str, interaction_type: str, rating: float):
        """Update user profile based on interaction."""
        # Get current profile and item features
        user_profile = self.user_db.get(user_id)
        item_data = self.item_db.get(item_id)
        
        if not user_profile or not item_data:
            return
        
        # Simple profile update (weighted average)
        weight = self._get_interaction_weight(interaction_type, rating)
        current_vector = np.array(user_profile['vector'])
        item_vector = np.array(item_data['vector'])
        
        # Update with exponential moving average
        alpha = 0.1  # Learning rate
        updated_vector = (1 - alpha) * current_vector + alpha * weight * item_vector
        
        # Update user profile
        self.user_db.update(user_id, updated_vector.tolist())
    
    def _get_interaction_weight(self, interaction_type: str, rating: float = None) -> float:
        """Convert interaction type to weight."""
        weights = {
            'view': 0.1,
            'click': 0.3,
            'like': 0.7,
            'purchase': 1.0,
            'rating': rating or 0.5
        }
        return weights.get(interaction_type, 0.1)
    
    def _get_popular_items(self, k: int):
        """Fallback for new users - return popular items."""
        # Simple implementation - could be enhanced with actual popularity metrics
        all_items = list(self.item_db)[:k]
        return all_items

# Usage
rec_system = RecommendationSystem()

# Add items
rec_system.add_item("item_1", feature_vector, {"category": "electronics", "price": 299.99})

# Add users
rec_system.add_user_profile("user_1", profile_vector, {"age": 25, "location": "NY"})

# Record interactions
rec_system.record_interaction("user_1", "item_1", "purchase", rating=4.5)

# Get recommendations
recommendations = rec_system.get_recommendations("user_1", k=10)
for rec in recommendations:
    print(f"Recommended: {rec['id']} (similarity: {1-rec['distance']:.3f})")
```

## Why Choose NusterDB?

### Complete Database Solution
- Full CRUD operations with transaction support
- Built-in persistence and data durability
- Comprehensive APIs for production use
- Multiple storage modes for different use cases

### Enterprise Security
- Industry-leading security features
- FIPS 140-2 compliance ready
- Quantum-resistant cryptography
- Comprehensive audit logging and access control

### High Performance
- Advanced algorithms optimized for different workloads
- Hardware acceleration (SIMD, multi-threading)
- Memory-efficient with zero-copy access
- Intelligent caching for large datasets

### Developer Friendly
- Single unified API for all storage modes
- Simple installation with pip
- Extensive documentation and examples
- Type hints and comprehensive error handling

## Use Cases

### Recommended For:
- **AI/ML Applications** requiring fast similarity search
- **Production Systems** needing reliability and persistence  
- **Enterprise Environments** with security requirements
- **Large-Scale Deployments** requiring monitoring and ops tools
- **Sensitive Data** needing encryption and compliance
- **Microservices** architecture with API-first design

### Common Applications:
- Semantic search and document retrieval
- Image and video similarity search
- Recommendation systems
- Anomaly detection
- Content-based filtering
- Knowledge base search

## Links & Resources

- [Documentation](https://docs.nusterai.com/nusterdb)
- [Issues](https://github.com/NusterAI/nusterdb/issues)
- [Discussions](https://github.com/NusterAI/nusterdb/discussions)
- [Performance Benchmarks](https://github.com/NusterAI/nusterdb/blob/main/docs/PERFORMANCE_ANALYSIS.md)
- [Security Guide](https://github.com/NusterAI/nusterdb/blob/main/docs/SECURITY.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Ready to build with high-performance vector search?**

```bash
pip install nusterdb
```

Get enterprise-grade vector database with security, persistence, and production features!