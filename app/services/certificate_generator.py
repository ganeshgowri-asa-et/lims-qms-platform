"""
Digital Certificate Generation Service
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.config import settings
from app.utils.qr_generator import QRCodeGenerator
from app.utils.digital_signature import DigitalSignature
import os


class CertificateGenerator:
    """Generate digital test certificates with QR codes and signatures"""

    def __init__(self, output_dir: str = "reports/certificates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.qr_dir = self.output_dir / "qr_codes"
        self.qr_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_certificate_styles()

    def _setup_certificate_styles(self):
        """Setup custom styles for certificates"""
        self.styles.add(ParagraphStyle(
            name='CertTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CertText',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=15,
        ))

        self.styles.add(ParagraphStyle(
            name='CertInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
        ))

    def generate_certificate(
        self,
        certificate_data: Dict[str, Any],
        output_filename: str,
        include_qr: bool = True,
        sign_certificate: bool = True
    ) -> Dict[str, str]:
        """
        Generate digital test certificate

        Args:
            certificate_data: Certificate information
            output_filename: Name of output PDF file
            include_qr: Include QR code for verification
            sign_certificate: Digitally sign the certificate

        Returns:
            Dictionary with paths to generated files
        """
        output_path = self.output_dir / output_filename

        # Generate QR code if requested
        qr_path = None
        if include_qr:
            qr_filename = f"qr_{certificate_data['certificate_number']}.png"
            qr_path = self.qr_dir / qr_filename

            verification_url = certificate_data.get(
                'verification_url',
                f"https://verify.lab.com/cert/{certificate_data['certificate_number']}"
            )

            QRCodeGenerator.generate_certificate_qr(
                certificate_number=certificate_data['certificate_number'],
                report_id=certificate_data['report_id'],
                verification_url=verification_url,
                output_path=str(qr_path)
            )

        # Generate digital signature if requested
        signature_hash = None
        signature_data = None
        if sign_certificate:
            # Sign the certificate data
            signing_data = {
                "certificate_number": certificate_data['certificate_number'],
                "report_number": certificate_data['report_number'],
                "customer_name": certificate_data['customer_name'],
                "test_type": certificate_data['test_type'],
                "result": certificate_data['result'],
                "issue_date": str(certificate_data['issue_date'])
            }

            # For demo, we'll create a hash (in production, use actual key)
            signature_hash = DigitalSignature.hash_certificate_data(signing_data)

        # Build PDF certificate
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=30*mm,
            leftMargin=30*mm,
            topMargin=30*mm,
            bottomMargin=30*mm
        )

        story = []

        # Border decoration
        story.append(Spacer(1, 20))

        # Title
        title = Paragraph(
            "<b>TEST CERTIFICATE</b>",
            self.styles['CertTitle']
        )
        story.append(title)
        story.append(Spacer(1, 10))

        # Lab info
        lab_info = Paragraph(
            f"<b>{settings.LAB_NAME}</b><br/>{settings.LAB_ACCREDITATION}",
            self.styles['CertText']
        )
        story.append(lab_info)
        story.append(Spacer(1, 20))

        # Certificate text
        cert_text = Paragraph(
            """
            This is to certify that the photovoltaic module specified below has been
            tested in accordance with the referenced standard and has met the
            applicable requirements.
            """,
            self.styles['CertText']
        )
        story.append(cert_text)
        story.append(Spacer(1, 20))

        # Certificate details table
        details_data = [
            ['Certificate Number:', certificate_data['certificate_number']],
            ['Report Number:', certificate_data.get('report_number', 'N/A')],
            ['Customer:', certificate_data.get('customer_name', 'N/A')],
            ['Module Model:', certificate_data.get('module_model', 'N/A')],
            ['Test Standard:', certificate_data.get('test_standard', 'N/A')],
            ['Test Type:', certificate_data.get('test_type', 'N/A')],
            ['Test Result:', certificate_data.get('result', 'N/A')],
            ['Issue Date:', str(certificate_data.get('issue_date', datetime.now().date()))],
            ['Valid Until:', str(certificate_data.get('expiry_date', 'N/A'))],
        ]

        details_table = Table(details_data, colWidths=[60*mm, 90*mm])
        details_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.grey),
        ]))

        story.append(details_table)
        story.append(Spacer(1, 30))

        # QR Code and signature section
        if qr_path and os.path.exists(qr_path):
            qr_sig_data = []

            # QR Code column
            qr_content = [
                Paragraph("<b>Verify Online:</b>", self.styles['CertInfo']),
                Image(str(qr_path), width=40*mm, height=40*mm),
                Paragraph(
                    "Scan to verify certificate authenticity",
                    self.styles['CertInfo']
                )
            ]

            # Signature column
            sig_content = [
                Paragraph("<b>Digital Signature:</b>", self.styles['CertInfo']),
                Paragraph(f"Hash: {signature_hash[:32]}..." if signature_hash else "N/A",
                         self.styles['CertInfo']),
                Spacer(1, 10),
                Paragraph(f"<b>Signed By:</b> {certificate_data.get('signed_by', 'N/A')}",
                         self.styles['CertInfo']),
                Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                         self.styles['CertInfo'])
            ]

            # Create two-column layout
            qr_sig_table = Table(
                [[qr_content, sig_content]],
                colWidths=[75*mm, 75*mm]
            )
            qr_sig_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            story.append(qr_sig_table)

        story.append(Spacer(1, 30))

        # Footer
        footer_text = Paragraph(
            f"""
            <i>This certificate is valid only when verified through our online portal.
            Unauthorized reproduction is prohibited.<br/>
            Certificate ID: {certificate_data['certificate_number']} |
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
            """,
            self.styles['CertInfo']
        )
        story.append(footer_text)

        # Build PDF
        doc.build(story)

        return {
            "certificate_pdf": str(output_path),
            "qr_code": str(qr_path) if qr_path else None,
            "signature_hash": signature_hash
        }

    def generate_certificate_from_report(
        self,
        report_data: Dict[str, Any],
        validity_days: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Generate certificate from test report data

        Args:
            report_data: Complete test report data
            validity_days: Certificate validity period (days)

        Returns:
            Dictionary with paths to generated files
        """
        if validity_days is None:
            validity_days = settings.CERT_VALIDITY_DAYS

        # Generate certificate number
        cert_number = self._generate_certificate_number(report_data)

        # Prepare certificate data
        certificate_data = {
            "certificate_number": cert_number,
            "report_number": report_data.get('report_number'),
            "report_id": report_data.get('id'),
            "customer_name": report_data.get('customer_name'),
            "module_model": report_data.get('module_model'),
            "test_standard": report_data.get('iec_standard'),
            "test_type": report_data.get('test_type'),
            "result": report_data.get('overall_result'),
            "issue_date": datetime.now(),
            "expiry_date": datetime.now() + timedelta(days=validity_days),
            "signed_by": report_data.get('approved_by', 'Lab Director'),
            "verification_url": f"https://verify.lab.com/cert/{cert_number}"
        }

        # Generate certificate
        output_filename = f"certificate_{cert_number}.pdf"
        return self.generate_certificate(
            certificate_data=certificate_data,
            output_filename=output_filename,
            include_qr=True,
            sign_certificate=True
        )

    def _generate_certificate_number(self, report_data: Dict[str, Any]) -> str:
        """
        Generate unique certificate number

        Args:
            report_data: Test report data

        Returns:
            Unique certificate number
        """
        # Format: CERT-YYYY-NNNN-XXX
        year = datetime.now().year
        report_id = report_data.get('id', 0)
        standard = report_data.get('iec_standard', 'IEC')

        # Extract standard code (e.g., 61215 from "IEC 61215")
        std_code = ''.join(filter(str.isdigit, standard))[:5]

        return f"CERT-{year}-{std_code}-{report_id:04d}"

    def verify_certificate_signature(
        self,
        certificate_data: Dict[str, Any],
        signature: str,
        public_key_pem: bytes
    ) -> bool:
        """
        Verify certificate digital signature

        Args:
            certificate_data: Certificate data
            signature: Signature to verify
            public_key_pem: Public key for verification

        Returns:
            True if signature is valid
        """
        return DigitalSignature.verify_signature(
            data=certificate_data,
            signature_base64=signature,
            public_key_pem=public_key_pem
        )
