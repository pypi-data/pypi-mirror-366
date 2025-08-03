#!/usr/bin/env python3
"""
Test script to verify that the Singleton pattern with weak references works correctly
and prevents memory leaks.
"""

import gc
import sys
import weakref
import time

from FernetKeyVault import (
    get_database_vault,
    remove_database_vault_from_cache,
    clear_database_vault_cache
)

def test_singleton_pattern():
    """Test that the Singleton pattern returns the same instance for the same parameters."""
    print("Testing Singleton pattern...")
    
    # Get two instances with the same parameters
    vault1 = get_database_vault(db_path="./test_singleton.db", key_file="./master.key")
    vault2 = get_database_vault(db_path="./test_singleton.db", key_file="./master.key")
    
    # They should be the same object
    assert vault1 is vault2
    print("✓ get_database_vault returns the same instance for the same parameters")
    
    # Get an instance with different parameters
    vault3 = get_database_vault(db_path="./test_singleton_other.db", key_file="./master.key")
    
    # It should be a different object
    assert vault1 is not vault3
    print("✓ get_database_vault returns different instances for different parameters")

def test_weak_references():
    """Test that weak references allow objects to be garbage collected."""
    print("\nTesting weak references...")
    
    # Create a weak reference to track when the object is garbage collected
    callback_called = [False]
    
    def callback(ref):
        callback_called[0] = True
        print("✓ Object has been garbage collected")
    
    # Get an instance with unique parameters
    db_path = f"test_singleton_weak_{time.time()}.db"
    vault = get_database_vault(db_path=db_path, key_file="./master.key")
    
    # Create a weak reference to the instance
    weak_ref = weakref.ref(vault, callback)
    
    # The weak reference should return the object
    assert weak_ref() is vault
    print("✓ Weak reference returns the object")
    
    # Remove all references to the object
    vault = None
    
    # Force garbage collection
    gc.collect()
    
    # The weak reference should now return None
    assert weak_ref() is None
    assert callback_called[0]
    print("✓ Weak reference returns None after the object is garbage collected")

def test_explicit_cache_management():
    """Test explicit cache management functions."""
    print("\nTesting explicit cache management...")
    
    # Get an instance
    db_path = "../test_singleton_cache.db"
    vault = get_database_vault(db_path=db_path, key_file="./master.key")
    
    # Remove it from the cache
    result = remove_database_vault_from_cache(db_path=db_path, key_file="./master.key")
    assert result is True
    print("✓ remove_database_vault_from_cache returns True when the instance is found")
    
    # Get a new instance with the same parameters
    new_vault = get_database_vault(db_path=db_path, key_file="./master.key")
    
    # It should be a different object
    assert vault is not new_vault
    print("✓ get_database_vault returns a new instance after removing from cache")
    
    # Try to remove a non-existent instance
    result = remove_database_vault_from_cache(db_path="non_existent.db", key_file="./master.key")
    assert result is False
    print("✓ remove_database_vault_from_cache returns False when the instance is not found")
    
    # Clear the cache
    clear_database_vault_cache()
    
    # Get a new instance with the same parameters
    another_vault = get_database_vault(db_path=db_path, key_file="./master.key")
    
    # It should be a different object
    assert new_vault is not another_vault
    print("✓ get_database_vault returns a new instance after clearing the cache")

def main():
    """Run all tests."""
    test_singleton_pattern()
    test_weak_references()
    test_explicit_cache_management()
    print("\nAll tests passed!")

if __name__ == "__main__":
    main()