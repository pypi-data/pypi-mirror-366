import platform
import getpass
import keyring
from keyring.backend import KeyringBackend
import json
import base64
from typing import Optional, List, Dict
from cryptography.fernet import Fernet

SERVICE_NAME = "muerte32crypt"
_INDEX_KEY = "_muerte_index"

# ================================
# Backend detection & availability
# ================================

def is_secure_store_available() -> bool:
    return platform.system() in ["Windows", "Darwin", "Linux"]

def get_backend_name() -> str:
    return str(keyring.get_keyring())

# ===================
# Basic CRUD Wrappers
# ===================

def store_secret(name: str, secret: str):
    keyring.set_password(SERVICE_NAME, name, secret)

def retrieve_secret(name: str) -> Optional[str]:
    return keyring.get_password(SERVICE_NAME, name)

def delete_secret(name: str):
    keyring.delete_password(SERVICE_NAME, name)

def secret_exists(name: str) -> bool:
    return retrieve_secret(name) is not None

# ==============
# Interactive Use
# ==============

def secure_prompt_store(name: str):
    secret = getpass.getpass(f"Enter secret for '{name}': ")
    store_secret(name, secret)

# ==============
# Advanced Use
# ==============

def list_stored_secrets() -> List[str]:
    try:
        backend: KeyringBackend = keyring.get_keyring()
        return backend.get_credential(SERVICE_NAME, None)
    except Exception:
        raise NotImplementedError("Listing stored secrets not supported on this backend.")

def get_all_service_items(service: str = SERVICE_NAME) -> Dict[str, str]:
    secrets = {}
    names = _load_index()
    for name in names:
        try:
            val = keyring.get_password(service, name)
            if val is not None:
                secrets[name] = val
        except Exception:
            continue
    return secrets

def store_secret(name: str, secret: str):
    keyring.set_password(SERVICE_NAME, name, secret)
    _add_to_index(name)

def delete_secret(name: str):
    keyring.delete_password(SERVICE_NAME, name)
    _remove_from_index(name)

def clear_all_secrets():
    for name in _load_index():
        delete_secret(name)
    _save_index([])  # Clear index

# ======================
# Index Functions
# ======================

def _load_index() -> list[str]:
    index_blob = keyring.get_password(SERVICE_NAME, _INDEX_KEY)
    if index_blob:
        try:
            return json.loads(index_blob)
        except json.JSONDecodeError:
            return []
    return []

def _save_index(names: list[str]):
    keyring.set_password(SERVICE_NAME, _INDEX_KEY, json.dumps(names))

def _add_to_index(name: str):
    names = _load_index()
    if name not in names:
        names.append(name)
        _save_index(names)

def _remove_from_index(name: str):
    names = _load_index()
    if name in names:
        names.remove(name)
        _save_index(names)

# ======================
# Local Encryption Layer
# ======================

def generate_local_key() -> bytes:
    return Fernet.generate_key()

def encrypt_locally(secret: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(secret.encode()).decode()

def decrypt_locally(token: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()

def store_encrypted_secret(name: str, secret: str, local_key: bytes):
    encrypted = encrypt_locally(secret, local_key)
    store_secret(name, encrypted)

def retrieve_encrypted_secret(name: str, local_key: bytes) -> str:
    encrypted = retrieve_secret(name)
    return decrypt_locally(encrypted, local_key) if encrypted else None

# ==========================
# Import / Export (Encrypted)
# ==========================

def export_store(local_key: bytes) -> str:
    secrets = {}
    names = _load_index()
    for name in names:
        val = retrieve_secret(name)
        if val:
            secrets[name] = encrypt_locally(val, local_key)
    return json.dumps(secrets, indent=2)

def import_store(blob: str, local_key: bytes):
    secrets = json.loads(blob)
    for name, encrypted in secrets.items():
        decrypted = decrypt_locally(encrypted, local_key)
        store_secret(name, decrypted)

# ==========================
# Migration between services
# ==========================

def migrate_backend(new_service: str):
    raise NotImplementedError("This requires backend listing support.")
