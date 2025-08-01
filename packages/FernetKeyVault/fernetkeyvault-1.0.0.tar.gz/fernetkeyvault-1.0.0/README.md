# Fernet Key Vault

A simple Python SQLite3-based key-value storage vault for securely storing and retrieving data. Note: Despite the repository name, the current implementation does not include Fernet encryption.

## Features

- Store key-value pairs in an SQLite database
- Retrieve values using their associated keys
- Delete entries from the vault
- Automatic database initialization
- Error handling and input validation

## Installation

### From Source

You can install the package directly from the source code:

```bash
# Clone the repository
git clone https://github.com/kvcrajan/FernetKeyVault.git
cd FernetKeyVault

# Install the package
pip install .
```

For development, you can install the package in editable mode:

```bash
pip install -e .
```

### Dependencies

No special dependencies are required beyond Python's standard library. The implementation uses the built-in `sqlite3` module.

## Usage

### Basic Usage

```python
from database_vault import DatabaseVault  # Import the DatabaseVault class

# Initialize the vault (creates vault.db by default)
vault = DatabaseVault()

# Add entries
vault.add_entry("username", "admin")
vault.add_entry("api_key", "sk_test_abcdefghijklmnopqrstuvwxyz")

# Retrieve entries
username = vault.retrieve_entry("username")
print(f"Username: {username}")  # Output: Username: admin

# Delete entries
vault.delete_entry("username")
```

### Custom Database Path

You can specify a custom path for the database file:

```python
from database_vault import DatabaseVault

vault = DatabaseVault(db_path="/path/to/custom/vault.db")
```

### Error Handling

The methods return appropriate values to indicate success or failure:

- `add_entry()`: Returns `True` if successful, `False` otherwise
- `retrieve_entry()`: Returns the value if found, `None` otherwise
- `delete_entry()`: Returns `True` if an entry was deleted, `False` otherwise

## API Reference

### `DatabaseVault(db_path="vault.db")`

Initialize a new DatabaseVault instance.

**Parameters:**
- `db_path` (str, optional): Path to the SQLite database file. Defaults to "vault.db".

### `add_entry(key, value)`

Add a key-value pair to the vault. If the key already exists, its value will be updated.

**Parameters:**
- `key` (str): The key for the entry
- `value` (str): The value to store

**Returns:**
- `bool`: True if successful, False otherwise

**Raises:**
- `TypeError`: If key or value is not a string

### `retrieve_entry(key)`

Retrieve a value from the vault using its key.

**Parameters:**
- `key` (str): The key to look up

**Returns:**
- `str` or `None`: The value associated with the key, or None if the key doesn't exist

**Raises:**
- `TypeError`: If key is not a string

### `delete_entry(key)`

Delete an entry from the vault using its key.

**Parameters:**
- `key` (str): The key of the entry to delete

**Returns:**
- `bool`: True if an entry was deleted, False otherwise

**Raises:**
- `TypeError`: If key is not a string

## Testing

Run the included test script to verify the functionality:

```bash
python test_database_vault.py
```

The test script creates a temporary database, tests all functionality, and then removes the test database.