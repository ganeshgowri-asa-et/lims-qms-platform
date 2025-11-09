"""
QR Code Generation Utilities
"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from pathlib import Path
from typing import Optional
import json


class QRCodeGenerator:
    """Generate QR codes for test certificates and reports"""

    @staticmethod
    def generate_qr_code(
        data: str,
        output_path: str,
        size: int = 10,
        border: int = 2,
        error_correction: int = qrcode.constants.ERROR_CORRECT_H
    ) -> str:
        """
        Generate a QR code image

        Args:
            data: Data to encode in QR code
            output_path: Path to save the QR code image
            size: Size of the QR code (box size)
            border: Border size in boxes
            error_correction: Error correction level

        Returns:
            Path to the generated QR code image
        """
        # Create QR code instance
        qr = qrcode.QRCode(
            version=None,  # Auto-determine version
            error_correction=error_correction,
            box_size=size,
            border=border,
        )

        # Add data
        qr.add_data(data)
        qr.make(fit=True)

        # Create image with styled appearance
        img = qr.make_image(
            fill_color="black",
            back_color="white",
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer()
        )

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save image
        img.save(output_path)

        return output_path

    @staticmethod
    def generate_certificate_qr(
        certificate_number: str,
        report_id: int,
        verification_url: str,
        output_path: str
    ) -> str:
        """
        Generate QR code for test certificate

        Args:
            certificate_number: Certificate number
            report_id: Test report ID
            verification_url: URL for certificate verification
            output_path: Path to save QR code

        Returns:
            Path to generated QR code
        """
        # Create verification data
        qr_data = {
            "certificate_number": certificate_number,
            "report_id": report_id,
            "verification_url": verification_url,
            "type": "test_certificate"
        }

        # Encode as JSON
        data_str = json.dumps(qr_data)

        return QRCodeGenerator.generate_qr_code(
            data=data_str,
            output_path=output_path,
            size=10,
            border=2
        )

    @staticmethod
    def generate_verification_qr(
        verification_url: str,
        output_path: str
    ) -> str:
        """
        Generate simple QR code with verification URL

        Args:
            verification_url: URL to encode
            output_path: Path to save QR code

        Returns:
            Path to generated QR code
        """
        return QRCodeGenerator.generate_qr_code(
            data=verification_url,
            output_path=output_path,
            size=10,
            border=2
        )
