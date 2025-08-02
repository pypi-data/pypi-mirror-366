import os  # For generating nonce
from base64 import b64decode, b64encode
from os import environ

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from castlecraft_engineer.common.env import ENV_SECRETS_ENCRYPTION_KEY


class InvalidEncryptionKey(Exception):
    pass


class InvalidEncryptionFormat(ValueError):
    """Custom exception for invalid encryption format."""

    def __init__(
        self, message: str = "Invalid encrypted data format", error: str | None = None
    ):
        super().__init__(message)
        self.error = error or message

    def __str__(self) -> str:
        return str(self.error)


def get_secret_enc_key():
    key = environ.get(ENV_SECRETS_ENCRYPTION_KEY)
    if not key:
        raise InvalidEncryptionKey(f"{ENV_SECRETS_ENCRYPTION_KEY} not set")
    return key.encode("utf-8")


def encrypt_data(data: str, key: bytes) -> str:
    """
    Encrypts data using AES-GCM.

    Args:
        data: The string data to encrypt.
        key: The AES encryption key (must be 16, 24, or 32 bytes).

    Returns:
        A base64 encoded string of the nonce prepended to the ciphertext and tag.
    """
    if len(key) not in [16, 24, 32]:
        raise InvalidEncryptionKey("AES key must be 16, 24, or 32 bytes long")

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # AES-GCM standard nonce size is 12 bytes (96 bits)
    data_bytes = data.encode("utf-8")

    # encrypt() returns ciphertext which includes the authentication tag
    ciphertext_and_tag = aesgcm.encrypt(nonce, data_bytes, None)  # No associated data

    # Prepend nonce to ciphertext_and_tag, then base64 encode
    encrypted_payload = nonce + ciphertext_and_tag
    return b64encode(encrypted_payload).decode("utf-8")


def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """
    Decrypts data encrypted with AES-GCM.

    Args:
        encrypted_data: The base64 encoded string containing the nonce and ciphertext.
        key: The AES decryption key (must be 16, 24, or 32 bytes).

    Returns:
        The decrypted string data.
    """
    if len(key) not in [16, 24, 32]:
        raise InvalidEncryptionKey("AES key must be 16, 24, or 32 bytes long")

    try:
        encrypted_payload_bytes = b64decode(
            encrypted_data.encode("utf-8"), validate=True
        )
    except Exception as e:  # Catches binascii.Error from b64decode
        raise InvalidEncryptionFormat(f"Invalid base64 encoding: {e}")

    nonce_size = 12  # Must match the nonce size used during encryption
    if len(encrypted_payload_bytes) < nonce_size:
        raise InvalidEncryptionFormat("Encrypted data is too short to contain a nonce.")

    nonce = encrypted_payload_bytes[:nonce_size]
    ciphertext_and_tag = encrypted_payload_bytes[nonce_size:]

    aesgcm = AESGCM(key)
    try:
        plaintext_bytes = aesgcm.decrypt(
            nonce, ciphertext_and_tag, None
        )  # No associated data
        return plaintext_bytes.decode("utf-8")
    except InvalidTag:
        raise InvalidEncryptionFormat(
            "Decryption failed: authentication tag mismatch or data corrupted."
        )
    except Exception as e:  # Catch any other potential errors during decryption
        raise InvalidEncryptionFormat(
            f"Decryption failed due to an unexpected error: {e}"
        )
