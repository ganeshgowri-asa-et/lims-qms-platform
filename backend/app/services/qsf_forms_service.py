"""
QSF Forms Generation Service
Quality System Forms for Training Management
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from ..models.training import TrainingAttendance, TrainingMaster
from ..config import settings


class QSFFormsService:
    """Service for generating QSF forms for training management"""

    def __init__(self, upload_dir: str = None):
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        self.forms_dir = Path(self.upload_dir) / "qsf_forms"
        self.forms_dir.mkdir(parents=True, exist_ok=True)

    def generate_qsf0203_training_attendance(
        self,
        db: Session,
        training_id: int,
        training_date: date,
        attendees: List[Dict]
    ) -> str:
        """
        Generate QSF0203 - Training Attendance Record

        Args:
            db: Database session
            training_id: Training program ID
            training_date: Date of training
            attendees: List of attendee dictionaries with employee details

        Returns:
            Path to generated PDF
        """
        # Get training details
        training = db.query(TrainingMaster).filter(
            TrainingMaster.id == training_id
        ).first()

        if not training:
            raise ValueError(f"Training {training_id} not found")

        # Create PDF
        filename = f"QSF0203_Training_Attendance_{training_date.strftime('%Y%m%d')}.pdf"
        filepath = self.forms_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor("#1a5490"),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Header
        story.append(Paragraph(settings.ORG_NAME, header_style))
        story.append(Paragraph("Training Attendance Record", title_style))
        story.append(Paragraph("QSF0203 - Rev 01", header_style))
        story.append(Spacer(1, 10*mm))

        # Training details table
        training_data = [
            ["Training Code:", training.training_code, "Training Date:", training_date.strftime("%d-%b-%Y")],
            ["Training Name:", training.training_name, "Duration:", f"{training.duration_hours or 'N/A'} hours"],
            ["Category:", training.category, "Type:", training.type],
            ["Trainer:", training.trainer or "", "Location:", ""],
        ]

        training_table = Table(training_data, colWidths=[35*mm, 60*mm, 30*mm, 50*mm])
        training_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(training_table)
        story.append(Spacer(1, 10*mm))

        # Attendance table header
        story.append(Paragraph("Attendance Register", styles['Heading2']))
        story.append(Spacer(1, 5*mm))

        # Attendance table
        attendance_data = [
            ["S.No", "Employee ID", "Employee Name", "Department", "Signature", "Time In", "Time Out"]
        ]

        for idx, attendee in enumerate(attendees, 1):
            attendance_data.append([
                str(idx),
                attendee.get("employee_id", ""),
                attendee.get("employee_name", ""),
                attendee.get("department", ""),
                "",  # Signature column
                "",  # Time in
                ""   # Time out
            ])

        attendance_table = Table(
            attendance_data,
            colWidths=[15*mm, 25*mm, 45*mm, 35*mm, 30*mm, 20*mm, 20*mm]
        )
        attendance_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a5490")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(attendance_table)
        story.append(Spacer(1, 15*mm))

        # Signature section
        sig_data = [
            ["Prepared By:", "", "Reviewed By:", "", "Approved By:", ""],
            ["Name:", "", "Name:", "", "Name:", ""],
            ["Signature:", "", "Signature:", "", "Signature:", ""],
            ["Date:", "", "Date:", "", "Date:", ""],
        ]

        sig_table = Table(sig_data, colWidths=[25*mm, 30*mm, 25*mm, 30*mm, 25*mm, 30*mm])
        sig_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (4, 0), (4, -1), 'Helvetica-Bold'),
        ]))
        story.append(sig_table)

        doc.build(story)
        return str(filepath)

    def generate_qsf0205_training_effectiveness(
        self,
        db: Session,
        attendance_id: int,
        evaluation_data: Dict
    ) -> str:
        """
        Generate QSF0205 - Training Effectiveness Evaluation

        Args:
            db: Database session
            attendance_id: Training attendance record ID
            evaluation_data: Dictionary with evaluation details

        Returns:
            Path to generated PDF
        """
        # Get attendance record
        attendance = db.query(TrainingAttendance).join(
            TrainingMaster
        ).filter(TrainingAttendance.id == attendance_id).first()

        if not attendance:
            raise ValueError(f"Attendance record {attendance_id} not found")

        # Create PDF
        filename = f"QSF0205_Effectiveness_{attendance.employee_id}_{date.today().strftime('%Y%m%d')}.pdf"
        filepath = self.forms_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor("#1a5490"),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        story.append(Paragraph(settings.ORG_NAME, header_style))
        story.append(Paragraph("Training Effectiveness Evaluation", title_style))
        story.append(Paragraph("QSF0205 - Rev 01", header_style))
        story.append(Spacer(1, 10*mm))

        # Training and employee details
        details_data = [
            ["Employee ID:", attendance.employee_id, "Employee Name:", attendance.employee_name],
            ["Department:", attendance.department or "", "Job Role:", ""],
            ["Training Name:", attendance.training.training_name, "", ""],
            ["Training Date:", attendance.training_date.strftime("%d-%b-%Y"), "Evaluation Date:", evaluation_data.get("evaluation_date", date.today()).strftime("%d-%b-%Y")],
        ]

        details_table = Table(details_data, colWidths=[35*mm, 60*mm, 35*mm, 45*mm])
        details_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 10*mm))

        # Evaluation criteria
        story.append(Paragraph("Evaluation Criteria (Rate 1-5)", styles['Heading3']))
        story.append(Spacer(1, 5*mm))

        eval_data = [
            ["Criterion", "Rating (1-5)", "Remarks"],
            ["Knowledge Retention", evaluation_data.get("knowledge_retention", ""), ""],
            ["Practical Application", evaluation_data.get("practical_application", ""), ""],
            ["Behavior Change", evaluation_data.get("behavior_change", ""), ""],
            ["Business Impact", evaluation_data.get("business_impact", ""), ""],
            ["Overall Effectiveness", evaluation_data.get("overall_effectiveness", ""), ""],
        ]

        eval_table = Table(eval_data, colWidths=[60*mm, 40*mm, 75*mm])
        eval_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a5490")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(eval_table)
        story.append(Spacer(1, 10*mm))

        # Comments
        story.append(Paragraph("Evaluator Comments:", styles['Heading3']))
        story.append(Spacer(1, 3*mm))
        comments = evaluation_data.get("comments", "")
        story.append(Paragraph(comments or "[Comments to be filled]", styles['Normal']))
        story.append(Spacer(1, 10*mm))

        # Follow-up actions
        story.append(Paragraph("Follow-up Actions Required:", styles['Heading3']))
        story.append(Spacer(1, 3*mm))
        follow_up = evaluation_data.get("follow_up_required", False)
        story.append(Paragraph(f"☐ Yes   ☐ No", styles['Normal']))
        story.append(Spacer(1, 15*mm))

        # Signature
        sig_data = [
            ["Evaluator Name:", "", "Signature:", "", "Date:", ""],
        ]

        sig_table = Table(sig_data, colWidths=[35*mm, 45*mm, 25*mm, 35*mm, 15*mm, 20*mm])
        sig_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(sig_table)

        doc.build(story)
        return str(filepath)

    def generate_qsf0206_training_needs_assessment(
        self,
        db: Session,
        department: str,
        assessment_data: Dict
    ) -> str:
        """
        Generate QSF0206 - Training Needs Assessment

        Args:
            db: Database session
            department: Department name
            assessment_data: Dictionary with assessment details

        Returns:
            Path to generated PDF
        """
        filename = f"QSF0206_TNA_{department.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        filepath = self.forms_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor("#1a5490"),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        story.append(Paragraph(settings.ORG_NAME, header_style))
        story.append(Paragraph("Training Needs Assessment", title_style))
        story.append(Paragraph("QSF0206 - Rev 01", header_style))
        story.append(Spacer(1, 10*mm))

        # Assessment details
        details_data = [
            ["Department:", department, "Assessment Period:", assessment_data.get("period", "")],
            ["Prepared By:", assessment_data.get("prepared_by", ""), "Date:", assessment_data.get("date", date.today()).strftime("%d-%b-%Y")],
        ]

        details_table = Table(details_data, colWidths=[35*mm, 65*mm, 40*mm, 35*mm])
        details_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 10*mm))

        # Training needs table
        story.append(Paragraph("Identified Training Needs", styles['Heading3']))
        story.append(Spacer(1, 5*mm))

        needs_data = [
            ["Training Topic", "Target Group", "Priority", "Proposed Date", "Estimated Cost"]
        ]

        training_needs = assessment_data.get("training_needs", [])
        for need in training_needs:
            needs_data.append([
                need.get("topic", ""),
                need.get("target_group", ""),
                need.get("priority", ""),
                need.get("proposed_date", ""),
                need.get("cost", "")
            ])

        needs_table = Table(needs_data, colWidths=[50*mm, 40*mm, 25*mm, 30*mm, 30*mm])
        needs_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a5490")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(needs_table)
        story.append(Spacer(1, 15*mm))

        # Approval section
        sig_data = [
            ["Department Head:", "", "HR Manager:", "", "Management Approval:", ""],
            ["Signature:", "", "Signature:", "", "Signature:", ""],
            ["Date:", "", "Date:", "", "Date:", ""],
        ]

        sig_table = Table(sig_data, colWidths=[35*mm, 25*mm, 30*mm, 25*mm, 40*mm, 20*mm])
        sig_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        story.append(sig_table)

        doc.build(story)
        return str(filepath)
