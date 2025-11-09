"""
Digital Signature Service - Handle digital signatures for approvals
"""
from typing import Dict, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import DigitalSignature, FormRecord, User
import hashlib
import base64


class SignatureService:
    """Service for managing digital signatures"""

    def __init__(self, db: Session):
        self.db = db

    def capture_signature(
        self,
        record_id: int,
        user_id: int,
        signature_type: str,  # 'doer', 'checker', 'approver'
        signature_data: str,  # Base64 encoded image or hash
        signature_method: str = 'drawn',  # 'drawn', 'typed', 'uploaded', 'certificate'
        ip_address: Optional[str] = None,
        device_info: Optional[Dict] = None,
        certificate_info: Optional[Dict] = None
    ) -> DigitalSignature:
        """Capture digital signature"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            raise ValueError("Record not found")

        # Verify user is authorized to sign
        authorized = False
        if signature_type == "doer" and record.doer_id == user_id:
            authorized = True
        elif signature_type == "checker" and record.checker_id == user_id:
            authorized = True
        elif signature_type == "approver" and record.approver_id == user_id:
            authorized = True

        if not authorized:
            raise ValueError(f"User not authorized to sign as {signature_type}")

        # Check if signature already exists
        existing = self.db.query(DigitalSignature).filter_by(
            record_id=record_id,
            signer_id=user_id,
            signature_type=signature_type,
            is_valid=True
        ).first()

        if existing:
            raise ValueError(f"Valid signature already exists for {signature_type}")

        # Create signature record
        signature = DigitalSignature(
            record_id=record_id,
            signer_id=user_id,
            signature_type=signature_type,
            signature_data=signature_data,
            signature_method=signature_method,
            signing_timestamp=datetime.utcnow().isoformat(),
            ip_address=ip_address,
            device_info=device_info,
            certificate_info=certificate_info,
            is_valid=True
        )
        self.db.add(signature)
        self.db.commit()

        return signature

    def verify_signature(self, signature_id: int) -> Dict:
        """Verify signature validity"""
        signature = self.db.query(DigitalSignature).filter_by(id=signature_id).first()
        if not signature:
            raise ValueError("Signature not found")

        # Get signer info
        signer = self.db.query(User).filter_by(id=signature.signer_id).first()

        # Get record info
        record = self.db.query(FormRecord).filter_by(id=signature.record_id).first()

        verification = {
            "signature_id": signature.id,
            "is_valid": signature.is_valid,
            "signature_type": signature.signature_type,
            "signer": {
                "id": signer.id,
                "username": signer.username,
                "full_name": signer.full_name,
                "email": signer.email
            } if signer else None,
            "record_number": record.record_number if record else None,
            "signing_timestamp": signature.signing_timestamp,
            "signature_method": signature.signature_method,
            "ip_address": signature.ip_address,
            "device_info": signature.device_info,
            "certificate_info": signature.certificate_info,
            "invalidated_at": signature.invalidated_at,
            "invalidation_reason": signature.invalidation_reason
        }

        # Additional verification checks
        if signature.is_valid:
            # Check if record still exists
            if not record:
                verification["warning"] = "Associated record not found"

            # Check if signer still exists
            if not signer:
                verification["warning"] = "Signer not found"

            # For certificate-based signatures, verify certificate
            if signature.signature_method == "certificate" and signature.certificate_info:
                cert_valid = self._verify_certificate(signature.certificate_info)
                verification["certificate_valid"] = cert_valid
                if not cert_valid:
                    verification["warning"] = "Certificate validation failed"

        return verification

    def invalidate_signature(
        self,
        signature_id: int,
        reason: str,
        user_id: int
    ) -> DigitalSignature:
        """Invalidate a signature"""
        signature = self.db.query(DigitalSignature).filter_by(id=signature_id).first()
        if not signature:
            raise ValueError("Signature not found")

        signature.is_valid = False
        signature.invalidated_at = datetime.utcnow().isoformat()
        signature.invalidation_reason = reason

        self.db.commit()

        return signature

    def get_record_signatures(self, record_id: int) -> List[Dict]:
        """Get all signatures for a record"""
        signatures = self.db.query(DigitalSignature).filter_by(
            record_id=record_id
        ).order_by(DigitalSignature.signing_timestamp).all()

        result = []
        for sig in signatures:
            signer = self.db.query(User).filter_by(id=sig.signer_id).first()
            result.append({
                "id": sig.id,
                "signature_type": sig.signature_type,
                "signer": {
                    "id": signer.id,
                    "username": signer.username,
                    "full_name": signer.full_name
                } if signer else None,
                "signature_method": sig.signature_method,
                "signing_timestamp": sig.signing_timestamp,
                "is_valid": sig.is_valid,
                "invalidated_at": sig.invalidated_at,
                "invalidation_reason": sig.invalidation_reason
            })

        return result

    def generate_signature_hash(self, data: str) -> str:
        """Generate hash for signature data"""
        return hashlib.sha256(data.encode()).hexdigest()

    def encode_signature_image(self, image_data: bytes) -> str:
        """Encode signature image to base64"""
        return base64.b64encode(image_data).decode('utf-8')

    def decode_signature_image(self, encoded_data: str) -> bytes:
        """Decode base64 signature image"""
        return base64.b64decode(encoded_data)

    def _verify_certificate(self, certificate_info: Dict) -> bool:
        """Verify digital certificate (placeholder)"""
        # This would integrate with actual certificate verification
        # For now, just check if required fields exist
        required_fields = ["issuer", "subject", "not_before", "not_after"]
        for field in required_fields:
            if field not in certificate_info:
                return False

        # Check certificate expiry
        try:
            not_after = datetime.fromisoformat(certificate_info["not_after"])
            if datetime.utcnow() > not_after:
                return False
        except:
            return False

        return True

    def create_signature_report(self, record_id: int) -> Dict:
        """Create signature verification report for a record"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            raise ValueError("Record not found")

        signatures = self.get_record_signatures(record_id)

        report = {
            "record_id": record.id,
            "record_number": record.record_number,
            "record_status": record.status.value,
            "signatures": signatures,
            "signature_count": len(signatures),
            "valid_signature_count": len([s for s in signatures if s["is_valid"]]),
            "signature_complete": False,
            "missing_signatures": []
        }

        # Check if all required signatures are present
        required_signatures = []
        if record.doer_id:
            required_signatures.append("doer")
        if record.checker_id and record.status.value in ["under_review", "approved"]:
            required_signatures.append("checker")
        if record.approver_id and record.status.value == "approved":
            required_signatures.append("approver")

        present_signatures = [s["signature_type"] for s in signatures if s["is_valid"]]

        for req_sig in required_signatures:
            if req_sig not in present_signatures:
                report["missing_signatures"].append(req_sig)

        report["signature_complete"] = len(report["missing_signatures"]) == 0

        return report
