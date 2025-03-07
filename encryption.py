import base64
import random
import string
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.asymmetric import rsa, padding

def public_encrypt(data, public_key_base64):
    """Encrypt data using a public RSA key."""
    public_key = serialization.load_pem_public_key(
        base64.b64decode(public_key_base64),
        backend=default_backend()
    )
    encrypted = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode()

def generate_nonce():
    """Generate a random nonce."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def encrypt(data, key):
    """Encrypt data with AES-128-CBC."""
    key_bytes = key.encode()
    iv = key_bytes[:16]
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
    padder = PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted_data).decode()

def decrypt(data, key):
    """Decrypt data with AES-128-CBC."""
    key_bytes = key.encode()
    iv = key_bytes[:16]
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(base64.b64decode(data)) + decryptor.finalize()
    unpadder = PKCS7(128).unpadder()
    return (unpadder.update(decrypted_data) + unpadder.finalize()).decode()
