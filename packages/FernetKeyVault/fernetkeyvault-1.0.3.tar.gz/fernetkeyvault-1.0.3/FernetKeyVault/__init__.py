"""
FernetKeyVault - A simple Python SQLite3-based key-value storage vault.

This package provides a DatabaseVault class for securely storing and retrieving data.
"""

__version__ = '1.0.3'

from typing import Any, Dict, Tuple, Optional
import time
import logging
import sys
import weakref

# Create a logger for the package
logger = logging.getLogger('FernetKeyVault')
logger.setLevel(logging.INFO)

# Prevent duplicate log messages by disabling propagation to the root logger
logger.propagate = False

# Ensure the logger has a handler if it doesn't already
if not logger.handlers:
    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(console_handler)


# Cache with TTL, size limit, and weak references to prevent memory leaks
class VaultCache:
    def __init__(self, max_size=10, ttl=3600):
        # Use a dictionary of weak references to prevent memory leaks
        self.cache: Dict[Tuple[str, str], Tuple[weakref.ReferenceType, float]] = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.logger = logging.getLogger('FernetKeyVault.cache')

    def get(self, key) -> Optional[Any]:
        """
        Get an item from the cache if it exists and is not expired.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found or expired
        """
        if key in self.cache:
            ref, timestamp = self.cache[key]
            instance = ref()  # Dereference the weak reference
            
            # Check if the reference is still alive
            if instance is None:
                # The object has been garbage collected
                self.logger.debug(f"Object for key {key} has been garbage collected")
                del self.cache[key]
                return None
                
            # Check if the entry has expired
            if time.time() - timestamp < self.ttl:
                return instance
            else:
                # Expired
                self.logger.debug(f"Cache entry for key {key} has expired")
                del self.cache[key]
                
        return None

    def set(self, key, value):
        """
        Add or update an item in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
        """
        # If the cache is full, remove the oldest entry
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
            self.logger.debug(f"Cache full, removing oldest entry: {oldest_key}")
            del self.cache[oldest_key]

        # Store with weak reference and timestamp
        self.cache[key] = (weakref.ref(value), time.time())
        
    def remove(self, key):
        """
        Explicitly remove an item from the cache.
        
        Args:
            key: The cache key to remove
            
        Returns:
            bool: True if the key was found and removed, False otherwise
        """
        if key in self.cache:
            del self.cache[key]
            self.logger.debug(f"Explicitly removed cache entry for key {key}")
            return True
        return False
        
    def clear(self):
        """Clear all entries from the cache."""
        self.cache.clear()
        self.logger.debug("Cache cleared")

# Create a singleton cache instance
_vault_cache = VaultCache()

def get_database_vault(db_path: str="vault.db", key_file: str="master.key", **kwargs: dict[str, Any]):
    """
    Return a singleton instance of DatabaseVault with caching behavior.
    
    This function implements the Singleton pattern with weak references to prevent memory leaks.
    It ensures that only one instance of DatabaseVault exists for a given database path and key file.

    Args:
        db_path (str): Path to the SQLite database file. Defaults to "vault.db".
        key_file (str): Path to the key file. Defaults to "master.key".
        **kwargs: Additional arguments to pass to the DatabaseVault constructor.

    Returns:
        DatabaseVault: A singleton instance of the DatabaseVault class.
    """
    # Create a cache key based on the db_path and key_file
    cache_key: tuple[str, str] = (db_path, key_file)

    # Try to get the instance from the cache
    instance = _vault_cache.get(cache_key)
    if instance is None:
        # If not in cache or expired, create a new instance
        from .database_vault import DatabaseVault
        instance = DatabaseVault(db_path=db_path, key_file=key_file, **kwargs)
        _vault_cache.set(cache_key, instance)
        logger.debug(f"Created new DatabaseVault instance for {db_path} with key {key_file}")
    else:
        logger.debug(f"Using cached DatabaseVault instance for {db_path} with key {key_file}")

    return instance


def remove_database_vault_from_cache(db_path: str="vault.db", key_file: str="master.key") -> bool:
    """
    Explicitly remove a DatabaseVault instance from the cache.
    
    This can be useful for managing memory usage or forcing a new instance to be created
    on the next call to get_database_vault.
    
    Args:
        db_path (str): Path to the SQLite database file. Defaults to "vault.db".
        key_file (str): Path to the key file. Defaults to "master.key".
        
    Returns:
        bool: True if the instance was found and removed, False otherwise.
    """
    cache_key: tuple[str, str] = (db_path, key_file)
    return _vault_cache.remove(cache_key)


def clear_database_vault_cache() -> None:
    """
    Clear all DatabaseVault instances from the cache.
    
    This can be useful for managing memory usage or forcing new instances to be created
    on later calls to get_database_vault.
    """
    _vault_cache.clear()