"""
Digital Signature Service
Handles signature capture, verification, and certificate management
"""
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import json


class SignatureService:
    """Manage digital signatures for form records"""

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or "default-signature-secret-key"

    def create_signature(
        self,
        user_id: int,
        record_id: int,
        role: str,
        signature_data: str,
        user_info: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Create a digital signature

        Args:
            user_id: ID of the signing user
            record_id: ID of the form record
            role: User's role (doer, checker, approver)
            signature_data: Base64 encoded signature image or text
            user_info: Additional user information
            ip_address: IP address of the signer
            user_agent: User agent string

        Returns:
            Signature data with hash and certificate
        """
        timestamp = datetime.utcnow().isoformat()

        # Create signature payload
        payload = {
            'user_id': user_id,
            'record_id': record_id,
            'role': role,
            'timestamp': timestamp,
            'ip_address': ip_address,
            'user_agent': user_agent
        }

        # Generate signature hash
        signature_hash = self._generate_signature_hash(
            signature_data=signature_data,
            payload=payload
        )

        # Create certificate data
        certificate = self._create_certificate(
            user_id=user_id,
            record_id=record_id,
            role=role,
            timestamp=timestamp,
            user_info=user_info,
            signature_hash=signature_hash
        )

        return {
            'signature_data': signature_data,
            'signature_hash': signature_hash,
            'certificate_data': certificate,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'signed_at': timestamp
        }

    def verify_signature(
        self,
        signature_data: str,
        signature_hash: str,
        payload: Dict[str, Any]
    ) -> bool:
        """
        Verify a signature's integrity

        Args:
            signature_data: Original signature data
            signature_hash: Hash to verify against
            payload: Original payload data

        Returns:
            True if signature is valid
        """
        # Regenerate hash from data and payload
        expected_hash = self._generate_signature_hash(signature_data, payload)

        # Compare hashes
        return hmac.compare_digest(expected_hash, signature_hash)

    def _generate_signature_hash(
        self,
        signature_data: str,
        payload: Dict[str, Any]
    ) -> str:
        """Generate secure hash of signature data"""
        # Combine signature data with payload
        payload_str = json.dumps(payload, sort_keys=True)
        combined = f"{signature_data}:{payload_str}:{self.secret_key}"

        # Generate SHA-256 hash
        return hashlib.sha256(combined.encode()).hexdigest()

    def _create_certificate(
        self,
        user_id: int,
        record_id: int,
        role: str,
        timestamp: str,
        user_info: Dict[str, Any] = None,
        signature_hash: str = None
    ) -> Dict[str, Any]:
        """
        Create a digital certificate for the signature

        This is a simplified certificate. In production, use proper PKI/X.509 certificates
        """
        certificate = {
            'version': '1.0',
            'issuer': 'LIMS-QMS Platform',
            'subject': {
                'user_id': user_id,
                'role': role
            },
            'valid_from': timestamp,
            'serial_number': self._generate_serial_number(user_id, record_id, timestamp),
            'signature_algorithm': 'SHA256',
            'public_key_fingerprint': signature_hash[:32] if signature_hash else None,
            'extensions': {
                'record_id': record_id,
                'signing_role': role,
                'user_info': user_info or {}
            }
        }

        # Sign the certificate itself
        cert_hash = self._sign_certificate(certificate)
        certificate['certificate_signature'] = cert_hash

        return certificate

    def _generate_serial_number(
        self,
        user_id: int,
        record_id: int,
        timestamp: str
    ) -> str:
        """Generate unique serial number for certificate"""
        data = f"{user_id}:{record_id}:{timestamp}"
        return hashlib.md5(data.encode()).hexdigest().upper()

    def _sign_certificate(self, certificate: Dict[str, Any]) -> str:
        """Sign the certificate with platform secret"""
        # Remove signature field if present
        cert_copy = {k: v for k, v in certificate.items() if k != 'certificate_signature'}

        # Create canonical JSON representation
        cert_json = json.dumps(cert_copy, sort_keys=True)

        # Sign with HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode(),
            cert_json.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def verify_certificate(self, certificate: Dict[str, Any]) -> bool:
        """Verify certificate integrity"""
        if 'certificate_signature' not in certificate:
            return False

        stored_signature = certificate['certificate_signature']
        expected_signature = self._sign_certificate(certificate)

        return hmac.compare_digest(stored_signature, expected_signature)

    def encode_signature_image(self, image_path: str) -> str:
        """Encode signature image to base64"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to encode signature image: {str(e)}")

    def decode_signature_image(self, base64_data: str) -> bytes:
        """Decode base64 signature to image bytes"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            return base64.b64decode(base64_data)
        except Exception as e:
            raise ValueError(f"Failed to decode signature image: {str(e)}")

    def save_signature_image(
        self,
        base64_data: str,
        output_path: str
    ) -> str:
        """Save signature image to file"""
        try:
            image_bytes = self.decode_signature_image(base64_data)

            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            return output_path
        except Exception as e:
            raise ValueError(f"Failed to save signature image: {str(e)}")

    def create_text_signature(
        self,
        user_name: str,
        role: str,
        timestamp: datetime = None
    ) -> str:
        """
        Create a text-based signature for users without digital signature capability

        Args:
            user_name: Name of the signing user
            role: User's role
            timestamp: Signing timestamp

        Returns:
            Formatted text signature
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        signature_text = f"""
        Electronically Signed By: {user_name}
        Role: {role}
        Date/Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
        """

        return signature_text.strip()

    def generate_signature_token(
        self,
        user_id: int,
        record_id: int,
        role: str,
        validity_hours: int = 24
    ) -> str:
        """
        Generate a one-time signature token for API-based signing

        Args:
            user_id: ID of the user
            record_id: ID of the record
            role: User's role
            validity_hours: Token validity in hours

        Returns:
            Signature token
        """
        timestamp = datetime.utcnow().isoformat()
        expiry = datetime.utcnow().timestamp() + (validity_hours * 3600)

        payload = {
            'user_id': user_id,
            'record_id': record_id,
            'role': role,
            'timestamp': timestamp,
            'expiry': expiry
        }

        # Create token
        payload_json = json.dumps(payload, sort_keys=True)
        token = base64.b64encode(payload_json.encode()).decode()

        # Sign token
        signature = hmac.new(
            self.secret_key.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{token}.{signature}"

    def verify_signature_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode signature token

        Args:
            token: Signature token

        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            # Split token and signature
            token_parts = token.split('.')
            if len(token_parts) != 2:
                return None

            token_data, signature = token_parts

            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                return None

            # Decode payload
            payload_json = base64.b64decode(token_data).decode()
            payload = json.loads(payload_json)

            # Check expiry
            if payload['expiry'] < datetime.utcnow().timestamp():
                return None

            return payload

        except Exception:
            return None

    def generate_qr_signature(
        self,
        signature_hash: str,
        user_id: int,
        record_id: int
    ) -> str:
        """
        Generate QR code data for signature verification

        Args:
            signature_hash: Hash of the signature
            user_id: ID of the user
            record_id: ID of the record

        Returns:
            QR code data string
        """
        qr_data = {
            'type': 'signature_verification',
            'hash': signature_hash,
            'user_id': user_id,
            'record_id': record_id,
            'timestamp': datetime.utcnow().isoformat()
        }

        return json.dumps(qr_data)

    def get_signature_metadata(
        self,
        signature_hash: str,
        certificate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract metadata from signature and certificate

        Returns:
            Metadata dictionary
        """
        return {
            'signature_hash': signature_hash,
            'algorithm': certificate.get('signature_algorithm'),
            'issuer': certificate.get('issuer'),
            'serial_number': certificate.get('serial_number'),
            'valid_from': certificate.get('valid_from'),
            'user_id': certificate.get('subject', {}).get('user_id'),
            'role': certificate.get('subject', {}).get('role'),
            'record_id': certificate.get('extensions', {}).get('record_id'),
            'is_verified': self.verify_certificate(certificate)
        }
