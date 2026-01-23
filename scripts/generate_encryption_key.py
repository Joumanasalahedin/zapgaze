#!/usr/bin/env python3
"""
Generate a new encryption key for GDPR pseudonymization.

Usage:
    python scripts/generate_encryption_key.py
    OR in Docker:
    docker-compose exec backend python scripts/generate_encryption_key.py
"""

from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    key_str = key.decode()

    print("=" * 60)
    print("Encryption Key Generated")
    print("=" * 60)
    print("\nAdd this EXACT line to your .env file (no spaces, no quotes):")
    print("-" * 60)
    print(f"ENCRYPTION_KEY={key_str}")
    print("-" * 60)
    print("\n⚠️  IMPORTANT:")
    print("  - Copy the ENTIRE line above (including ENCRYPTION_KEY=)")
    print("  - Paste it into your .env file")
    print("  - Make sure there are NO spaces before or after the = sign")
    print("  - Make sure there are NO quotes around the key")
    print("  - Store this key securely")
    print("  - Never commit it to version control")
    print("  - Back it up in a secure location")
    print("  - If lost, encrypted data cannot be decrypted")
    print("\nKey length:", len(key_str), "characters (correct)")
    print("=" * 60)
