"""
Training Certificate Generation Service
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import date, timedelta
from pathlib import Path
import qrcode
from io import BytesIO
from typing import Optional
import os

from sqlalchemy.orm import Session
from ..models.training import TrainingAttendance, TrainingMaster
from ..config import settings


class CertificateService:
    """Service for generating training certificates"""

    def __init__(self, upload_dir: str = None):
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        self.certificates_dir = Path(self.upload_dir) / "certificates"
        self.certificates_dir.mkdir(parents=True, exist_ok=True)

    def generate_certificate(
        self,
        db: Session,
        attendance_id: int,
        template: str = "default"
    ) -> dict:
        """
        Generate training certificate PDF

        Args:
            db: Database session
            attendance_id: Training attendance record ID
            template: Certificate template to use

        Returns:
            Dictionary with certificate details
        """
        # Get attendance record with training details
        attendance = db.query(TrainingAttendance).join(
            TrainingMaster,
            TrainingAttendance.training_id == TrainingMaster.id
        ).filter(TrainingAttendance.id == attendance_id).first()

        if not attendance:
            raise ValueError(f"Attendance record {attendance_id} not found")

        if attendance.pass_fail != "Pass":
            raise ValueError("Certificate can only be generated for passed trainings")

        # Generate certificate number if not exists
        if not attendance.certificate_number:
            attendance.certificate_number = self._generate_certificate_number(
                attendance.training_date,
                attendance.employee_id
            )
            attendance.certificate_issue_date = date.today()

            # Calculate validity
            if attendance.training.validity_months:
                attendance.certificate_valid_until = date.today() + timedelta(
                    days=attendance.training.validity_months * 30
                )

        # Generate PDF
        cert_filename = f"CERT_{attendance.certificate_number}.pdf"
        cert_path = self.certificates_dir / cert_filename

        if template == "default":
            self._generate_default_certificate(attendance, str(cert_path))
        else:
            self._generate_default_certificate(attendance, str(cert_path))

        # Update attendance record
        attendance.certificate_path = str(cert_path)
        db.commit()

        return {
            "certificate_number": attendance.certificate_number,
            "certificate_path": str(cert_path),
            "issue_date": attendance.certificate_issue_date,
            "valid_until": attendance.certificate_valid_until
        }

    def _generate_certificate_number(self, training_date: date, employee_id: str) -> str:
        """Generate unique certificate number"""
        return f"TRN-{training_date.strftime('%Y%m')}-{employee_id}-{training_date.strftime('%d')}"

    def _generate_default_certificate(self, attendance: TrainingAttendance, output_path: str):
        """Generate default certificate template"""
        # Create PDF in landscape mode
        pdf = canvas.Canvas(output_path, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Draw border
        pdf.setLineWidth(2)
        pdf.setStrokeColor(colors.HexColor("#1a5490"))
        pdf.rect(20*mm, 20*mm, width-40*mm, height-40*mm, stroke=1, fill=0)

        # Inner decorative border
        pdf.setLineWidth(0.5)
        pdf.rect(25*mm, 25*mm, width-50*mm, height-50*mm, stroke=1, fill=0)

        # Title
        pdf.setFont("Helvetica-Bold", 32)
        pdf.setFillColor(colors.HexColor("#1a5490"))
        pdf.drawCentredString(width/2, height-60*mm, "CERTIFICATE OF TRAINING")

        # Subtitle
        pdf.setFont("Helvetica", 14)
        pdf.setFillColor(colors.black)
        pdf.drawCentredString(width/2, height-70*mm, "This is to certify that")

        # Employee name
        pdf.setFont("Helvetica-Bold", 24)
        pdf.setFillColor(colors.HexColor("#1a5490"))
        pdf.drawCentredString(width/2, height-85*mm, attendance.employee_name.upper())

        # Department
        pdf.setFont("Helvetica-Oblique", 12)
        pdf.setFillColor(colors.black)
        pdf.drawCentredString(
            width/2,
            height-92*mm,
            f"Department: {attendance.department or 'N/A'}"
        )

        # Training details
        pdf.setFont("Helvetica", 14)
        pdf.drawCentredString(width/2, height-105*mm, "has successfully completed the training on")

        pdf.setFont("Helvetica-Bold", 18)
        pdf.setFillColor(colors.HexColor("#1a5490"))

        # Handle long training names
        training_name = attendance.training.training_name
        if len(training_name) > 60:
            # Split into two lines
            words = training_name.split()
            line1 = ""
            line2 = ""
            for word in words:
                if len(line1 + word) < 60:
                    line1 += word + " "
                else:
                    line2 += word + " "
            pdf.drawCentredString(width/2, height-115*mm, line1.strip())
            pdf.drawCentredString(width/2, height-122*mm, line2.strip())
            y_offset = 130
        else:
            pdf.drawCentredString(width/2, height-115*mm, training_name)
            y_offset = 122

        # Training details table
        pdf.setFont("Helvetica", 11)
        pdf.setFillColor(colors.black)

        details_y = height - y_offset*mm
        left_x = width/2 - 80*mm
        right_x = width/2 + 20*mm

        pdf.drawString(left_x, details_y, f"Training Date:")
        pdf.drawString(right_x, details_y, f"{attendance.training_date.strftime('%d-%b-%Y')}")

        details_y -= 15
        pdf.drawString(left_x, details_y, f"Duration:")
        pdf.drawString(right_x, details_y, f"{attendance.training.duration_hours or 'N/A'} hours")

        details_y -= 15
        pdf.drawString(left_x, details_y, f"Trainer:")
        pdf.drawString(right_x, details_y, f"{attendance.trainer_name or 'N/A'}")

        details_y -= 15
        pdf.drawString(left_x, details_y, f"Assessment Score:")
        pdf.drawString(right_x, details_y, f"{attendance.overall_score or 'N/A'}%")

        # Certificate details
        details_y -= 20
        pdf.setFont("Helvetica", 10)
        pdf.drawString(left_x, details_y, f"Certificate Number: {attendance.certificate_number}")

        if attendance.certificate_issue_date:
            pdf.drawString(right_x + 40*mm, details_y, f"Issue Date: {attendance.certificate_issue_date.strftime('%d-%b-%Y')}")

        details_y -= 12
        if attendance.certificate_valid_until:
            pdf.drawString(left_x, details_y, f"Valid Until: {attendance.certificate_valid_until.strftime('%d-%b-%Y')}")

        # QR Code
        qr_img = self._generate_qr_code(attendance.certificate_number)
        pdf.drawInlineImage(qr_img, width - 60*mm, 30*mm, width=25*mm, height=25*mm)

        # Signature line
        sig_y = 40*mm
        pdf.setLineWidth(0.5)
        pdf.line(width/2 - 50*mm, sig_y, width/2 + 50*mm, sig_y)

        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(width/2, sig_y - 5*mm, "Authorized Signatory")
        pdf.drawCentredString(width/2, sig_y - 10*mm, settings.ORG_NAME)

        # Footer
        pdf.setFont("Helvetica-Oblique", 8)
        pdf.setFillColor(colors.grey)
        pdf.drawCentredString(
            width/2,
            25*mm,
            "This is a computer-generated certificate and is valid without signature"
        )

        pdf.save()

    def _generate_qr_code(self, certificate_number: str) -> BytesIO:
        """Generate QR code for certificate verification"""
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(f"CERT:{certificate_number}")
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

    def generate_batch_certificates(
        self,
        db: Session,
        attendance_ids: list,
        template: str = "default"
    ) -> list:
        """Generate certificates for multiple attendance records"""
        results = []
        for attendance_id in attendance_ids:
            try:
                cert = self.generate_certificate(db, attendance_id, template)
                results.append({"attendance_id": attendance_id, "success": True, "certificate": cert})
            except Exception as e:
                results.append({"attendance_id": attendance_id, "success": False, "error": str(e)})
        return results
