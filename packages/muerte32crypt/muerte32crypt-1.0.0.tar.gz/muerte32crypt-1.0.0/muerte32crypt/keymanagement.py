import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import algorithms

class KeyManager:
    def __init__(self):
        self.symmetric_keys = {}  # name: bytes
        self.asymmetric_keys = {}  # name: (private_key, public_key)

    def generate_key(self, name: str, length: int = 32):
      key = self.generate_symmetric_key(name, length)
      return name, key
    
    def get_key(self, name: str):
      return self.get_symmetric_key(name)
    
    def delete_key(self, name: str):
      if name in self.symmetric_keys:
        self.symmetric_keys.pop(name)
      elif name in self.asymmetric_keys:
        self.asymmetric_keys.pop(name)

    def derive_key_from_password(self, name: str, password: str, salt: bytes = None, iterations: int = 100_000, length: int = 32) -> bytes:
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        self.symmetric_keys[name] = key
        return key
    
    def get_derived_key(self, name: str) -> bytes:
        return self.symmetric_keys.get(name)

    def generate_salt(self, length: int = 16) -> bytes:
        return os.urandom(length)
    
    # Symmetric key generation
    def generate_symmetric_key(self, name: str, length: int = 32):
        key = os.urandom(length)
        self.symmetric_keys[name] = key
        return key

    # Get symmetric key
    def get_symmetric_key(self, name: str) -> bytes:
        return self.symmetric_keys.get(name)

    # Rotate symmetric key (overwrite)
    def rotate_symmetric_key(self, name: str, length: int = 32):
        return self.generate_symmetric_key(name, length)

    # RSA keypair generation
    def generate_rsa_keypair(self, name: str, key_size: int = 2048):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        self.asymmetric_keys[name] = (private_key, public_key)
        return private_key, public_key

    # Get RSA keys
    def get_rsa_keypair(self, name: str):
        return self.asymmetric_keys.get(name)

    # Export RSA private key PEM (optionally encrypted with passphrase)
    def export_private_key_pem(self, name: str, passphrase: bytes = None) -> bytes:
        private_key, _ = self.asymmetric_keys.get(name, (None, None))
        if private_key is None:
            raise ValueError(f"No RSA keypair named {name}")

        encryption_algo = (
            serialization.BestAvailableEncryption(passphrase) if passphrase else serialization.NoEncryption()
        )
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algo
        )

    # Export RSA public key PEM
    def export_public_key_pem(self, name: str) -> bytes:
        _, public_key = self.asymmetric_keys.get(name, (None, None))
        if public_key is None:
            raise ValueError(f"No RSA keypair named {name}")
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    # Import RSA private key PEM
    def import_private_key_pem(self, name: str, pem_data: bytes, passphrase: bytes = None):
        private_key = serialization.load_pem_private_key(
            pem_data,
            password=passphrase,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        self.asymmetric_keys[name] = (private_key, public_key)

    # Delete keys
    def delete_symmetric_key(self, name: str):
        self.symmetric_keys.pop(name, None)

    def delete_rsa_keypair(self, name: str):
        self.asymmetric_keys.pop(name, None)
