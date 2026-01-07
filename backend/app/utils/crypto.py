import base64
import os
import hashlib
from cryptography.fernet import Fernet
from flask import current_app

def get_fernet():
    # Derive a stable 32-byte key from SECRET_KEY
    secret = current_app.config.get('SECRET_KEY', 'fallback-secret-key').encode()
    # Use SHA256 to get a stable 32-byte hash
    key_32 = hashlib.sha256(secret).digest()
    # Fernet requires base64 encoded 32 bytes
    fernet_key = base64.urlsafe_b64encode(key_32)
    return Fernet(fernet_key)

def encrypt_key(plain_text):
    if not plain_text:
        return None
    f = get_fernet()
    return f.encrypt(plain_text.encode()).decode()

def decrypt_key(encrypted_text):
    if not encrypted_text:
        return None
    try:
        f = get_fernet()
        return f.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return None
