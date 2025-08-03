import sqlite3
from sqlite3 import Connection, Cursor
from typing import Any
import logging

from .key_loader import FileKeyLoader, EnvironmentKeyLoader, KeyLoader
from .encryption_manager import EncryptionManager

# Get a module-level logger
logger = logging.getLogger('FernetKeyVault.database_vault')


class DatabaseVault:
    """
    A class for securely storing key-value pairs in an SQLite database.
    Provides methods to add, retrieve, and delete entries.
    """

    def __init__(self, db_path: str="vault.db", key_file: str="master.key", key_loader: KeyLoader=None, encryption_manager: EncryptionManager=None):
        """
        Initialize the DatabaseVault with the specified database path.

        Args:
            db_path (str): Path to the SQLite database file. Defaults to "vault.db".
            key_file (str): Path to the key file. Defaults to "master.key".
            key_loader (KeyLoader): Key loader implementation. Defaults to EnvironmentKeyLoader.
        """
        self.db_path: str = db_path
        self.key_file: str = key_file
        self.key_loader: KeyLoader = key_loader or EnvironmentKeyLoader()

        self._initialize_encryption_manager(encryption_manager)
        self._initialize_db()

    def _initialize_encryption_manager(self, encryption_manager: EncryptionManager=None) -> None:
        # Handle different key loader types appropriately
        if isinstance(self.key_loader, FileKeyLoader):
            # For FileKeyLoader, pass the key_file path
            encryption_key = self.key_loader.load_key(self.key_file)
        elif isinstance(self.key_loader, EnvironmentKeyLoader):
            # For EnvironmentKeyLoader, use the default environment variable
            encryption_key = self.key_loader.load_key()
        else:
            # For other KeyLoader implementations, pass the key_file as a parameter
            # This maintains backward compatibility with custom KeyLoader implementations
            encryption_key = self.key_loader.load_key(self.key_file)
            
        self.encryption_manager: EncryptionManager = encryption_manager or EncryptionManager(encryption_key)

    def _initialize_db(self) -> None:
        """
        Initialize the database by creating the necessary table if it doesn't exist.
        Also enables WAL (Write-Ahead Logging) mode for better concurrency support.
        """
        conn:Connection = None
        try:
            conn, cursor = self._get_cursor()
            
            # Create the vault table if it doesn't exist
            # noinspection SqlNoDataSourceInspection
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vault (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def add_entry(self, key: str, value: str) -> bool:
        """
        Add a key-value pair to the vault.
        If the key already exists, its value will be updated.
        
        Args:
            key (str): The key for the entry
            value (str): The value to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("Both key and value must be strings")

        encrypted_value: str = self.encryption_manager.encrypt(value)
            
        conn:Connection = None
        try:
            conn, cursor = self._get_cursor()
            
            # Use REPLACE to handle both insert and update cases
            # noinspection SqlNoDataSourceInspection
            cursor.execute('''
                INSERT OR REPLACE INTO vault (key, value) VALUES (?, ?)
            ''', (key, encrypted_value))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding entry: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def retrieve_entry(self, key: str) -> str:
        """
        Retrieve a value from the vault using its key.
        
        Args:
            key (str): The key to look up
            
        Returns:
            str or None: The value associated with the key, or None if the key doesn't exist
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
            
        conn:Connection = None
        try:
            conn, cursor = self._get_cursor()
            
            # noinspection SqlNoDataSourceInspection
            cursor.execute('''
                SELECT value FROM vault WHERE key = ?
            ''', (key,))
            
            result:Any = cursor.fetchone()
            return self.encryption_manager.decrypt(result[0]) if result else None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving entry: {e}")
            return None
        finally:
            if conn:
                conn.close()


    def delete_entry(self, key: str) -> bool:
        """
        Delete an entry from the vault using its key.
        
        Args:
            key (str): The key of the entry to delete
            
        Returns:
            bool: True if an entry was deleted, False otherwise
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
            
        conn:Connection = None
        try:
            conn, cursor = self._get_cursor()
            
            # noinspection SqlNoDataSourceInspection
            cursor.execute('''
                DELETE FROM vault WHERE key = ?
            ''', (key,))
            
            deleted:bool = cursor.rowcount > 0
            conn.commit()
            return deleted
        except sqlite3.Error as e:
            logger.error(f"Error deleting entry: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def _get_cursor(self) -> tuple[Connection, Cursor]:
        """
        Get a database cursor along with its connection.

        Returns:
            tuple[Connection, Cursor]: A tuple containing the SQLite database connection and cursor
        """
        conn:Connection = sqlite3.connect(self.db_path)
        cursor:Cursor = conn.cursor()

        try:
            # Enable WAL mode for better concurrency (multiple readers)
            cursor.execute('PRAGMA journal_mode=WAL')
        except sqlite3.Error as e:
            # Log the error but continue, as WAL mode is an optimization, not a requirement
            logger.warning(f"Could not enable WAL mode: {e}")

        return conn, cursor