import ctypes
from ctypes import wintypes
import base64

crypt32 = ctypes.WinDLL('crypt32.dll')
kernel32 = ctypes.WinDLL("kernel32.dll")  # <-- add this

kernel32.LocalFree.argtypes = [ctypes.c_void_p]
kernel32.LocalFree.restype = ctypes.c_void_p

class DATA_BLOB(ctypes.Structure):
    _fields_ = [('cbData', wintypes.DWORD),
                ('pbData', ctypes.POINTER(ctypes.c_byte))]

def _to_data_blob(data: bytes) -> DATA_BLOB:
    blob = DATA_BLOB()
    blob.cbData = len(data)
    blob.pbData = ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte))
    return blob

def _from_data_blob(blob: DATA_BLOB) -> bytes:
    buffer = ctypes.cast(blob.pbData, ctypes.POINTER(ctypes.c_byte * blob.cbData))
    return bytes(buffer.contents)

def encrypt(data: bytes, entropy: bytes = None, description: str = None) -> bytes:
    in_blob = _to_data_blob(data)
    out_blob = DATA_BLOB()

    p_entropy = ctypes.byref(_to_data_blob(entropy)) if entropy else None
    desc_ptr = ctypes.c_wchar_p(description) if description else None

    res = crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        desc_ptr,
        p_entropy,
        None, None,
        0x01,
        ctypes.byref(out_blob)
    )
    if not res:
        raise ctypes.WinError()

    encrypted = _from_data_blob(out_blob)
    kernel32.LocalFree(out_blob.pbData)
    return encrypted

def decrypt(encrypted_data: bytes, entropy: bytes = None) -> bytes:
    in_blob = _to_data_blob(encrypted_data)
    out_blob = DATA_BLOB()

    p_entropy = ctypes.byref(_to_data_blob(entropy)) if entropy else None

    res = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        p_entropy,
        None, None,
        0x01,
        ctypes.byref(out_blob)
    )
    if not res:
        raise ctypes.WinError()

    decrypted = _from_data_blob(out_blob)
    kernel32.LocalFree(out_blob.pbData)
    return decrypted

def encrypt_str(text: str, entropy: str = None, description: str = None) -> str:
    encrypted = encrypt(text.encode(), entropy.encode() if entropy else None, description)
    return base64.b64encode(encrypted).decode()

def decrypt_str(b64text: str, entropy: str = None) -> str:
    decrypted = decrypt(base64.b64decode(b64text), entropy.encode() if entropy else None)
    return decrypted.decode()

def encrypt_file(input_path: str, output_path: str, entropy: bytes = None, description: str = None):
    with open(input_path, "rb") as f:
        data = f.read()
    encrypted = encrypt(data, entropy, description)
    with open(output_path, "wb") as f:
        f.write(encrypted)

def decrypt_file(input_path: str, output_path: str, entropy: bytes = None):
    with open(input_path, "rb") as f:
        data = f.read()
    decrypted = decrypt(data, entropy)
    with open(output_path, "wb") as f:
        f.write(decrypted)
