import pytest
from cryptography.fernet import Fernet
from FernetKeyVault.encryption_manager import EncryptionManager


class TestEncryptionManager:
    """Test suite for the EncryptionManager class."""

    @pytest.fixture
    def valid_key(self):
        """Fixture that provides a valid Fernet key for testing."""
        return Fernet.generate_key()

    @pytest.fixture
    def encryption_manager(self, valid_key):
        """Fixture that provides an EncryptionManager instance for testing."""
        return EncryptionManager(valid_key)

    def test_initialization(self, valid_key):
        """Test that EncryptionManager initializes correctly with a valid key."""
        manager = EncryptionManager(valid_key)
        assert manager.key == valid_key

    def test_encrypt_decrypt_cycle(self, encryption_manager):
        """Test that a value can be encrypted and then decrypted back to the original."""
        original_value = "test_secret_value"
        
        # Encrypt the value
        encrypted_value = encryption_manager.encrypt(original_value)
        
        # Verify the encrypted value is bytes and different from the original
        assert isinstance(encrypted_value, bytes)
        assert encrypted_value != original_value.encode()
        
        # Decrypt the value
        decrypted_value = encryption_manager.decrypt(encrypted_value)
        
        # Verify the decrypted value matches the original
        assert decrypted_value == original_value

    def test_encrypt_with_non_string_value(self, encryption_manager):
        """Test that encrypt raises TypeError when given a non-string value."""
        with pytest.raises(TypeError, match="Value must be a string"):
            encryption_manager.encrypt(123)  # Integer instead of string

    def test_decrypt_with_non_bytes_value(self, encryption_manager):
        """Test that decrypt raises TypeError when given a non-bytes value."""
        with pytest.raises(TypeError, match="Encrypted value must be bytes"):
            encryption_manager.decrypt("not_bytes")  # String instead of bytes

    def test_decrypt_with_invalid_token(self, encryption_manager):
        """Test that decrypt raises an error when given invalid encrypted data."""
        with pytest.raises(Exception):  # Fernet will raise an exception for invalid tokens
            encryption_manager.decrypt(b"invalid_encrypted_data")

    def test_different_keys_incompatible(self, valid_key):
        """Test that data encrypted with one key cannot be decrypted with another."""
        # Create two managers with different keys
        manager1 = EncryptionManager(valid_key)
        manager2 = EncryptionManager(Fernet.generate_key())  # Different key
        
        # Encrypt with first manager
        original_value = "test_secret_value"
        encrypted_value = manager1.encrypt(original_value)
        
        # Try to decrypt with second manager (should fail)
        with pytest.raises(Exception):  # Fernet will raise an exception
            manager2.decrypt(encrypted_value)

    def test_empty_string_encryption(self, encryption_manager):
        """Test that an empty string can be encrypted and decrypted correctly."""
        empty_string = ""
        
        # Encrypt and decrypt
        encrypted = encryption_manager.encrypt(empty_string)
        decrypted = encryption_manager.decrypt(encrypted)
        
        assert decrypted == empty_string

    def test_special_characters(self, encryption_manager):
        """Test that strings with special characters can be encrypted and decrypted correctly."""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?\\`~"
        
        # Encrypt and decrypt
        encrypted = encryption_manager.encrypt(special_chars)
        decrypted = encryption_manager.decrypt(encrypted)
        
        assert decrypted == special_chars

    def test_unicode_characters(self, encryption_manager):
        """Test that strings with Unicode characters can be encrypted and decrypted correctly."""
        unicode_string = "こんにちは世界 • Hello World • مرحبا بالعالم"
        
        # Encrypt and decrypt
        encrypted = encryption_manager.encrypt(unicode_string)
        decrypted = encryption_manager.decrypt(encrypted)
        
        assert decrypted == unicode_string