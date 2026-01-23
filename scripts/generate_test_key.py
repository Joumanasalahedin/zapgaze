#!/usr/bin/env python3
"""
Generate a test encryption key for unit tests.
This key should only be used for testing, never in production.
"""

from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    key_str = key.decode()
    
    print("Test Encryption Key (for conftest.py):")
    print("=" * 60)
    print(f'os.environ["ENCRYPTION_KEY"] = "{key_str}"')
    print("=" * 60)
    print(f"\nKey length: {len(key_str)} characters (valid)")
