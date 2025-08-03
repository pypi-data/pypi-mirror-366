from cryptography.fernet import Fernet


class EncryptionManager:
    def __init__(self, key: str):
        self.key = key

    def encrypt(self, value):
        """
        Encrypt a value using Fernet symmetric encryption.

        Args:
            value (str): The value to encrypt

        Returns:
            bytes: The encrypted value
        """
        if not isinstance(value, str):
            raise TypeError("Value must be a string")

        f = Fernet(self.key)
        return f.encrypt(value.encode())

    def decrypt(self, value: str):
        """
        Decrypt a value using Fernet symmetric encryption.

        Args:
            value (bytes): The encrypted value

        Returns:
            str: The decrypted value
        """
        if not isinstance(value, bytes):
            raise TypeError("Encrypted value must be bytes")

        f = Fernet(self.key)
        return f.decrypt(value).decode()