#!/usr/bin/env python3
"""
Test script for validating the input validation in vault.py
"""

import os
import subprocess
import tempfile

def test_key_file_validation():
    """Test validation of key file existence"""
    print("\n=== Testing key file validation ===")
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.key', delete=False) as temp_file:
        temp_file.write(b'some key data')
        temp_key_path = temp_file.name
    
    # Test with non-existent key file
    non_existent_key = "non_existent.key"
    print(f"Testing with non-existent key file: {non_existent_key}")
    result = subprocess.run(
        ["python", "vault.py", "retrieve", "--key_file", non_existent_key],
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    # The error message might be in stdout or stderr depending on how logging is configured
    assert "does not exist" in result.stderr or "does not exist" in result.stdout
    
    # Test with existing key file
    print(f"Testing with existing key file: {temp_key_path}")
    result = subprocess.run(
        ["python", "vault.py", "retrieve", "--key_file", temp_key_path],
        input="valid_key\n",
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    
    # Clean up
    os.unlink(temp_key_path)

def test_key_validation():
    """Test validation of key format"""
    print("\n=== Testing key validation ===")
    
    # Test with empty key
    print("Testing with empty key")
    result = subprocess.run(
        ["python", "vault.py", "retrieve", "--key_file", "master.key"],
        input="\n",
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    assert "Key cannot be empty" in result.stderr or "Key cannot be empty" in result.stdout
    
    # Test with invalid key (special characters)
    print("Testing with invalid key (special characters)")
    result = subprocess.run(
        ["python", "vault.py", "retrieve", "--key_file", "master.key"],
        input="invalid@key\n",
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    assert "Key can only contain" in result.stderr or "Key can only contain" in result.stdout
    
    # Test with valid key
    print("Testing with valid key")
    result = subprocess.run(
        ["python", "vault.py", "retrieve", "--key_file", "master.key"],
        input="valid_key\n",
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    
def test_value_validation():
    """Test validation of value format"""
    print("\n=== Testing value validation ===")
    
    # Test with empty value
    print("Testing with empty value")
    result = subprocess.run(
        ["python", "vault.py", "add", "--key_file", "master.key"],
        input="valid_key\n\n",
        capture_output=True,
        text=True
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    assert "Value cannot be empty" in result.stderr or "Value cannot be empty" in result.stdout

if __name__ == "__main__":
    # Make sure master.key exists for testing
    if not os.path.exists("master.key"):
        with open("master.key", "wb") as f:
            f.write(b"test_key_for_validation")
        print("Created master.key for testing")
    
    test_key_file_validation()
    test_key_validation()
    test_value_validation()
    
    print("\nAll tests completed.")