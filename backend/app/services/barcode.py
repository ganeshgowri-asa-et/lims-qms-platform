"""
Barcode generation service for samples and test requests
"""
import base64
from io import BytesIO
from typing import Optional
import barcode
from barcode.writer import ImageWriter


class BarcodeService:
    """Service for generating barcodes and QR codes"""

    @staticmethod
    def generate_code128(data: str, width: int = 2, height: int = 15) -> str:
        """
        Generate Code128 barcode for a document number

        Args:
            data: Data to encode (e.g., TRQ-2025-00001)
            width: Width of bars
            height: Height of barcode in mm

        Returns:
            Base64 encoded PNG image string
        """
        try:
            # Create Code128 barcode
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(data, writer=ImageWriter())

            # Generate image in memory
            buffer = BytesIO()
            barcode_instance.write(
                buffer,
                options={
                    'module_width': width,
                    'module_height': height,
                    'quiet_zone': 6.5,
                    'text_distance': 5,
                    'font_size': 10,
                    'write_text': True
                }
            )

            # Convert to base64
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return f"data:image/png;base64,{img_base64}"

        except Exception as e:
            print(f"Error generating barcode: {e}")
            return ""

    @staticmethod
    def generate_qrcode(data: str, box_size: int = 10, border: int = 4) -> str:
        """
        Generate QR code for quick sample lookup

        Args:
            data: Data to encode
            box_size: Size of each box in pixels
            border: Border size in boxes

        Returns:
            Base64 encoded PNG image string
        """
        try:
            import qrcode

            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=box_size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Generate image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return f"data:image/png;base64,{img_base64}"

        except Exception as e:
            print(f"Error generating QR code: {e}")
            return ""

    @staticmethod
    def generate_barcode_for_sample(sample_number: str) -> str:
        """
        Generate barcode specifically for sample tracking

        Args:
            sample_number: Sample number (e.g., SMP-2025-00001)

        Returns:
            Base64 encoded barcode image
        """
        return BarcodeService.generate_code128(sample_number)

    @staticmethod
    def generate_barcode_for_test_request(trq_number: str) -> str:
        """
        Generate barcode specifically for test request

        Args:
            trq_number: Test request number (e.g., TRQ-2025-00001)

        Returns:
            Base64 encoded barcode image
        """
        return BarcodeService.generate_code128(trq_number)
