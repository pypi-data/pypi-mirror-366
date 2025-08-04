"""
NusterDB Exceptions
==================

Custom exception classes for NusterDB operations.
"""

class NusterDBError(Exception):
    """Base exception class for all NusterDB errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class ConnectionError(NusterDBError):
    """Raised when connection to NusterDB server fails."""
    pass

class SecurityError(NusterDBError):
    """Raised when security validation fails."""
    pass

class IndexError(NusterDBError):
    """Raised when index operations fail."""
    pass

class ConfigurationError(NusterDBError):
    """Raised when configuration is invalid."""
    pass

class ValidationError(NusterDBError):
    """Raised when input validation fails."""
    pass

class StorageError(NusterDBError):
    """Raised when storage operations fail."""
    pass

class AuthenticationError(SecurityError):
    """Raised when authentication fails."""
    pass

class AuthorizationError(SecurityError):
    """Raised when authorization fails."""
    pass

class EncryptionError(SecurityError):
    """Raised when encryption/decryption fails."""
    pass