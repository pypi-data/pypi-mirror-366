"""
NusterDB API Client
==================

Client for connecting to NusterDB server instances.
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional, Union
import numpy as np

from .exceptions import ConnectionError, NusterDBError
from .utils import validate_vectors

class NusterClient:
    """
    Client for connecting to NusterDB server instances.
    
    Example:
        >>> client = NusterClient("http://localhost:7878")
        >>> client.add(1, [0.1, 0.2, 0.3])
        >>> results = client.search([0.1, 0.2, 0.3], k=5)
    """
    
    def __init__(
        self,
        url: str = "http://localhost:7878",
        timeout: int = 30,
        retry_attempts: int = 3,
        api_key: Optional[str] = None,
        verify_ssl: bool = True
    ):
        """
        Initialize NusterDB client.
        
        Args:
            url: Server URL
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
            api_key: Optional API key for authentication
            verify_ssl: Verify SSL certificates
        """
        self.url = url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        
        # Session for connection reuse
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to server."""
        try:
            response = self._request("GET", "/health")
            if response.status_code != 200:
                raise ConnectionError(f"Server returned status {response.status_code}")
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to {self.url}: {e}")
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = f"{self.url}{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, 
                        params=params,
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                else:
                    response = self.session.request(
                        method,
                        url,
                        json=data,
                        params=params,
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                
                if response.status_code < 500:  # Don't retry client errors
                    return response
                    
            except requests.RequestException as e:
                if attempt == self.retry_attempts - 1:
                    raise ConnectionError(f"Request failed after {self.retry_attempts} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return response
    
    def add(
        self, 
        id: Union[int, str], 
        vector: Union[List[float], np.ndarray],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a single vector."""
        try:
            if isinstance(vector, np.ndarray):
                vector = vector.tolist()
            
            data = {
                "id": id,
                "vector": vector,
                "metadata": metadata or {}
            }
            
            response = self._request("POST", "/vectors", data)
            
            if response.status_code == 200:
                return True
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Failed to add vector: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Add operation failed: {e}")
    
    def bulk_add(
        self,
        ids: List[Union[int, str]],
        vectors: Union[List[List[float]], np.ndarray],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """Add multiple vectors efficiently."""
        try:
            if isinstance(vectors, np.ndarray):
                vectors = vectors.tolist()
            
            # Prepare bulk data
            vectors_data = []
            for i, (vid, vector) in enumerate(zip(ids, vectors)):
                item = {
                    "id": vid,
                    "vector": vector,
                    "metadata": metadata[i] if metadata else {}
                }
                vectors_data.append(item)
            
            data = {"vectors": vectors_data}
            
            response = self._request("POST", "/vectors/bulk", data)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("added", len(vectors_data))
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Failed to bulk add vectors: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Bulk add operation failed: {e}")
    
    def search(
        self,
        query: Union[List[float], np.ndarray],
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_distances: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            if isinstance(query, np.ndarray):
                query = query.tolist()
            
            data = {
                "query": query,
                "k": k,
                "filters": filters or {},
                "include_metadata": include_metadata,
                "include_distances": include_distances
            }
            
            response = self._request("POST", "/search", data)
            
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Search failed: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Search operation failed: {e}")
    
    def update(
        self,
        id: Union[int, str],
        vector: Optional[Union[List[float], np.ndarray]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing vector."""
        try:
            data = {"id": id}
            
            if vector is not None:
                if isinstance(vector, np.ndarray):
                    vector = vector.tolist()
                data["vector"] = vector
            
            if metadata is not None:
                data["metadata"] = metadata
            
            response = self._request("PUT", f"/vectors/{id}", data)
            
            if response.status_code == 200:
                return True
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Failed to update vector: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Update operation failed: {e}")
    
    def delete(self, id: Union[int, str]) -> bool:
        """Delete a vector by ID."""
        try:
            response = self._request("DELETE", f"/vectors/{id}")
            
            if response.status_code == 200:
                return True
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Failed to delete vector: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Delete operation failed: {e}")
    
    def get(
        self, 
        id: Union[int, str],
        include_metadata: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        try:
            params = {"include_metadata": include_metadata}
            response = self._request("GET", f"/vectors/{id}", params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Failed to get vector: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Get operation failed: {e}")
    
    def batch_search(
        self,
        queries: Union[List[List[float]], np.ndarray],
        k: int = 10,
        filters: Optional[List[Dict[str, Any]]] = None
    ) -> List[List[Dict[str, Any]]]:
        """Search with multiple queries."""
        try:
            if isinstance(queries, np.ndarray):
                queries = queries.tolist()
            
            data = {
                "queries": queries,
                "k": k,
                "filters": filters or []
            }
            
            response = self._request("POST", "/batch_search", data)
            
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Batch search failed: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Batch search operation failed: {e}")
    
    def count(self) -> int:
        """Get total number of vectors."""
        try:
            response = self._request("GET", "/stats")
            
            if response.status_code == 200:
                stats = response.json()
                return stats.get("vector_count", 0)
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Failed to get count: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Count operation failed: {e}")
    
    def stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            response = self._request("GET", "/stats")
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Failed to get stats: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Stats operation failed: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            response = self._request("GET", "/health")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "healthy": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    def clear(self) -> bool:
        """Clear all vectors."""
        try:
            response = self._request("DELETE", "/vectors/clear")
            
            if response.status_code == 200:
                return True
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise NusterDBError(f"Failed to clear database: {error_msg}")
                
        except Exception as e:
            raise NusterDBError(f"Clear operation failed: {e}")
    
    def close(self):
        """Close the client session."""
        if self.session:
            self.session.close()