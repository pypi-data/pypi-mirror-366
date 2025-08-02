import hashlib
import hmac
import os
import base64
from cryptography.hazmat.primitives import keywrap, hashes, serialization
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.keywrap import InvalidUnwrap
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from twofish import Twofish
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import padding
from Crypto.Util.Padding import pad, unpad
from cryptography.exceptions import InvalidSignature

# --- Hashing, HMAC & HKDF---

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()

def hmac_sha256(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()

def hmac_sha512(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha512).digest()

def hkdf_sha256(input_key_material: bytes, length: int = 32, salt: bytes = None, info: bytes = b'') -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        info=info,
        backend=default_backend()
    )
    return hkdf.derive(input_key_material)

# --- Random & Base64 ---

def generate_random_bytes(length: int) -> bytes:
    return os.urandom(length)

def base64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")

def base64_decode(encoded: str) -> bytes:
    return base64.b64decode(encoded.encode("utf-8"))

# --- PBKDF2 ---

def pbkdf2_sha256(password: str, salt: bytes, iterations: int = 100_000, dklen: int = 32) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=dklen,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password.encode("utf-8"))

def pbkdf2_sha512(password: str, salt: bytes, iterations: int = 100_000, dklen: int = 64) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=dklen,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password.encode("utf-8"))

def secure_compare(a: bytes, b: bytes) -> bool:
    return hmac.compare_digest(a, b)

# --- AES Key Wrap/Unwrap ---

def aes_key_wrap(wrapping_key: bytes, key_to_wrap: bytes) -> bytes:
    if len(key_to_wrap) % 8 != 0:
        raise ValueError("Key to wrap must be a multiple of 8 bytes in length.")
    return keywrap.aes_key_wrap(wrapping_key, key_to_wrap, backend=default_backend())

def aes_key_unwrap(wrapping_key: bytes, wrapped_key: bytes) -> bytes:
    try:
        return keywrap.aes_key_unwrap(wrapping_key, wrapped_key, backend=default_backend())
    except InvalidUnwrap as e:
        raise ValueError("Invalid wrapped key or incorrect wrapping key.") from e

# --- Symmetric AES-GCM Encryption/Decryption ---

def aes_gcm_encrypt(key: bytes, plaintext: bytes, associated_data: bytes = None) -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 128, 192, or 256 bits (16, 24, or 32 bytes).")

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce recommended for GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce + ciphertext

def aes_gcm_decrypt(key: bytes, encrypted: bytes, associated_data: bytes = None) -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 128, 192, or 256 bits (16, 24, or 32 bytes).")

    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data)

def aes_gcm_encrypt_with_nonce(key: bytes, nonce: bytes, plaintext: bytes, associated_data: bytes = None) -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 128, 192, or 256 bits.")
    if len(nonce) != 12:
        raise ValueError("Nonce must be exactly 12 bytes for AES-GCM.")
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return ciphertext

def aes_gcm_decrypt_with_nonce(key: bytes, nonce: bytes, ciphertext: bytes, associated_data: bytes = None) -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 128, 192, or 256 bits.")
    if len(nonce) != 12:
        raise ValueError("Nonce must be exactly 12 bytes for AES-GCM.")
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data)


def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 128, 192, or 256 bits.")
    if len(iv) != 16:
        raise ValueError("IV must be 16 bytes for AES-CBC.")
    
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return iv + ciphertext  # Prepend IV so decryptor can extract it

def aes_cbc_decrypt(key: bytes, ciphertext: bytes) -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 128, 192, or 256 bits.")
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext

# --- Twofish ---

def twofish_encrypt_raw(key: bytes, plaintext: bytes) -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("Key must be 128, 192, or 256 bits.")
    cipher = Twofish(key)
    padded = pad(plaintext, 16)
    return b''.join(cipher.encrypt(padded[i:i+16]) for i in range(0, len(padded), 16))

def twofish_decrypt_raw(key: bytes, ciphertext: bytes) -> bytes:
    cipher = Twofish(key)
    decrypted = b''.join(cipher.decrypt(ciphertext[i:i+16]) for i in range(0, len(ciphertext), 16))
    return unpad(decrypted, 16)

# --- Asymmetric RSA Key Generation, Encrypt/Decrypt, Sign/Verify ---

def generate_rsa_keypair(key_size: int = 2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def rsa_encrypt(public_key, message: bytes) -> bytes:
    return public_key.encrypt(
        message,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def rsa_decrypt(private_key, ciphertext: bytes) -> bytes:
    return private_key.decrypt(
        ciphertext,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def rsa_sign(private_key, data: bytes) -> bytes:
    return private_key.sign(
        data,
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def rsa_verify(public_key, signature: bytes, data: bytes) -> bool:
    try:
        public_key.verify(
            signature,
            data,
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

# --- RSA Key Serialization ---

def serialize_private_key(private_key, password: bytes = None) -> bytes:
    encryption_algo = (serialization.BestAvailableEncryption(password)
                       if password else serialization.NoEncryption())
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algo
    )

def serialize_public_key(public_key) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def load_private_key(pem_data: bytes, password: bytes = None):
    return serialization.load_pem_private_key(pem_data, password=password, backend=default_backend())

def load_public_key(pem_data: bytes):
    return serialization.load_pem_public_key(pem_data, backend=default_backend())

def get_public_key_fingerprint(public_key) -> str:
    pem = serialize_public_key(public_key)
    digest = sha256(pem)
    return base64_encode(digest)
