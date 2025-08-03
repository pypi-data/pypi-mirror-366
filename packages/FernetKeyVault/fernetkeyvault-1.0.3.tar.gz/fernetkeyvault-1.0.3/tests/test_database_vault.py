import os
import pytest
import sqlite3
from unittest.mock import Mock, patch

from FernetKeyVault.database_vault import DatabaseVault
from FernetKeyVault.encryption_manager import EncryptionManager
from FernetKeyVault.key_loader import KeyLoader


class TestDatabaseVault:
    """Test suite for the DatabaseVault class."""

    @pytest.fixture
    def test_db_path(self):
        """Fixture that provides a test database path."""
        db_path = "test_vault.db"
        # Clean up any existing test database
        if os.path.exists(db_path):
            os.remove(db_path)
        yield db_path
        # Clean up after tests
        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.fixture
    def mock_key_loader(self):
        """Fixture that provides a mock KeyLoader."""
        mock_loader = Mock(spec=KeyLoader)
        mock_loader.load_key.return_value = b'test_key_for_encryption_purposes_only=='
        return mock_loader

    @pytest.fixture
    def mock_encryption_manager(self):
        """Fixture that provides a mock EncryptionManager."""
        mock_manager = Mock(spec=EncryptionManager)
        
        # Configure the mock to "encrypt" by adding a prefix and "decrypt" by removing it
        def mock_encrypt(value):
            return f"encrypted_{value}".encode()
            
        def mock_decrypt(value):
            return value.decode().replace("encrypted_", "")
            
        mock_manager.encrypt.side_effect = mock_encrypt
        mock_manager.decrypt.side_effect = mock_decrypt
        
        return mock_manager

    @pytest.fixture
    def database_vault(self, test_db_path, mock_key_loader, mock_encryption_manager):
        """Fixture that provides a DatabaseVault instance with mocked dependencies."""
        return DatabaseVault(
            db_path=test_db_path,
            key_file="dummy_key.key",
            key_loader=mock_key_loader,
            encryption_manager=mock_encryption_manager
        )

    def test_initialization(self, test_db_path, mock_key_loader):
        """Test that DatabaseVault initializes correctly."""
        # Arrange
        key_file = "test_key.key"
        
        # Act
        vault = DatabaseVault(
            db_path=test_db_path,
            key_file=key_file,
            key_loader=mock_key_loader
        )
        
        # Assert
        assert vault.db_path == test_db_path
        assert vault.key_file == key_file
        assert vault.key_loader == mock_key_loader
        mock_key_loader.load_key.assert_called_once_with(key_file)
        
        # Verify the database was initialized
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vault'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_add_entry(self, database_vault, mock_encryption_manager):
        """Test adding an entry to the vault."""
        # Arrange
        key = "test_key"
        value = "test_value"
        
        # Act
        result = database_vault.add_entry(key, value)
        
        # Assert
        assert result is True
        mock_encryption_manager.encrypt.assert_called_once_with(value)

    def test_add_entry_with_non_string_key(self, database_vault):
        """Test that add_entry raises TypeError when key is not a string."""
        with pytest.raises(TypeError, match="Both key and value must be strings"):
            database_vault.add_entry(123, "value")

    def test_add_entry_with_non_string_value(self, database_vault):
        """Test that add_entry raises TypeError when value is not a string."""
        with pytest.raises(TypeError, match="Both key and value must be strings"):
            database_vault.add_entry("key", 123)

    def test_retrieve_entry(self, database_vault, mock_encryption_manager):
        """Test retrieving an entry from the vault."""
        # Arrange
        key = "test_key"
        value = "test_value"
        database_vault.add_entry(key, value)
        
        # Reset the mock to clear the call history
        mock_encryption_manager.encrypt.reset_mock()
        mock_encryption_manager.decrypt.reset_mock()
        
        # Act
        retrieved_value = database_vault.retrieve_entry(key)
        
        # Assert
        assert retrieved_value == value
        mock_encryption_manager.decrypt.assert_called_once()

    def test_retrieve_non_existent_entry(self, database_vault):
        """Test retrieving a non-existent entry from the vault."""
        # Act
        retrieved_value = database_vault.retrieve_entry("non_existent_key")
        
        # Assert
        assert retrieved_value is None

    def test_retrieve_entry_with_non_string_key(self, database_vault):
        """Test that retrieve_entry raises TypeError when key is not a string."""
        with pytest.raises(TypeError, match="Key must be a string"):
            database_vault.retrieve_entry(123)

    def test_delete_entry(self, database_vault):
        """Test deleting an entry from the vault."""
        # Arrange
        key = "test_key"
        value = "test_value"
        database_vault.add_entry(key, value)
        
        # Act
        result = database_vault.delete_entry(key)
        
        # Assert
        assert result is True
        assert database_vault.retrieve_entry(key) is None

    def test_delete_non_existent_entry(self, database_vault):
        """Test deleting a non-existent entry from the vault."""
        # Act
        result = database_vault.delete_entry("non_existent_key")
        
        # Assert
        assert result is False

    def test_delete_entry_with_non_string_key(self, database_vault):
        """Test that delete_entry raises TypeError when key is not a string."""
        with pytest.raises(TypeError, match="Key must be a string"):
            database_vault.delete_entry(123)

    def test_update_existing_entry(self, database_vault):
        """Test updating an existing entry in the vault."""
        # Arrange
        key = "test_key"
        original_value = "original_value"
        updated_value = "updated_value"
        
        # Add the original entry
        database_vault.add_entry(key, original_value)
        
        # Act - Update the entry
        result = database_vault.add_entry(key, updated_value)
        
        # Assert
        assert result is True
        assert database_vault.retrieve_entry(key) == updated_value

    @patch('FernetKeyVault.database_vault.sqlite3.connect')
    def test_database_error_handling_in_add_entry(self, mock_connect, database_vault):
        """Test error handling in add_entry when a database error occurs."""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Configure the mock to raise an exception when execute is called
        mock_cursor.execute.side_effect = sqlite3.Error("Test database error")
        
        # Act
        result = database_vault.add_entry("key", "value")
        
        # Assert
        assert result is False
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('FernetKeyVault.database_vault.sqlite3.connect')
    def test_database_error_handling_in_retrieve_entry(self, mock_connect, database_vault):
        """Test error handling in retrieve_entry when a database error occurs."""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Configure the mock to raise an exception when execute is called
        mock_cursor.execute.side_effect = sqlite3.Error("Test database error")
        
        # Act
        result = database_vault.retrieve_entry("key")
        
        # Assert
        assert result is None
        mock_conn.close.assert_called_once()

    @patch('FernetKeyVault.database_vault.sqlite3.connect')
    def test_database_error_handling_in_delete_entry(self, mock_connect, database_vault):
        """Test error handling in delete_entry when a database error occurs."""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Configure the mock to raise an exception when execute is called
        mock_cursor.execute.side_effect = sqlite3.Error("Test database error")
        
        # Act
        result = database_vault.delete_entry("key")
        
        # Assert
        assert result is False
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()