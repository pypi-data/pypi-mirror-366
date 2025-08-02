from .dpapi import encrypt, decrypt, encrypt_str, decrypt_str, encrypt_file, decrypt_file
from .tpm import is_tpm_available, generate_tpm_key, seal_data_to_tpm, unseal_data_from_tpm
from .certs import (
    load_cert, save_cert, get_cert_fingerprint, get_cert_subject,
    get_cert_issuer, get_cert_sans, verify_cert_chain,
    generate_self_signed_cert, generate_csr, save_csr, load_csr,
)
from .securestorage import (
    is_secure_store_available,
    get_backend_name,
    store_secret,
    retrieve_secret,
    delete_secret,
    secret_exists,
    secure_prompt_store,
    encrypt_locally,
    decrypt_locally,
    store_encrypted_secret,
    retrieve_encrypted_secret,
    generate_local_key,
    export_store,
    import_store,
    get_all_service_items,
    clear_all_secrets,
)
from .utils import (
    sha256, sha512, generate_random_bytes,
    hmac_sha256, hmac_sha512,
    aes_key_wrap, aes_key_unwrap,
    aes_gcm_encrypt, aes_gcm_decrypt,
    generate_rsa_keypair, rsa_encrypt, rsa_decrypt,
    rsa_sign, rsa_verify,
    serialize_private_key, serialize_public_key,
    load_private_key, load_public_key, get_public_key_fingerprint, 
    hkdf_sha256, aes_gcm_decrypt_with_nonce, aes_gcm_encrypt_with_nonce,
    aes_cbc_encrypt, aes_cbc_decrypt,
    twofish_encrypt_raw, twofish_decrypt_raw
)
from .curves import (
    generate_ec_key, generate_ed_key,
    list_all_curves, serialize_private_key, get_curve_name
)

from .compression import decrypt_then_decompress, compress_then_encrypt, decrypt, encrypt, decompress, compress

from .keymanagement import KeyManager

__all__ = [
    "encrypt", "decrypt", "encrypt_str", "decrypt_str",
    "encrypt_file", "decrypt_file",
    "is_tpm_available", "generate_tpm_key",
    "seal_data_to_tpm", "unseal_data_from_tpm",
    "sha256", "sha512", "generate_random_bytes",
    "hmac_sha256", "hmac_sha512",
    "aes_key_wrap", "aes_key_unwrap",
    "aes_gcm_encrypt", "aes_gcm_decrypt",
    "generate_rsa_keypair", "rsa_encrypt", "rsa_decrypt",
    "rsa_sign", "rsa_verify",
    "serialize_private_key", "serialize_public_key",
    "load_private_key", "load_public_key",
    "KeyManager", "get_public_key_fingerprint", "hkdf_sha256",
    "aes_gcm_decrypt_with_nonce", "aes_gcm_encrypt_with_nonce",
    "aes_cbc_encrypt", "aes_cbc_decrypt",
    "twofish_encrypt_raw", "twofish_decrypt_raw",
    "load_cert", "save_cert", "get_cert_fingerprint", "get_cert_subject",
    "get_cert_issuer", "get_cert_sans", "verify_cert_chain",
    "generate_self_signed_cert", "generate_csr", "save_csr", "load_csr",
    "generate_ec_key", "generate_ed_key", "list_all_curves", "get_curve_name",
    "decrypt_then_decompress", "compress_then_encrypt", "decompress", "compress",
    "is_secure_store_available", "get_backend_name", "store_secret",
    "retrieve_secret", "delete_secret", "secret_exists", "secure_prompt_store",
    "encrypt_locally", "decrypt_locally", "store_encrypted_secret",
    "retrieve_encrypted_secret", "generate_local_key", "export_store",
    "import_store", "get_all_service_items", "clear_all_secrets",
]
