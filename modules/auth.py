"""
Authentication Module
Handles user registration, login, and secure API key encryption.
"""

import hashlib
import hmac
import os
import base64
from cryptography.fernet import Fernet


# Generate or load encryption key for API keys
def get_encryption_key() -> bytes:
    """Get or generate the encryption key for API keys."""
    key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".secret_key")
    
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        # Generate a new key
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(key)
        # Restrict permissions (Windows)
        os.chmod(key_file, 0o600)
        return key


def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    salt_hex = salt.hex()
    hash_hex = pwdhash.hex()
    return f"{salt_hex}${hash_hex}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt_hex, hash_hex = password_hash.split('$')
        salt = bytes.fromhex(salt_hex)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pwdhash.hex() == hash_hex
    except Exception:
        return False


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key using Fernet."""
    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(api_key.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_api_key(encrypted_api_key: str) -> str | None:
    """Decrypt an API key."""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(base64.b64decode(encrypted_api_key.encode('utf-8')))
        return decrypted.decode('utf-8')
    except Exception:
        return None


def is_valid_email(email: str) -> bool:
    """Basic email validation."""
    return "@" in email and "." in email.split("@")[1]


def is_valid_password(password: str) -> bool:
    """Validate password strength."""
    # At least 6 characters
    return len(password) >= 6
