"""
Tests for the FernetKeyVault package with logging.
"""

import os
import logging
import sys
import pytest
from cryptography.fernet import Fernet
from FernetKeyVault import get_database_vault
from FernetKeyVault.key_loader import FileKeyLoader

# Configure logging to see all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Test database and key file
TEST_DB = "test_logging.db"
TEST_KEY = "master.key"

# Generate a valid Fernet key for testing
TEST_FERNET_KEY = Fernet.generate_key()


@pytest.fixture(scope="function")
def logger():
    """Fixture to provide a logger for tests."""
    logger = logging.getLogger('test_script')
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture(scope="function")
def clean_db():
    """Fixture to clean up the test database before and after tests."""
    # Clean up any existing test database before test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Provide the test database path
    yield TEST_DB
    
    # Clean up after test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture(scope="function")
def env_key():
    """Fixture to set and clean up the MASTER_KEY environment variable."""
    # Set the environment variable with the test key
    os.environ["MASTER_KEY"] = TEST_FERNET_KEY.decode()
    
    # Provide the key for tests
    yield TEST_FERNET_KEY
    
    # Clean up after test (optional, but good practice)
    if "MASTER_KEY" in os.environ:
        del os.environ["MASTER_KEY"]


class TestLogging:
    """Test class for FernetKeyVault with logging."""
    
    def test_logging_basics(self, logger):
        """Test that basic logging works."""
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        # No assertions needed, just verifying logs are produced without errors
    
    def test_nonexistent_key_file(self, logger, clean_db, monkeypatch):
        """Test behavior with a missing environment variable."""
        # Remove the MASTER_KEY environment variable if it exists
        monkeypatch.delenv("MASTER_KEY", raising=False)
        
        # Create a vault with explicit FileKeyLoader for a non-existent file
        with pytest.raises(Exception):
            get_database_vault(clean_db, "non_existent_key.file", key_loader=FileKeyLoader())
    
    def test_add_entry(self, logger, clean_db, env_key):
        """Test adding an entry to the vault."""
        vault = get_database_vault(clean_db)
        vault.add_entry("test_key", "test_value")
        
        # Verify the entry was added
        value = vault.retrieve_entry("test_key")
        assert value == "test_value"
    
    def test_add_entry_with_invalid_key_type(self, logger, clean_db, env_key):
        """Test adding an entry with an invalid key type."""
        vault = get_database_vault(clean_db)
        
        with pytest.raises(Exception):
            vault.add_entry(123, "test_value")
    
    def test_add_entry_with_invalid_value_type(self, logger, clean_db, env_key):
        """Test adding an entry with an invalid value type."""
        vault = get_database_vault(clean_db)
        
        with pytest.raises(Exception):
            vault.add_entry("test_key", 123)
    
    def test_retrieve_entry(self, logger, clean_db, env_key):
        """Test retrieving an entry from the vault."""
        vault = get_database_vault(clean_db)
        vault.add_entry("test_key", "test_value")
        
        value = vault.retrieve_entry("test_key")
        assert value == "test_value"
    
    def test_retrieve_nonexistent_entry(self, logger, clean_db, env_key):
        """Test retrieving a non-existent entry."""
        vault = get_database_vault(clean_db)
        
        value = vault.retrieve_entry("non_existent_key")
        assert value is None
    
    def test_delete_entry(self, logger, clean_db, env_key):
        """Test deleting an entry from the vault."""
        vault = get_database_vault(clean_db)
        vault.add_entry("test_key", "test_value")
        
        result = vault.delete_entry("test_key")
        assert result is True
        
        # Verify the entry was deleted
        value = vault.retrieve_entry("test_key")
        assert value is None
    
    def test_delete_nonexistent_entry(self, logger, clean_db, env_key):
        """Test deleting a non-existent entry."""
        vault = get_database_vault(clean_db)
        
        result = vault.delete_entry("non_existent_key")
        assert result is False