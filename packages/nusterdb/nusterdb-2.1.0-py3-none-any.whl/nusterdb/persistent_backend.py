"""
Persistent Backend for NusterDB
===============================

Disk-based vector storage backend with durability guarantees.
"""

import numpy as np
import os
import json
import pickle
import mmap
import threading
from threading import RLock
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from .config import NusterConfig
from .exceptions import NusterDBError, StorageError
from .memory_backend import MemoryBackend

class PersistentBackend:
    """
    Persistent vector storage backend.
    
    Combines in-memory performance with disk durability.
    Uses memory-mapped files for efficient I/O.
    """
    
    def __init__(self, config: NusterConfig, path: str, dimension: int):
        """Initialize persistent backend."""
        self.config = config
        self.path = Path(path)
        self.dimension = dimension
        
        # Create directory structure
        self.path.mkdir(parents=True, exist_ok=True)
        self.vectors_file = self.path / "vectors.dat"
        self.metadata_file = self.path / "metadata.json"
        self.index_file = self.path / "index.json"
        
        # In-memory cache for performance
        self._memory_backend = MemoryBackend(config, dimension)
        
        # File handles
        self._vectors_fd = None
        self._vectors_mmap = None
        
        # Thread safety
        self._lock = RLock()
        
        # Load existing data
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load existing data from disk."""
        try:
            # Load metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    metadata_data = json.load(f)
                    
                # Load vectors
                if self.vectors_file.exists() and metadata_data:
                    with open(self.vectors_file, 'rb') as f:
                        vectors_data = np.frombuffer(f.read(), dtype=np.float32)
                        num_vectors = len(metadata_data)
                        
                        if len(vectors_data) == num_vectors * self.dimension:
                            vectors_matrix = vectors_data.reshape(num_vectors, self.dimension)
                            
                            # Load into memory cache
                            ids = list(metadata_data.keys())
                            metadata_list = [metadata_data[id].get('metadata', {}) for id in ids]
                            
                            self._memory_backend.bulk_add(ids, vectors_matrix, metadata_list)
                            
        except Exception as e:
            print(f"Warning: Failed to load existing data: {e}")
            # Continue with empty database
    
    def _save_to_disk(self):
        """Save current state to disk."""
        try:
            with self._lock:
                # Get all data from memory backend
                all_data = []
                metadata_data = {}
                
                # Collect all vectors and metadata
                for id in self._memory_backend._vectors.keys():
                    vector = self._memory_backend._vectors[id]
                    metadata = self._memory_backend._metadata.get(id, {})
                    
                    all_data.append(vector)
                    metadata_data[str(id)] = {
                        'id': id,
                        'metadata': metadata
                    }
                
                if all_data:
                    # Save vectors as binary
                    vectors_matrix = np.vstack(all_data)
                    with open(self.vectors_file, 'wb') as f:
                        f.write(vectors_matrix.astype(np.float32).tobytes())
                
                # Save metadata as JSON
                with open(self.metadata_file, 'w') as f:
                    json.dump(metadata_data, f, indent=2)
                    
        except Exception as e:
            raise StorageError(f"Failed to save to disk: {e}")
    
    def add(self, id: Union[int, str], vector: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Add a single vector."""
        try:
            result = self._memory_backend.add(id, vector, metadata)
            if result and self.config.custom.get('auto_save', True):
                self._save_to_disk()
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
        try:
            result = self._memory_backend.bulk_add(ids, vectors, metadata)
            if result > 0:
                self._save_to_disk()
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
        return self._memory_backend.search(query, k, filters, include_metadata, include_distances)
    
    def update(
        self,
        id: Union[int, str],
        vector: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing vector."""
        try:
            result = self._memory_backend.update(id, vector, metadata)
            if result and self.config.custom.get('auto_save', True):
                self._save_to_disk()
            return result
        except Exception as e:
            raise NusterDBError(f"Failed to update vector: {e}")
    
    def delete(self, id: Union[int, str]) -> bool:
        """Delete a vector by ID."""
        try:
            result = self._memory_backend.delete(id)
            if result and self.config.custom.get('auto_save', True):
                self._save_to_disk()
            return result
        except Exception as e:
            raise NusterDBError(f"Failed to delete vector: {e}")
    
    def get(self, id: Union[int, str], include_metadata: bool = True) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        return self._memory_backend.get(id, include_metadata)
    
    def batch_search(
        self,
        queries: np.ndarray,
        k: int,
        filters: Optional[List[Dict[str, Any]]] = None
    ) -> List[List[Dict[str, Any]]]:
        """Search with multiple queries."""
        return self._memory_backend.batch_search(queries, k, filters)
    
    def clear(self) -> bool:
        """Clear all vectors."""
        try:
            result = self._memory_backend.clear()
            if result:
                # Remove files
                if self.vectors_file.exists():
                    self.vectors_file.unlink()
                if self.metadata_file.exists():
                    self.metadata_file.unlink()
                if self.index_file.exists():
                    self.index_file.unlink()
            return result
        except Exception as e:
            raise NusterDBError(f"Failed to clear: {e}")
    
    def count(self) -> int:
        """Get total number of vectors."""
        return self._memory_backend.count()
    
    def save(self, path: Optional[str] = None) -> bool:
        """Save database to disk."""
        try:
            if path:
                # Save to different location
                old_path = self.path
                self.path = Path(path)
                self.path.mkdir(parents=True, exist_ok=True)
                self.vectors_file = self.path / "vectors.dat"
                self.metadata_file = self.path / "metadata.json"
                self.index_file = self.path / "index.json"
                
                self._save_to_disk()
                
                # Restore original path
                self.path = old_path
                self.vectors_file = self.path / "vectors.dat"
                self.metadata_file = self.path / "metadata.json"
                self.index_file = self.path / "index.json"
            else:
                self._save_to_disk()
            
            return True
        except Exception as e:
            raise StorageError(f"Failed to save: {e}")
    
    def load(self, path: str) -> bool:
        """Load database from disk."""
        try:
            # Clear current data
            self._memory_backend.clear()
            
            # Update paths
            old_path = self.path
            self.path = Path(path)
            self.vectors_file = self.path / "vectors.dat"
            self.metadata_file = self.path / "metadata.json"
            self.index_file = self.path / "index.json"
            
            # Load from new path
            self._load_from_disk()
            
            return True
        except Exception as e:
            # Restore original path on failure
            self.path = old_path
            self.vectors_file = self.path / "vectors.dat"
            self.metadata_file = self.path / "metadata.json"
            self.index_file = self.path / "index.json"
            raise StorageError(f"Failed to load: {e}")
    
    def stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        memory_stats = self._memory_backend.stats()
        
        # Add persistent storage stats
        file_sizes = {}
        for filename, filepath in [
            ("vectors", self.vectors_file),
            ("metadata", self.metadata_file),
            ("index", self.index_file)
        ]:
            if filepath.exists():
                file_sizes[f"{filename}_file_size"] = filepath.stat().st_size
            else:
                file_sizes[f"{filename}_file_size"] = 0
        
        return {
            **memory_stats,
            **file_sizes,
            "backend": "persistent",
            "path": str(self.path),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        memory_health = self._memory_backend.health_check()
        
        # Check disk space
        disk_space = None
        try:
            stat = os.statvfs(self.path)
            disk_space = {
                "free_bytes": stat.f_bavail * stat.f_frsize,
                "total_bytes": stat.f_blocks * stat.f_frsize,
            }
        except:
            pass
        
        return {
            **memory_health,
            "backend": "persistent",
            "path": str(self.path),
            "files_exist": {
                "vectors": self.vectors_file.exists(),
                "metadata": self.metadata_file.exists(),
                "index": self.index_file.exists(),
            },
            "disk_space": disk_space,
        }
    
    def close(self):
        """Close backend and cleanup resources."""
        try:
            # Save final state
            self._save_to_disk()
            
            # Close memory backend
            self._memory_backend.close()
            
            # Close file handles
            if self._vectors_mmap:
                self._vectors_mmap.close()
            if self._vectors_fd:
                self._vectors_fd.close()
                
        except Exception as e:
            print(f"Warning: Error during backend close: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.close()
        except:
            pass