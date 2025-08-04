"""
NusterDB Configuration Module
============================

Centralized configuration management for all NusterDB components.
"""

from enum import Enum
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import json

class Algorithm(Enum):
    """Supported indexing algorithms."""
    FLAT = "flat"              # Exact search (FAISS IndexFlat)
    IVF = "ivf"               # Inverted File Index (FAISS IndexIVFFlat)
    PQ = "pq"                 # Product Quantization (FAISS IndexPQ)
    LSH = "lsh"               # Locality Sensitive Hashing (FAISS IndexLSH)
    SQ = "sq"                 # Scalar Quantization (FAISS IndexSQ)
    HNSW = "hnsw"             # Hierarchical NSW (FAISS IndexHNSW)
    HYBRID = "hybrid"         # Multi-algorithm hybrid approach

class SecurityLevel(Enum):
    """Security compliance levels."""
    NONE = "none"                   # No special security
    BASIC = "basic"                 # Basic encryption
    ENTERPRISE = "enterprise"       # Enterprise-grade security
    GOVERNMENT = "government"       # Government-grade (FIPS 140-2, Common Criteria)

class StorageMode(Enum):
    """Storage backend modes."""
    MEMORY = "memory"               # In-memory only (fastest)
    PERSISTENT = "persistent"       # Disk-based storage (durable)
    CACHE = "cache"                # Memory + disk caching (balanced)
    API = "api"                    # Remote API connection (distributed)
    HYBRID = "hybrid"              # Mixed storage approach

class DistanceMetric(Enum):
    """Distance metrics for similarity calculation."""
    L2 = "l2"                      # Euclidean distance
    COSINE = "cosine"              # Cosine similarity
    INNER_PRODUCT = "inner_product" # Inner product
    L1 = "l1"                      # Manhattan distance
    HAMMING = "hamming"            # Hamming distance
    JACCARD = "jaccard"            # Jaccard similarity

@dataclass
class SecurityConfig:
    """Security-specific configuration."""
    level: SecurityLevel = SecurityLevel.NONE
    fips_mode: bool = False
    common_criteria: bool = False
    encryption_at_rest: bool = False
    encryption_key: Optional[str] = None
    audit_logging: bool = False
    access_control: bool = False
    quantum_resistant: bool = False

@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    use_simd: bool = True
    use_gpu: bool = True
    parallel_processing: bool = True
    num_threads: Optional[int] = None
    batch_size: int = 1000
    cache_size: str = "512MB"
    prefetch_size: int = 64
    memory_limit: Optional[str] = None

@dataclass
class AlgorithmConfig:
    """Algorithm-specific parameters."""
    # IVF parameters
    ivf_clusters: int = 256
    ivf_probe_lists: int = 32
    
    # PQ parameters
    pq_subvectors: int = 8
    pq_centroids: int = 256
    
    # LSH parameters
    lsh_hash_tables: int = 16
    lsh_hash_length: int = 64
    
    # SQ parameters
    sq_bits: int = 8
    
    # HNSW parameters
    hnsw_m: int = 16
    hnsw_ef_construction: int = 200
    hnsw_ef_search: int = 50
    
    # Hybrid parameters
    hybrid_primary: Optional[Algorithm] = None
    hybrid_secondary: Optional[Algorithm] = None

@dataclass
class NusterConfig:
    """
    Complete NusterDB configuration.
    
    This unified configuration handles all aspects of the database:
    - Algorithm selection and tuning
    - Security and compliance settings
    - Performance optimizations
    - Storage configurations
    """
    
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
    
    # Advanced configurations
    security: Optional[SecurityConfig] = None
    performance: Optional[PerformanceConfig] = None
    algorithms: Optional[AlgorithmConfig] = None
    
    # Custom settings
    custom: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize sub-configurations if not provided."""
        if self.security is None:
            self.security = SecurityConfig(level=self.security_level)
        
        if self.performance is None:
            self.performance = PerformanceConfig(
                use_simd=self.use_simd,
                use_gpu=self.use_gpu,
                parallel_processing=self.parallel_processing,
                cache_size=self.cache_size,
            )
        
        if self.algorithms is None:
            self.algorithms = AlgorithmConfig()
        
        if self.custom is None:
            self.custom = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = asdict(self)
        
        # Convert enums to values
        config_dict['algorithm'] = self.algorithm.value
        config_dict['security_level'] = self.security_level.value
        config_dict['distance_metric'] = self.distance_metric.value
        
        if self.algorithms and self.algorithms.hybrid_primary:
            config_dict['algorithms']['hybrid_primary'] = self.algorithms.hybrid_primary.value
        if self.algorithms and self.algorithms.hybrid_secondary:
            config_dict['algorithms']['hybrid_secondary'] = self.algorithms.hybrid_secondary.value
        
        return config_dict
    
    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'NusterConfig':
        """Create configuration from dictionary."""
        # Convert string values back to enums
        if 'algorithm' in config_dict:
            config_dict['algorithm'] = Algorithm(config_dict['algorithm'])
        if 'security_level' in config_dict:
            config_dict['security_level'] = SecurityLevel(config_dict['security_level'])
        if 'distance_metric' in config_dict:
            config_dict['distance_metric'] = DistanceMetric(config_dict['distance_metric'])
        
        return cls(**config_dict)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'NusterConfig':
        """Create configuration from JSON string."""
        config_dict = json.loads(json_str)
        return cls.from_dict(config_dict)
    
    def update(self, **kwargs) -> 'NusterConfig':
        """Create a new configuration with updated values."""
        config_dict = self.to_dict()
        config_dict.update(kwargs)
        return self.from_dict(config_dict)
    
    def optimize_for_speed(self) -> 'NusterConfig':
        """Get configuration optimized for maximum speed."""
        return self.update(
            algorithm=Algorithm.LSH,
            use_simd=True,
            use_gpu=True,
            parallel_processing=True,
            cache_size="1GB",
            compression=False,
        )
    
    def optimize_for_accuracy(self) -> 'NusterConfig':
        """Get configuration optimized for highest accuracy."""
        return self.update(
            algorithm=Algorithm.FLAT,
            use_simd=True,
            parallel_processing=True,
            cache_size="2GB",
        )
    
    def optimize_for_memory(self) -> 'NusterConfig':
        """Get configuration optimized for minimal memory usage."""
        return self.update(
            algorithm=Algorithm.PQ,
            compression=True,
            cache_size="256MB",
        )
    
    def enable_government_security(self) -> 'NusterConfig':
        """Enable government-grade security features."""
        security_config = SecurityConfig(
            level=SecurityLevel.GOVERNMENT,
            fips_mode=True,
            common_criteria=True,
            encryption_at_rest=True,
            audit_logging=True,
            access_control=True,
            quantum_resistant=True,
        )
        
        return self.update(
            security_level=SecurityLevel.GOVERNMENT,
            security=security_config,
        )

# Predefined configurations for common use cases
class PresetConfigs:
    """Predefined configurations for common use cases."""
    
    @staticmethod
    def development() -> NusterConfig:
        """Configuration for development and testing."""
        return NusterConfig(
            algorithm=Algorithm.FLAT,
            security_level=SecurityLevel.NONE,
            use_gpu=False,  # Don't require GPU for dev
            cache_size="256MB",
        )
    
    @staticmethod
    def production_speed() -> NusterConfig:
        """Configuration optimized for production speed."""
        return NusterConfig(
            algorithm=Algorithm.LSH,
            security_level=SecurityLevel.BASIC,
            use_simd=True,
            use_gpu=True,
            parallel_processing=True,
            cache_size="2GB",
        )
    
    @staticmethod
    def production_accuracy() -> NusterConfig:
        """Configuration optimized for production accuracy."""
        return NusterConfig(
            algorithm=Algorithm.IVF,
            security_level=SecurityLevel.ENTERPRISE,
            use_simd=True,
            use_gpu=True,
            parallel_processing=True,
            cache_size="4GB",
        )
    
    @staticmethod
    def government_secure() -> NusterConfig:
        """Configuration for government/defense applications."""
        return NusterConfig(
            algorithm=Algorithm.IVF,
            security_level=SecurityLevel.GOVERNMENT,
            use_simd=True,
            use_gpu=True,
            parallel_processing=True,
            cache_size="1GB",
        ).enable_government_security()
    
    @staticmethod
    def memory_constrained() -> NusterConfig:
        """Configuration for memory-constrained environments."""
        return NusterConfig(
            algorithm=Algorithm.PQ,
            security_level=SecurityLevel.BASIC,
            use_simd=True,
            use_gpu=False,
            parallel_processing=True,
            cache_size="128MB",
            compression=True,
        )
    
    @staticmethod
    def high_throughput() -> NusterConfig:
        """Configuration for high-throughput applications."""
        return NusterConfig(
            algorithm=Algorithm.HYBRID,
            security_level=SecurityLevel.ENTERPRISE,
            use_simd=True,
            use_gpu=True,
            parallel_processing=True,
            cache_size="8GB",
        )

def create_config(
    use_case: str = "development",
    **overrides
) -> NusterConfig:
    """
    Create a configuration for a specific use case.
    
    Args:
        use_case: Predefined use case ("development", "production_speed", etc.)
        **overrides: Configuration overrides
        
    Returns:
        Configured NusterConfig instance
    """
    preset_map = {
        "development": PresetConfigs.development,
        "dev": PresetConfigs.development,
        "production_speed": PresetConfigs.production_speed,
        "prod_speed": PresetConfigs.production_speed,
        "production_accuracy": PresetConfigs.production_accuracy,
        "prod_accuracy": PresetConfigs.production_accuracy,
        "government": PresetConfigs.government_secure,
        "secure": PresetConfigs.government_secure,
        "memory_constrained": PresetConfigs.memory_constrained,
        "low_memory": PresetConfigs.memory_constrained,
        "high_throughput": PresetConfigs.high_throughput,
        "throughput": PresetConfigs.high_throughput,
    }
    
    if use_case not in preset_map:
        raise ValueError(f"Unknown use case: {use_case}. Available: {list(preset_map.keys())}")
    
    config = preset_map[use_case]()
    
    if overrides:
        config = config.update(**overrides)
    
    return config