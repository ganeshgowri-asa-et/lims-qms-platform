"""PDF generation utilities with watermarks."""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from typing import Dict, Any, Optional


class WatermarkCanvas(canvas.Canvas):
    """Custom canvas class to add watermarks to PDF pages."""

    def __init__(self, *args, watermark_text: str = "CONTROLLED COPY", **kwargs):
        super().__init__(*args, **kwargs)
        self.watermark_text = watermark_text

    def showPage(self):
        """Override showPage to add watermark before showing the page."""
        self.add_watermark()
        super().showPage()

    def add_watermark(self):
        """Add diagonal watermark to the page."""
        self.saveState()
        self.setFont("Helvetica", 60)
        self.setFillColor(colors.lightgrey)
        self.setFillAlpha(0.3)

        # Calculate center of page
        page_width = letter[0]
        page_height = letter[1]

        # Rotate and draw watermark
        self.translate(page_width / 2, page_height / 2)
        self.rotate(45)
        self.drawCentredString(0, 0, self.watermark_text)

        self.restoreState()


def generate_document_pdf(
    document_data: Dict[str, Any],
    output_path: str,
    watermark_text: Optional[str] = "CONTROLLED COPY",
) -> str:
    """
    Generate a PDF document with header, content, and watermark.

    Args:
        document_data: Dictionary containing document information
        output_path: Path where PDF will be saved
        watermark_text: Text for watermark (None to disable)

    Returns:
        Path to generated PDF
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create PDF with watermark canvas if needed
    if watermark_text:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        def on_first_page(canvas, doc):
            wc = WatermarkCanvas(canvas._filename, watermark_text=watermark_text)
            wc.add_watermark()

        def on_later_pages(canvas, doc):
            wc = WatermarkCanvas(canvas._filename, watermark_text=watermark_text)
            wc.add_watermark()
    else:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        on_first_page = None
        on_later_pages = None

    # Container for PDF elements
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1f4788"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    header_style = ParagraphStyle(
        "CustomHeader",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1f4788"),
        spaceAfter=12,
    )

    # Add title
    title = Paragraph(document_data.get("title", "QMS Document"), title_style)
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Add document metadata table
    metadata = [
        ["Document Number:", document_data.get("doc_number", "N/A")],
        ["Revision:", document_data.get("current_revision", "1.0")],
        ["Status:", document_data.get("status", "Draft")],
        ["Owner:", document_data.get("owner", "N/A")],
        ["Department:", document_data.get("department", "N/A")],
        ["Effective Date:", document_data.get("effective_date", "N/A")],
        ["Created By:", document_data.get("created_by", "N/A")],
        ["Approved By:", document_data.get("approved_by", "N/A")],
    ]

    metadata_table = Table(metadata, colWidths=[2 * inch, 4 * inch])
    metadata_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eaf6")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(metadata_table)
    story.append(Spacer(1, 0.3 * inch))

    # Add description/content
    if document_data.get("description"):
        story.append(Paragraph("Description", header_style))
        content = Paragraph(document_data["description"], styles["BodyText"])
        story.append(content)
        story.append(Spacer(1, 0.2 * inch))

    # Add revision history if available
    if document_data.get("revisions"):
        story.append(Paragraph("Revision History", header_style))
        revision_data = [["Revision", "Date", "Revised By", "Reason"]]

        for rev in document_data["revisions"]:
            revision_data.append(
                [
                    rev.get("revision_number", ""),
                    rev.get("created_at", ""),
                    rev.get("revised_by", ""),
                    rev.get("revision_reason", ""),
                ]
            )

        revision_table = Table(revision_data, colWidths=[1 * inch, 1.5 * inch, 1.5 * inch, 2.5 * inch])
        revision_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4788")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(revision_table)

    # Add footer with generation timestamp
    story.append(Spacer(1, 0.5 * inch))
    footer_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    footer = Paragraph(footer_text, styles["Italic"])
    story.append(footer)

    # Build PDF
    if on_first_page and on_later_pages:
        doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    else:
        doc.build(story)

    return output_path


def add_watermark(input_pdf: str, output_pdf: str, watermark_text: str = "CONTROLLED COPY"):
    """
    Add watermark to an existing PDF.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF with watermark
        watermark_text: Text for watermark
    """
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import io

    # Create watermark
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 60)
    can.setFillColor(colors.lightgrey)
    can.setFillAlpha(0.3)

    # Calculate center and rotate
    can.translate(letter[0] / 2, letter[1] / 2)
    can.rotate(45)
    can.drawCentredString(0, 0, watermark_text)
    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)

    # Read the existing PDF
    existing_pdf = PdfReader(open(input_pdf, "rb"))
    watermark_pdf = PdfReader(packet)

    # Merge watermark with each page
    output = PdfWriter()

    for page in existing_pdf.pages:
        page.merge_page(watermark_pdf.pages[0])
        output.add_page(page)

    # Write output
    with open(output_pdf, "wb") as output_stream:
        output.write(output_stream)

    return output_pdf
