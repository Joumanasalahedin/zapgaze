"""
Encryption utilities for GDPR compliance.
Uses Fernet symmetric encryption to encrypt personal data at rest.
"""

from cryptography.fernet import Fernet
import os
import secrets
import string

# Get encryption key from environment variable
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError(
        "ENCRYPTION_KEY environment variable is required.\n"
        "Generate one with:\n"
        "  python scripts/generate_encryption_key.py\n"
        "  OR\n"
        "  python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'\n"
        "Then add it to your .env file:\n"
        "  ENCRYPTION_KEY=your_generated_key_here"
    )

# Strip whitespace (common issue when copying keys)
ENCRYPTION_KEY = ENCRYPTION_KEY.strip()

# Validate key format
if len(ENCRYPTION_KEY) < 32:
    raise ValueError(
        f"ENCRYPTION_KEY is too short ({len(ENCRYPTION_KEY)} characters). "
        "Fernet keys must be 32 url-safe base64-encoded bytes (typically 44 characters).\n"
        "Generate a new key with: python scripts/generate_encryption_key.py"
    )

try:
    cipher = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    raise ValueError(
        f"Invalid ENCRYPTION_KEY format: {e}\n"
        "The key must be a valid Fernet key (32 url-safe base64-encoded bytes).\n"
        "Generate a new key with: python scripts/generate_encryption_key.py\n"
        "Make sure there are no extra spaces or characters in your .env file."
    )


def encrypt(data: str) -> str:
    """
    Encrypt a string using Fernet symmetric encryption.

    Args:
        data: Plain text string to encrypt

    Returns:
        Encrypted string (base64 encoded)
    """
    if not data:
        return ""
    return cipher.encrypt(data.encode()).decode()


def decrypt(encrypted_data: str) -> str:
    """
    Decrypt a string that was encrypted with encrypt().

    Args:
        encrypted_data: Encrypted string (base64 encoded)

    Returns:
        Decrypted plain text string
    """
    if not encrypted_data:
        return ""
    try:
        return cipher.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        # If decryption fails, might be unencrypted data (for migration)
        # Return as-is and log warning
        import logging

        logging.warning(f"Decryption failed, returning as-is: {e}")
        return encrypted_data


def generate_pseudonym_id() -> str:
    """
    Generate a pseudonymized ID for analytics.
    Format: PSEUDO-{random_alphanumeric}

    Returns:
        Pseudonymized ID string
    """
    random_part = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8)
    )
    return f"PSEUDO-{random_part}"
