import ctypes
from ctypes import wintypes

# DLLs
ncrypt = ctypes.WinDLL("ncrypt.dll")
kernel32 = ctypes.WinDLL("kernel32.dll")

# Constants
NTE_BAD_KEYSET = 0x80090016
MS_PLATFORM_CRYPTO_PROVIDER = "Microsoft Platform Crypto Provider"
PROTECTION_DESCRIPTOR_FLAGS = 0
CRYPTPROTECT_UI_FORBIDDEN = 0x01

# Error helper
def get_last_error_message(code):
    buffer = ctypes.create_unicode_buffer(512)
    kernel32.FormatMessageW(
        0x00001000,  # FORMAT_MESSAGE_FROM_SYSTEM
        None,
        code,
        0,
        buffer,
        len(buffer),
        None
    )
    return buffer.value.strip()

# Handle class
class SafeHandle:
    def __init__(self, handle=None):
        self.handle = handle or wintypes.HANDLE()

    def __enter__(self):
        return self.handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.handle:
            ncrypt.NCryptFreeObject(self.handle)
            self.handle = None

# TPM Availability Check
def is_tpm_available() -> bool:
    handle = wintypes.HANDLE()
    status = ncrypt.NCryptOpenStorageProvider(
        ctypes.byref(handle),
        ctypes.c_wchar_p(MS_PLATFORM_CRYPTO_PROVIDER),
        0
    )
    if status == 0:
        ncrypt.NCryptFreeObject(handle)
        return True
    return False

# Sealing
def seal_data_to_tpm(data: bytes, descriptor: str = "LOCAL=user") -> bytes:
    hProv = wintypes.HANDLE()
    if ncrypt.NCryptOpenStorageProvider(ctypes.byref(hProv), MS_PLATFORM_CRYPTO_PROVIDER, 0) != 0:
        raise RuntimeError("Could not open TPM crypto provider")

    # Create protection descriptor
    hDesc = wintypes.HANDLE()
    if ncrypt.NCryptCreateProtectionDescriptor(ctypes.byref(hDesc), descriptor, PROTECTION_DESCRIPTOR_FLAGS) != 0:
        raise RuntimeError("Failed to create protection descriptor")

    pb_out = ctypes.c_void_p()
    cb_out = wintypes.DWORD()

    buffer = ctypes.create_string_buffer(data)
    res = ncrypt.NCryptProtectSecret(
        hProv, hDesc,
        None,
        buffer, len(data),
        None, 0,
        ctypes.byref(pb_out), ctypes.byref(cb_out)
    )
    if res != 0:
        raise RuntimeError(f"NCryptProtectSecret failed: {get_last_error_message(res)}")

    out = ctypes.string_at(pb_out, cb_out.value)
    kernel32.LocalFree(pb_out)

    # Free handles
    ncrypt.NCryptFreeObject(hDesc)
    ncrypt.NCryptFreeObject(hProv)

    return out

# Unsealing
def unseal_data_from_tpm(sealed: bytes) -> bytes:
    """
    Unseal previously sealed TPM data using DPAPI-NG.
    """
    hProv = wintypes.HANDLE()
    if ncrypt.NCryptOpenStorageProvider(ctypes.byref(hProv), MS_PLATFORM_CRYPTO_PROVIDER, 0) != 0:
        raise RuntimeError("Could not open TPM crypto provider")

    pb_out = ctypes.c_void_p()
    cb_out = wintypes.DWORD()

    buffer = ctypes.create_string_buffer(sealed)
    res = ncrypt.NCryptUnprotectSecret(
        hProv, None,
        None,
        buffer, len(sealed),
        None, 0,
        ctypes.byref(pb_out), ctypes.byref(cb_out)
    )
    if res != 0:
        raise RuntimeError(f"NCryptUnprotectSecret failed: {get_last_error_message(res)}")

    data = ctypes.string_at(pb_out, cb_out.value)
    kernel32.LocalFree(pb_out)
    ncrypt.NCryptFreeObject(hProv)

    return data

def generate_tpm_key(key_name: str = "MyTPMKey", key_length: int = 2048, overwrite: bool = False) -> None:
    """
    Generates a TPM-protected RSA key pair and stores it persistently.
    """
    NCRYPT_OVERWRITE_KEY_FLAG = 0x00000080
    NCRYPT_PAD_PKCS1_FLAG = 0x00000002
    NCRYPT_MACHINE_KEY_FLAG = 0x00000020

    flags = NCRYPT_OVERWRITE_KEY_FLAG if overwrite else 0

    h_provider = wintypes.HANDLE()
    h_key = wintypes.HANDLE()

    # Open the Platform Crypto Provider
    status = ncrypt.NCryptOpenStorageProvider(
        ctypes.byref(h_provider),
        MS_PLATFORM_CRYPTO_PROVIDER,
        0
    )
    if status != 0:
        raise RuntimeError(f"Failed to open Platform Crypto Provider: {get_last_error_message(status)}")

    # Create a new persisted RSA key
    status = ncrypt.NCryptCreatePersistedKey(
        h_provider,
        ctypes.byref(h_key),
        b"RSA",  # Key algorithm
        ctypes.c_wchar_p(key_name),
        0,  # Legacy: AT_KEYEXCHANGE
        flags
    )
    if status != 0:
        raise RuntimeError(f"Failed to create persisted TPM key: {get_last_error_message(status)}")

    # Set key length
    key_length_bytes = ctypes.c_ulong(key_length)
    status = ncrypt.NCryptSetProperty(
        h_key,
        b"Length",
        ctypes.byref(key_length_bytes),
        ctypes.sizeof(key_length_bytes),
        0
    )
    if status != 0:
        raise RuntimeError(f"Failed to set key length: {get_last_error_message(status)}")

    # Finalize key creation
    status = ncrypt.NCryptFinalizeKey(h_key, 0)
    if status != 0:
        raise RuntimeError(f"Failed to finalize TPM key: {get_last_error_message(status)}")

    # Free handles
    ncrypt.NCryptFreeObject(h_key)
    ncrypt.NCryptFreeObject(h_provider)