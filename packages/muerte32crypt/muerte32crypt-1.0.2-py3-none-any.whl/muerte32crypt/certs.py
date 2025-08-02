# muerte32crypt/certs.py

from cryptography import x509
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from typing import List, Union, Optional
import datetime


# --- Loading & Saving ---
def load_cert(path: Union[str, bytes]) -> x509.Certificate:
    """Load a PEM or DER certificate from file."""
    with open(path, "rb") as f:
        data = f.read()
    try:
        return x509.load_pem_x509_certificate(data, default_backend())
    except ValueError:
        return x509.load_der_x509_certificate(data, default_backend())

def save_cert(cert: x509.Certificate, path: str, encoding: str = "PEM"):
    """Save a certificate to a file."""
    with open(path, "wb") as f:
        if encoding.upper() == "PEM":
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        elif encoding.upper() == "DER":
            f.write(cert.public_bytes(serialization.Encoding.DER))
        else:
            raise ValueError("Unsupported encoding: use PEM or DER")


# --- Fingerprints & Info ---
def get_cert_fingerprint(cert: x509.Certificate, hash_algo: str = "sha256") -> str:
    algo = {
        "sha256": hashes.SHA256(),
        "sha1": hashes.SHA1(),
        "md5": hashes.MD5(),
    }.get(hash_algo.lower())
    if not algo:
        raise ValueError("Unsupported hash algorithm")
    return cert.fingerprint(algo).hex()

def get_cert_subject(cert: x509.Certificate) -> str:
    return cert.subject.rfc4514_string()

def get_cert_issuer(cert: x509.Certificate) -> str:
    return cert.issuer.rfc4514_string()

def get_cert_sans(cert: x509.Certificate) -> List[str]:
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        return ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return []


# --- Chain Verification ---
def verify_cert_chain(cert: x509.Certificate, chain: List[x509.Certificate]) -> bool:
    issuer = cert.issuer
    for ca_cert in chain:
        if ca_cert.subject == issuer:
            try:
                ca_cert.public_key().verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    cert.signature_hash_algorithm,
                )
                return True
            except Exception:
                continue
    return False

# --- Self-Signed Cert Generation ---
def generate_self_signed_cert(
    common_name: str,
    private_key: Optional[rsa.RSAPrivateKey] = None,
    days_valid: int = 365,
    key_size: int = 2048,
) -> Tuple[x509.Certificate, rsa.RSAPrivateKey]:
    if private_key is None:
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size, backend=default_backend()
        )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=days_valid))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(private_key, hashes.SHA256(), default_backend())
    )

    return cert, private_key


# --- CSR Generation ---
def generate_csr(private_key, common_name: str, san_list: List[str] = []) -> x509.CertificateSigningRequest:
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    builder = x509.CertificateSigningRequestBuilder().subject_name(name)

    if san_list:
        san = x509.SubjectAlternativeName([x509.DNSName(name) for name in san_list])
        builder = builder.add_extension(san, critical=False)

    csr = builder.sign(private_key, hashes.SHA256(), default_backend())
    return csr

def save_csr(csr: x509.CertificateSigningRequest, path: str):
    with open(path, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))


# --- Public Utilities ---
def load_csr(path: Union[str, bytes]) -> x509.CertificateSigningRequest:
    with open(path, "rb") as f:
        data = f.read()
    return x509.load_pem_x509_csr(data, default_backend())
