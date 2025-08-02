import os
import sys
import tempfile
from cryptography import x509
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import base64
from muerte32crypt.dpapi import encrypt, decrypt, encrypt_str, decrypt_str, encrypt_file, decrypt_file
from muerte32crypt.tpm import is_tpm_available, generate_tpm_key, seal_data_to_tpm, unseal_data_from_tpm
from muerte32crypt.utils import (
    sha256, sha512, generate_random_bytes,
    hmac_sha256, hmac_sha512,
    aes_key_wrap, aes_key_unwrap,
    aes_gcm_encrypt, aes_gcm_decrypt,
    generate_rsa_keypair, rsa_encrypt, rsa_decrypt,
    rsa_sign, rsa_verify,
    serialize_private_key, serialize_public_key,
    load_private_key, load_public_key,
    get_public_key_fingerprint,
    hkdf_sha256,
    aes_gcm_encrypt_with_nonce,
    aes_gcm_decrypt_with_nonce,
    aes_cbc_encrypt,
    aes_cbc_decrypt,
    twofish_encrypt_raw,
    twofish_decrypt_raw
)
from muerte32crypt.certs import (
    generate_self_signed_cert,
    get_cert_fingerprint,
    get_cert_subject,
    get_cert_issuer,
    save_cert,
    load_cert,
    get_cert_sans,
    generate_csr,
    save_csr,
    load_csr,
    verify_cert_chain,
)
from cryptography.x509 import Certificate, CertificateSigningRequest
from muerte32crypt.keymanagement import KeyManager

def print_header(title):
    print(f"\n{'='*10} {title} {'='*10}")

def test_dpapi():
    print_header("DPAPI")
    data = b"secret-data"
    encrypted = encrypt(data)
    decrypted = decrypt(encrypted)
    assert decrypted == data

    encrypted_str = encrypt_str("hello")
    decrypted_str = decrypt_str(encrypted_str)
    assert decrypted_str == "hello"

    test_path = "test.txt"
    with open(test_path, "wb") as f:
        f.write(b"file-data")
    encrypt_file(test_path, test_path + ".enc")
    decrypt_file(test_path + ".enc", test_path + ".dec")
    with open(test_path, "rb") as f:
        assert f.read() == b"file-data"
    os.remove(test_path)
    os.remove(test_path + ".enc")
    os.remove(test_path + ".dec")

def test_tpm():
    print_header("TPM")
    if not is_tpm_available():
        print("TPM not available; skipping.")
        return
    data = b"tpm-secret"
    sealed = seal_data_to_tpm(data)
    unsealed = unseal_data_from_tpm(sealed)
    assert unsealed == data
    print("TPM seal/unseal OK")

def test_hash_hmac():
    print_header("Hash / HMAC")
    data = b"abc"
    print("SHA256:", sha256(data).hex())
    print("SHA512:", sha512(data).hex())

    key = generate_random_bytes(32)
    print("HMAC-SHA256:", hmac_sha256(key, data).hex())
    print("HMAC-SHA512:", hmac_sha512(key, data).hex())

def test_aes():
    print_header("AES-GCM / Wrap")
    key = generate_random_bytes(32)
    plaintext = b"AES-GCM test data"
    associated_data = b"header"

    encrypted = aes_gcm_encrypt(key, plaintext, associated_data)
    
    # Extract nonce, tag, ciphertext from the combined encrypted bytes
    nonce = encrypted[:12]
    tag = encrypted[-16:]
    ciphertext = encrypted[12:-16]

    decrypted = aes_gcm_decrypt(key, encrypted, associated_data)
    assert decrypted == plaintext
    print("AES-GCM encryption/decryption successful.")

    # AES Key Wrap/Unwrap test
    kek = generate_random_bytes(32)
    wrapped = aes_key_wrap(kek, key)
    unwrapped = aes_key_unwrap(kek, wrapped)
    assert unwrapped == key
    print("AES Key Wrap/Unwrap successful.")

def test_aes_with_nonce():
    print_header("AES-GCM Encrypt/Decrypt with Nonce")
    key = generate_random_bytes(32)
    nonce = generate_random_bytes(12)
    plaintext = b"Test AES-GCM with nonce"
    aad = b"aad-header"

    ciphertext = aes_gcm_encrypt_with_nonce(key, nonce, plaintext, aad)
    decrypted = aes_gcm_decrypt_with_nonce(key, nonce, ciphertext, aad)
    assert decrypted == plaintext
    print("AES-GCM with nonce encrypt/decrypt OK")

def test_aes_cbc():
    print_header("AES-CBC Encrypt/Decrypt")
    key = generate_random_bytes(32)
    iv = generate_random_bytes(16)
    plaintext = b"This is a test message."
    print(f"Plaintext: {plaintext}")

    ciphertext = aes_cbc_encrypt(key, iv, plaintext)
    decrypted = aes_cbc_decrypt(key, ciphertext)
    assert decrypted == plaintext
    print(f"Decrypted: {decrypted}")
    print("AES-CBC encrypt/decrypt OK")

def test_rsa():
    print_header("RSA")
    priv, pub = generate_rsa_keypair()
    msg = b"verify me"

    enc = rsa_encrypt(pub, msg)
    dec = rsa_decrypt(priv, enc)
    assert dec == msg

    sig = rsa_sign(priv, msg)
    assert rsa_verify(pub, sig, msg)

    priv_bytes = serialize_private_key(priv)
    pub_bytes = serialize_public_key(pub)

    priv2 = load_private_key(priv_bytes)
    pub2 = load_public_key(pub_bytes)
    assert rsa_verify(pub2, rsa_sign(priv2, msg), msg)

    # Test public key fingerprint
    fingerprint = get_public_key_fingerprint(pub)
    assert isinstance(fingerprint, str) and len(fingerprint) > 0
    print("RSA tests OK")

def test_keymanager():
    print_header("KeyManager")
    km = KeyManager()
    key_id, key = km.generate_key("mykey", 32)
    assert km.get_key("mykey") == key
    km.delete_key("mykey")
    assert km.get_key("mykey") is None
    print("KeyManager tests OK")

def test_hkdf():
    print("\n========== HKDF-SHA256 ==========")
    salt = os.urandom(16)
    ikm = b"input key material"
    info = b"context info"
    length = 32  # length must be int
    derived_key = hkdf_sha256(
        input_key_material=ikm,
        length=length,
        salt=salt,
        info=info
    )
    assert isinstance(derived_key, bytes) and len(derived_key) == length
    print("HKDF-SHA256 OK")

def test_twofish():
    print_header("Twofish (Raw ECB-like)")

    from muerte32crypt.utils import twofish_encrypt_raw, twofish_decrypt_raw

    key = generate_random_bytes(32)
    plaintext = b"This is some test data."

    ciphertext = twofish_encrypt_raw(key, plaintext)
    decrypted = twofish_decrypt_raw(key, ciphertext)
    assert decrypted == plaintext
    print("Twofish ECB-like encryption/decryption OK")


def test_compression_encryption():
    print_header("Compression + Encryption")

    from muerte32crypt.compression import compress_then_encrypt, decrypt_then_decompress
    from muerte32crypt.utils import generate_random_bytes

    key = generate_random_bytes(32)
    hmac_key = generate_random_bytes(32)
    data = b"this is a bunch of repetitive data! " * 100

    compression_methods = ["zlib", "gzip", "bz2", "lzma"]
    encryption_methods = ["aes_gcm", "aes_cbc", "twofish"]

    for comp in compression_methods:
        for enc in encryption_methods:
            print(f"Testing: {comp} + {enc}")
            blob = compress_then_encrypt(
                data, key,
                compression=comp,
                encryption=enc,
                hmac_key=hmac_key,
                hmac_algo="sha256"
            )
            result = decrypt_then_decompress(blob, key, hmac_key=hmac_key)
            assert result == data, f"Mismatch with {comp} + {enc}"
    
    print("All compression+encryption combinations passed ✅")

def test_cert_functions():
    print_header("Certificate Utilities")

    common_name = "test.local"
    san_list = ["test.local", "www.test.local"]
    
    # Generate cert and key
    cert, key = generate_self_signed_cert(common_name)
    assert isinstance(cert, Certificate)

    # --- Fingerprint, Subject, Issuer ---
    fp = get_cert_fingerprint(cert)
    assert len(fp) == 64  # SHA-256 is 32 bytes = 64 hex chars

    subject = get_cert_subject(cert)
    issuer = get_cert_issuer(cert)
    assert common_name in subject
    assert subject == issuer  # self-signed

    # --- Save & Load ---
    with tempfile.TemporaryDirectory() as tmpdir:
        cert_path = os.path.join(tmpdir, "cert.pem")
        save_cert(cert, cert_path)
        loaded = load_cert(cert_path)
        assert loaded.serial_number == cert.serial_number

    # --- SANs ---
    csr = generate_csr(key, common_name, san_list)
    assert isinstance(csr, CertificateSigningRequest)

    csr_path = os.path.join(tempfile.gettempdir(), "test_csr.pem")
    save_csr(csr, csr_path)
    loaded_csr = load_csr(csr_path)
    assert loaded_csr.subject.get_attributes_for_oid(
        x509.NameOID.COMMON_NAME
    )[0].value == common_name

    # We generated a cert without SANs, so this should be empty
    assert get_cert_sans(cert) == []

    # --- Chain Verification (trivial self-signed chain) ---
    assert verify_cert_chain(cert, [cert]) == True

    print("Certificate tests OK")


def run_all():
    test_dpapi()
    test_tpm()
    test_hash_hmac()
    test_aes()
    test_aes_with_nonce()
    test_compression_encryption()
    test_cert_functions()
    test_aes_cbc()
    test_twofish()
    test_rsa()
    test_keymanager()
    test_hkdf()
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    run_all()
