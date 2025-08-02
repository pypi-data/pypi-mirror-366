import os
import struct
import json
import zlib
import gzip
import bz2
import lzma
from typing import Literal, Optional, Tuple

from muerte32crypt.utils import (
    aes_gcm_encrypt_with_nonce, aes_gcm_decrypt_with_nonce,
    aes_cbc_encrypt, aes_cbc_decrypt,
    twofish_encrypt_raw, twofish_decrypt_raw,
    hmac_sha256, hmac_sha512
)

CompressionMethod = Literal["zlib", "gzip", "bz2", "lzma"]
EncryptionMethod = Literal["aes_gcm", "aes_cbc", "twofish"]
HMACAlgorithm = Literal["sha256", "sha512"]

# --- Compression ---

def compress(data: bytes, method: CompressionMethod, level: int = 9) -> bytes:
    if method == "zlib":
        return zlib.compress(data, level)
    elif method == "gzip":
        return gzip.compress(data, compresslevel=level)
    elif method == "bz2":
        return bz2.compress(data, compresslevel=level)
    elif method == "lzma":
        return lzma.compress(data, preset=level)
    raise ValueError(f"Unsupported compression method: {method}")

def decompress(data: bytes, method: CompressionMethod) -> bytes:
    if method == "zlib":
        return zlib.decompress(data)
    elif method == "gzip":
        return gzip.decompress(data)
    elif method == "bz2":
        return bz2.decompress(data)
    elif method == "lzma":
        return lzma.decompress(data)
    raise ValueError(f"Unsupported compression method: {method}")

# --- Encryption ---

def encrypt(data: bytes, key: bytes, method: EncryptionMethod) -> Tuple[bytes, bytes]:
    if method == "aes_gcm":
        nonce = os.urandom(12)
        ciphertext = aes_gcm_encrypt_with_nonce(key, nonce, data)
        return ciphertext, nonce

    elif method == "aes_cbc":
        iv = os.urandom(16)
        ciphertext = aes_cbc_encrypt(key, iv, data)
        return ciphertext, iv

    elif method == "twofish":
        ciphertext = twofish_encrypt_raw(key, data)
        return ciphertext, b""  # No IV/nonce

    else:
        raise ValueError(f"Unsupported encryption method: {method}")

def decrypt(encrypted: bytes, key: bytes, method: EncryptionMethod, nonce: bytes) -> bytes:
    if method == "aes_gcm":
        return aes_gcm_decrypt_with_nonce(key, nonce, encrypted)
    elif method == "aes_cbc":
        return aes_cbc_decrypt(key, encrypted)
    elif method == "twofish":
        return twofish_decrypt_raw(key, encrypted)
    else:
        raise ValueError(f"Unsupported encryption method: {method}")

# --- Main Interface ---

def compress_then_encrypt(
    data: bytes,
    key: bytes,
    compression: CompressionMethod = "zlib",
    encryption: EncryptionMethod = "aes_gcm",
    compression_level: int = 9,
    hmac_key: Optional[bytes] = None,
    hmac_algo: HMACAlgorithm = "sha256"
) -> bytes:
    compressed = compress(data, compression, level=compression_level)
    encrypted, nonce = encrypt(compressed, key, encryption)

    payload = {
        "compression": compression,
        "encryption": encryption,
        "nonce": nonce.hex()
    }
    payload_bytes = json.dumps(payload).encode()
    result = struct.pack("!I", len(payload_bytes)) + payload_bytes + encrypted

    if hmac_key:
        tag = hmac_sha512(hmac_key, result) if hmac_algo == "sha512" else hmac_sha256(hmac_key, result)
        return result + tag

    return result

def decrypt_then_decompress(
    blob: bytes,
    key: bytes,
    hmac_key: Optional[bytes] = None,
    hmac_algo: HMACAlgorithm = "sha256"
) -> bytes:
    if hmac_key:
        tag_len = 64 if hmac_algo == "sha512" else 32
        data, tag = blob[:-tag_len], blob[-tag_len:]
        expected = hmac_sha512(hmac_key, data) if hmac_algo == "sha512" else hmac_sha256(hmac_key, data)
        if tag != expected:
            raise ValueError("HMAC verification failed.")
    else:
        data = blob

    meta_len = struct.unpack("!I", data[:4])[0]
    meta = json.loads(data[4:4+meta_len])
    encrypted = data[4+meta_len:]

    nonce = bytes.fromhex(meta["nonce"])
    decrypted = decrypt(encrypted, key, meta["encryption"], nonce)
    return decompress(decrypted, meta["compression"])
