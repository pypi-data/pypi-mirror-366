#!/usr/bin/env python3
"""
Test script to verify that WAL mode is enabled in the DatabaseVault.
"""

import os
import sqlite3
import threading
import time
from FernetKeyVault.database_vault import DatabaseVault

def test_wal_mode_enabled():
    """Test that WAL mode is enabled when DatabaseVault is initialized."""
    # Use a test database file
    test_db_path = "test_wal.db"
    
    # Remove the test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize the database vault
    vault = DatabaseVault(db_path=test_db_path)
    
    # Add a test entry
    vault.add_entry("test_key", "test_value")
    
    # Check if WAL mode is enabled
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode;")
    journal_mode = cursor.fetchone()[0]
    conn.close()
    
    print(f"Journal mode: {journal_mode}")
    assert journal_mode.upper() == "WAL", f"Expected WAL mode, got {journal_mode}"
    
    # Clean up
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    # Also remove WAL and SHM files
    if os.path.exists(f"{test_db_path}-wal"):
        os.remove(f"{test_db_path}-wal")
    if os.path.exists(f"{test_db_path}-shm"):
        os.remove(f"{test_db_path}-shm")
    
    print("WAL mode test passed!")

def concurrent_read_test():
    """Test that multiple readers can access the database concurrently."""
    # Use a test database file
    test_db_path = "test_concurrent.db"
    
    # Remove the test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize the database vault
    vault = DatabaseVault(db_path=test_db_path)
    
    # Add some test entries
    for i in range(10):
        vault.add_entry(f"key_{i}", f"value_{i}")
    
    # Function for reader threads
    def reader_thread(thread_id):
        local_vault = DatabaseVault(db_path=test_db_path)
        print(f"Thread {thread_id} starting reads")
        for i in range(10):
            value = local_vault.retrieve_entry(f"key_{i}")
            print(f"Thread {thread_id} read: key_{i} = {value}")
            time.sleep(0.1)  # Small delay to simulate work
        print(f"Thread {thread_id} completed")
    
    # Create and start multiple reader threads
    threads = []
    for i in range(3):  # Create 3 concurrent readers
        thread = threading.Thread(target=reader_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Clean up
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    # Also remove WAL and SHM files
    if os.path.exists(f"{test_db_path}-wal"):
        os.remove(f"{test_db_path}-wal")
    if os.path.exists(f"{test_db_path}-shm"):
        os.remove(f"{test_db_path}-shm")
    
    print("Concurrent read test completed!")

if __name__ == "__main__":
    print("Testing WAL mode in DatabaseVault...")
    test_wal_mode_enabled()
    print("\nTesting concurrent reads...")
    concurrent_read_test()
    print("\nAll tests passed!")