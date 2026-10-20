from cryptography.fernet import Fernet
from app.core.config import settings

# Initialize the cipher suite using the key from .env
cipher_suite = Fernet(settings.encryption_key.encode())

def encrypt_token(token: str) -> str:
    """Encrypts a plain text token."""
    if not token:
        return ""
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypts an encrypted token."""
    if not encrypted_token:
        return ""
    return cipher_suite.decrypt(encrypted_token.encode()).decode()