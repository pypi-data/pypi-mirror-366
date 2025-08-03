import os
import pytest
import tempfile
from unittest.mock import patch
from FernetKeyVault.key_loader import KeyLoader, FileKeyLoader, EnvironmentKeyLoader


class TestFileKeyLoader:
    """Test suite for the FileKeyLoader class."""

    @pytest.fixture
    def sample_key(self):
        """Fixture that provides a sample key for testing."""
        return b'sample_key_for_testing_purposes_only'

    @pytest.fixture
    def temp_key_file(self, sample_key):
        """Fixture that creates a temporary key file for testing."""
        # Create a temporary file with the sample key
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(sample_key)
            temp_file_path = temp_file.name
        
        # Return the path to the temporary file
        yield temp_file_path
        
        # Clean up the temporary file after the test
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    def test_load_key_from_file(self, temp_key_file, sample_key):
        """Test that FileKeyLoader can load a key from a file."""
        # Create a FileKeyLoader instance
        key_loader = FileKeyLoader()
        
        # Load the key from the temporary file
        loaded_key = key_loader.load_key(temp_key_file)
        
        # Verify the loaded key matches the sample key
        assert loaded_key == sample_key

    def test_load_key_with_none_path(self):
        """Test that FileKeyLoader raises ValueError when key_file is None."""
        key_loader = FileKeyLoader()
        
        with pytest.raises(ValueError, match="Key file path cannot be None"):
            key_loader.load_key(None)

    def test_load_key_file_not_found(self):
        """Test that FileKeyLoader raises FileNotFoundError when the key file doesn't exist."""
        key_loader = FileKeyLoader()
        non_existent_file = "/path/to/non/existent/file"
        
        with pytest.raises(FileNotFoundError):
            key_loader.load_key(non_existent_file)

    def test_load_key_with_empty_file(self):
        """Test that FileKeyLoader can handle an empty key file."""
        # Create an empty temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            key_loader = FileKeyLoader()
            loaded_key = key_loader.load_key(temp_file_path)
            
            # The loaded key should be an empty bytes object
            assert loaded_key == b''
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)


class TestEnvironmentKeyLoader:
    """Test suite for the EnvironmentKeyLoader class."""

    @pytest.fixture
    def sample_key(self):
        """Fixture that provides a sample key for testing."""
        return "sample_env_key_for_testing"

    def test_load_key_from_environment(self, sample_key):
        """Test that EnvironmentKeyLoader can load a key from an environment variable."""
        # Set up the environment variable
        env_var_name = "TEST_MASTER_KEY"
        with patch.dict(os.environ, {env_var_name: sample_key}):
            # Create an EnvironmentKeyLoader instance
            key_loader = EnvironmentKeyLoader()
            
            # Load the key from the environment variable
            loaded_key = key_loader.load_key(env_var_name)
            
            # Verify the loaded key matches the sample key
            assert loaded_key == sample_key

    def test_load_key_env_var_not_set(self):
        """Test that EnvironmentKeyLoader returns None when the environment variable is not set."""
        # Ensure the environment variable doesn't exist
        env_var_name = "NON_EXISTENT_ENV_VAR"
        if env_var_name in os.environ:
            del os.environ[env_var_name]
        
        # Create an EnvironmentKeyLoader instance
        key_loader = EnvironmentKeyLoader()
        
        # Load the key from the non-existent environment variable
        loaded_key = key_loader.load_key(env_var_name)
        
        # Verify the loaded key is None
        assert loaded_key is None

    def test_load_key_default_env_var(self, sample_key):
        """Test that EnvironmentKeyLoader uses the default environment variable if none is specified."""
        # Set up the default environment variable
        default_env_var = "MASTER_KEY"
        with patch.dict(os.environ, {default_env_var: sample_key}):
            # Create an EnvironmentKeyLoader instance
            key_loader = EnvironmentKeyLoader()
            
            # Load the key without specifying an environment variable name
            loaded_key = key_loader.load_key()
            
            # Verify the loaded key matches the sample key
            assert loaded_key == sample_key