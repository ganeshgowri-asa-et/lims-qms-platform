"""
PDF generation and watermarking service
"""
import os
from typing import Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from datetime import datetime

from app.models.document import QMSDocument
from app.core.config import settings


class PDFService:
    """
    Service for generating and watermarking PDF documents
    """

    @staticmethod
    def create_watermark(
        text: str = None,
        opacity: float = None,
        page_size: tuple = letter
    ) -> BytesIO:
        """
        Create a watermark PDF

        Args:
            text: Watermark text (default from settings)
            opacity: Watermark opacity 0-1 (default from settings)
            page_size: Page size tuple

        Returns:
            BytesIO object containing watermark PDF
        """
        if text is None:
            text = settings.WATERMARK_TEXT
        if opacity is None:
            opacity = settings.WATERMARK_OPACITY

        # Create watermark PDF in memory
        watermark_buffer = BytesIO()
        c = canvas.Canvas(watermark_buffer, pagesize=page_size)

        # Set watermark properties
        c.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
        c.setFont("Helvetica-Bold", 60)

        # Calculate position (diagonal across page)
        width, height = page_size
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()

        c.save()
        watermark_buffer.seek(0)

        return watermark_buffer

    @staticmethod
    def add_watermark_to_pdf(
        input_path: str,
        output_path: str,
        watermark_text: Optional[str] = None,
        opacity: Optional[float] = None
    ):
        """
        Add watermark to existing PDF

        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            watermark_text: Optional watermark text
            opacity: Optional opacity
        """
        # Read input PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Get page size from first page
        first_page = reader.pages[0]
        page_size = (
            float(first_page.mediabox.width),
            float(first_page.mediabox.height)
        )

        # Create watermark
        watermark_buffer = PDFService.create_watermark(
            text=watermark_text,
            opacity=opacity,
            page_size=page_size
        )
        watermark_reader = PdfReader(watermark_buffer)
        watermark_page = watermark_reader.pages[0]

        # Apply watermark to each page
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)

        # Write output
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

    @staticmethod
    def generate_document_pdf(
        document: QMSDocument,
        output_path: str,
        include_watermark: bool = True
    ):
        """
        Generate PDF for a QMS document

        Args:
            document: QMS Document
            output_path: Output file path
            include_watermark: Whether to include watermark
        """
        # Create temporary PDF without watermark
        temp_path = output_path + ".temp.pdf"

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for the 'Flowable' objects
        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        elements.append(Paragraph(document.title, title_style))
        elements.append(Spacer(1, 12))

        # Document metadata table
        metadata = [
            ['Document Number:', document.doc_number],
            ['Version:', document.version_string],
            ['Type:', document.type.value],
            ['Status:', document.status.value],
            ['Owner:', document.owner],
            ['Department:', document.department or 'N/A'],
            ['Created:', document.created_at.strftime('%Y-%m-%d %H:%M:%S') if document.created_at else 'N/A'],
            ['Effective Date:', document.effective_date.strftime('%Y-%m-%d') if document.effective_date else 'N/A'],
        ]

        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(metadata_table)
        elements.append(Spacer(1, 20))

        # Description
        if document.description:
            elements.append(Paragraph('Description', heading_style))
            elements.append(Paragraph(document.description, styles['Normal']))
            elements.append(Spacer(1, 20))

        # Content
        if document.content_text:
            elements.append(Paragraph('Content', heading_style))
            elements.append(Paragraph(document.content_text, styles['Normal']))

        # Build PDF
        doc.build(elements)

        # Add watermark if requested
        if include_watermark and document.status in ['EFFECTIVE', 'APPROVED']:
            PDFService.add_watermark_to_pdf(temp_path, output_path)
            os.remove(temp_path)
        else:
            os.rename(temp_path, output_path)

    @staticmethod
    def generate_approval_sheet(
        document: QMSDocument,
        signatures: list,
        output_path: str
    ):
        """
        Generate approval signature sheet

        Args:
            document: QMS Document
            signatures: List of document signatures
            output_path: Output file path
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        elements.append(Paragraph('Document Approval Sheet', title_style))
        elements.append(Spacer(1, 20))

        # Document info
        doc_info = [
            ['Document Number:', document.doc_number],
            ['Title:', document.title],
            ['Version:', document.version_string],
        ]

        info_table = Table(doc_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 30))

        # Signatures
        elements.append(Paragraph('Approval Signatures', styles['Heading2']))
        elements.append(Spacer(1, 12))

        sig_data = [['Role', 'Name', 'Date', 'Comments']]
        for sig in signatures:
            sig_data.append([
                sig.role.value,
                sig.signer,
                sig.signature_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                sig.comments or ''
            ])

        sig_table = Table(sig_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(sig_table)

        # Build PDF
        doc.build(elements)
