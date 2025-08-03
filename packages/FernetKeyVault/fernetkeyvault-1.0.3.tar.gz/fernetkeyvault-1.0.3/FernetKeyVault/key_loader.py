# Define an interface for key loading
from abc import ABC, abstractmethod
import logging

# Get a module-level logger
logger = logging.getLogger('FernetKeyVault.key_loader')


class KeyLoader(ABC):
    @abstractmethod
    def load_key(self, key_file=None):
        """Load a key from a source"""
        pass

# Concrete implementation of the key loader
class FileKeyLoader(KeyLoader):
    def load_key(self, key_file=None):
        """
        Load a pass key from a file.

        Args:
            key_file (str): Path to the key file.

        Returns:
            str or None: The key as a string if successful, None otherwise

        Raises:
            FileNotFoundError: If the key file doesn't exist,
            ValueError: If key_file is None
        """

        if key_file is None:
            raise ValueError("Key file path cannot be None")

        try:
            with open(key_file, 'rb') as file:
                key = file.read().strip()
            return key
        except FileNotFoundError:
            logger.error(f"Key file '{key_file}' not found.")
            raise
        except Exception as e:
            logger.error(f"Error loading key: {e}")
            return None

# With a different key loader implementation
class EnvironmentKeyLoader(KeyLoader):
    def load_key(self, key_env_var="MASTER_KEY"):
        import os
        return os.environ.get(key_env_var)