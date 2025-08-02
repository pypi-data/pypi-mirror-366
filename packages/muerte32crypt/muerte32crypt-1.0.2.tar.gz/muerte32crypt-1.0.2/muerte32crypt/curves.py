from cryptography.hazmat.primitives.asymmetric import ec, ed25519, ed448
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# --- Supported Curves ---

NIST_CURVES = [
    ec.SECP192R1(), ec.SECP224R1(), ec.SECP256R1(),
    ec.SECP384R1(), ec.SECP521R1(),
    ec.SECP256K1(),
]

BRAINPOOL_CURVES = [
    ec.BrainpoolP256R1(), ec.BrainpoolP384R1(), ec.BrainpoolP512R1()
]

ALL_EC_CURVES = NIST_CURVES + BRAINPOOL_CURVES

# Note: EdDSA curves do not use the same API
ED_CURVES = ["ed25519", "ed448"]

# --- Key Generation ---

def generate_ec_key(curve: ec.EllipticCurve):
    return ec.generate_private_key(curve, backend=default_backend())

def generate_ed_key(curve: str):
    if curve.lower() == "ed25519":
        return ed25519.Ed25519PrivateKey.generate()
    elif curve.lower() == "ed448":
        return ed448.Ed448PrivateKey.generate()
    else:
        raise ValueError("Unsupported EdDSA curve")

# --- Utility Functions ---

def list_all_curves() -> list:
    return [type(c).__name__ for c in ALL_EC_CURVES] + ED_CURVES

def serialize_private_key(key, password: bytes = None) -> bytes:
    encryption = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )

def serialize_public_key(key) -> bytes:
    return key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def get_curve_name(key) -> str:
    if isinstance(key, ec.EllipticCurvePrivateKey):
        return type(key.curve).__name__
    elif isinstance(key, ed25519.Ed25519PrivateKey):
        return "ed25519"
    elif isinstance(key, ed448.Ed448PrivateKey):
        return "ed448"
    else:
        return "unknown"

