# muerte32crypt

Windows-native DPAPI encryption using `ctypes`.  
Encrypt and decrypt strings, bytes, or files with optional entropy and descriptions.

# Usage
```py
from muerte32crypt.dpapi import encrypt_str, decrypt_str

enc = encrypt_str("my_password", entropy="somesalt")
print(decrypt_str(enc, entropy="somesalt"))
```

## Install

```bash
pip install muerte32crypt
