"""
Digital Signature Utilities for Test Certificates
"""
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from pathlib import Path
from typing import Tuple, Optional
import hashlib
import base64
import json


class DigitalSignature:
    """Handle digital signatures for test certificates"""

    @staticmethod
    def generate_key_pair(
        key_size: int = 2048,
        private_key_path: Optional[str] = None,
        public_key_path: Optional[str] = None
    ) -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair for signing

        Args:
            key_size: Size of the RSA key (2048 or 4096 recommended)
            private_key_path: Optional path to save private key
            public_key_path: Optional path to save public key

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )

        # Generate public key
        public_key = private_key.public_key()

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Save to files if paths provided
        if private_key_path:
            Path(private_key_path).parent.mkdir(parents=True, exist_ok=True)
            with open(private_key_path, 'wb') as f:
                f.write(private_pem)

        if public_key_path:
            Path(public_key_path).parent.mkdir(parents=True, exist_ok=True)
            with open(public_key_path, 'wb') as f:
                f.write(public_pem)

        return private_pem, public_pem

    @staticmethod
    def sign_data(data: dict, private_key_pem: bytes) -> Tuple[str, str]:
        """
        Sign data using private key

        Args:
            data: Dictionary of data to sign
            private_key_pem: Private key in PEM format

        Returns:
            Tuple of (data_hash, signature_base64)
        """
        # Convert data to JSON string
        data_str = json.dumps(data, sort_keys=True)

        # Create SHA-256 hash of data
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()

        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )

        # Sign the hash
        signature = private_key.sign(
            data_str.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Encode signature to base64 for storage
        signature_base64 = base64.b64encode(signature).decode()

        return data_hash, signature_base64

    @staticmethod
    def verify_signature(
        data: dict,
        signature_base64: str,
        public_key_pem: bytes
    ) -> bool:
        """
        Verify signature of data

        Args:
            data: Dictionary of data to verify
            signature_base64: Base64 encoded signature
            public_key_pem: Public key in PEM format

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Convert data to JSON string
            data_str = json.dumps(data, sort_keys=True)

            # Decode signature
            signature = base64.b64decode(signature_base64)

            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=default_backend()
            )

            # Verify signature
            public_key.verify(
                signature,
                data_str.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True

        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Verification error: {e}")
            return False

    @staticmethod
    def hash_certificate_data(certificate_data: dict) -> str:
        """
        Create hash of certificate data for integrity verification

        Args:
            certificate_data: Certificate data dictionary

        Returns:
            SHA-256 hash of the data
        """
        data_str = json.dumps(certificate_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
