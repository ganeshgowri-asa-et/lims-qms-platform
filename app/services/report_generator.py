"""
PDF Report Generation Service
"""
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import settings
import os


class ReportGenerator:
    """Generate PDF test reports"""

    def __init__(self, output_dir: str = "reports/pdf"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Subheading style
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))

        # Info text style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
        ))

    def _create_header(self, canvas, doc):
        """Create page header"""
        canvas.saveState()
        # Lab name
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(30*mm, 280*mm, settings.LAB_NAME)

        # Accreditation
        canvas.setFont('Helvetica', 9)
        canvas.drawString(30*mm, 275*mm, f"Accredited: {settings.LAB_ACCREDITATION}")

        # Page number
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(180*mm, 280*mm, f"Page {doc.page}")

        # Header line
        canvas.setStrokeColor(colors.HexColor('#1f4788'))
        canvas.setLineWidth(2)
        canvas.line(30*mm, 272*mm, 180*mm, 272*mm)

        canvas.restoreState()

    def _create_footer(self, canvas, doc):
        """Create page footer"""
        canvas.saveState()
        # Footer line
        canvas.setStrokeColor(colors.HexColor('#1f4788'))
        canvas.setLineWidth(1)
        canvas.line(30*mm, 20*mm, 180*mm, 20*mm)

        # Footer text
        canvas.setFont('Helvetica', 8)
        canvas.drawString(30*mm, 15*mm, settings.LAB_ADDRESS)
        canvas.drawRightString(180*mm, 15*mm,
                              f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        canvas.restoreState()

    def generate_test_report(
        self,
        report_data: Dict[str, Any],
        output_filename: str,
        include_graphs: bool = True
    ) -> str:
        """
        Generate complete test report PDF

        Args:
            report_data: Complete report data including tests and results
            output_filename: Name of output PDF file
            include_graphs: Whether to include graphs in report

        Returns:
            Path to generated PDF
        """
        output_path = self.output_dir / output_filename
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=30*mm,
            leftMargin=30*mm,
            topMargin=40*mm,
            bottomMargin=30*mm
        )

        # Build story (content)
        story = []

        # Title page
        story.extend(self._build_title_page(report_data))
        story.append(PageBreak())

        # Report information
        story.extend(self._build_report_info(report_data))
        story.append(Spacer(1, 12))

        # Module specifications
        story.extend(self._build_module_specs(report_data))
        story.append(Spacer(1, 12))

        # Test results
        story.extend(self._build_test_results(report_data))
        story.append(Spacer(1, 12))

        # Graphs
        if include_graphs and report_data.get('graphs'):
            story.append(PageBreak())
            story.extend(self._build_graphs_section(report_data['graphs']))

        # Evaluation summary
        story.append(PageBreak())
        story.extend(self._build_evaluation_summary(report_data))

        # Signatures
        story.append(Spacer(1, 24))
        story.extend(self._build_signatures(report_data))

        # Build PDF
        doc.build(
            story,
            onFirstPage=self._create_header,
            onLaterPages=self._create_header
        )

        return str(output_path)

    def _build_title_page(self, report_data: Dict[str, Any]) -> List:
        """Build title page content"""
        content = []

        content.append(Spacer(1, 50))

        # Report title
        title = Paragraph(
            f"<b>IEC Test Report</b><br/>{report_data.get('iec_standard', '')}",
            self.styles['CustomTitle']
        )
        content.append(title)
        content.append(Spacer(1, 30))

        # Report number
        report_num = Paragraph(
            f"<b>Report Number:</b> {report_data.get('report_number', 'N/A')}",
            self.styles['Heading2']
        )
        content.append(report_num)
        content.append(Spacer(1, 30))

        # Basic info table
        info_data = [
            ['Customer:', report_data.get('customer_name', 'N/A')],
            ['Sample ID:', report_data.get('sample_id', 'N/A')],
            ['Module Model:', report_data.get('module_model', 'N/A')],
            ['Test Type:', report_data.get('test_type', 'N/A')],
            ['Test Date:', report_data.get('test_start_date', 'N/A')],
            ['Report Date:', report_data.get('report_date', 'N/A')],
        ]

        info_table = Table(info_data, colWidths=[60*mm, 90*mm])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        content.append(info_table)
        content.append(Spacer(1, 40))

        # Overall result
        result = report_data.get('overall_result', 'NOT_TESTED')
        result_color = colors.green if result == 'PASS' else colors.red

        result_text = Paragraph(
            f"<b>Overall Result: <font color='{result_color.hexval()}'>{result}</font></b>",
            self.styles['Heading1']
        )
        content.append(result_text)

        return content

    def _build_report_info(self, report_data: Dict[str, Any]) -> List:
        """Build report information section"""
        content = []

        content.append(Paragraph("Report Information", self.styles['SectionHeading']))

        info_text = f"""
        <b>Test Objective:</b> {report_data.get('test_objective', 'N/A')}<br/>
        <b>Status:</b> {report_data.get('status', 'N/A')}<br/>
        <b>Tested By:</b> {report_data.get('tested_by', 'N/A')}<br/>
        <b>Reviewed By:</b> {report_data.get('reviewed_by', 'N/A')}<br/>
        <b>Approved By:</b> {report_data.get('approved_by', 'N/A')}
        """

        content.append(Paragraph(info_text, self.styles['InfoText']))

        if report_data.get('remarks'):
            content.append(Spacer(1, 10))
            content.append(Paragraph("<b>Remarks:</b>", self.styles['SubHeading']))
            content.append(Paragraph(report_data['remarks'], self.styles['InfoText']))

        return content

    def _build_module_specs(self, report_data: Dict[str, Any]) -> List:
        """Build module specifications section"""
        content = []

        content.append(Paragraph("Module Specifications", self.styles['SectionHeading']))

        modules = report_data.get('test_modules', [])
        if modules:
            module = modules[0]  # Primary module

            spec_data = [
                ['Parameter', 'Value'],
                ['Manufacturer', module.get('manufacturer', 'N/A')],
                ['Model Number', module.get('model_number', 'N/A')],
                ['Serial Number', module.get('serial_number', 'N/A')],
                ['Technology Type', module.get('technology_type', 'N/A')],
                ['Rated Power (Pmax)', f"{module.get('rated_power_pmax', 'N/A')} W"],
                ['Open Circuit Voltage (Voc)', f"{module.get('open_circuit_voltage_voc', 'N/A')} V"],
                ['Short Circuit Current (Isc)', f"{module.get('short_circuit_current_isc', 'N/A')} A"],
                ['Efficiency', f"{module.get('efficiency', 'N/A')} %"],
            ]

            spec_table = Table(spec_data, colWidths=[70*mm, 80*mm])
            spec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))

            content.append(spec_table)

        return content

    def _build_test_results(self, report_data: Dict[str, Any]) -> List:
        """Build test results section"""
        content = []

        content.append(Paragraph("Test Results", self.styles['SectionHeading']))

        # Build results table based on standard
        standard = report_data.get('iec_standard', '')

        if 'IEC 61215' in standard:
            tests = report_data.get('iec_61215_tests', [])
            content.extend(self._build_iec_61215_results(tests))
        elif 'IEC 61730' in standard:
            tests = report_data.get('iec_61730_tests', [])
            content.extend(self._build_iec_61730_results(tests))
        elif 'IEC 61701' in standard:
            tests = report_data.get('iec_61701_tests', [])
            content.extend(self._build_iec_61701_results(tests))

        return content

    def _build_iec_61215_results(self, tests: List[Dict]) -> List:
        """Build IEC 61215 test results table"""
        content = []

        for test in tests:
            content.append(Paragraph(
                f"<b>{test.get('test_name', 'N/A')}</b> ({test.get('test_sequence', '')})",
                self.styles['SubHeading']
            ))

            result_data = [
                ['Parameter', 'Initial', 'Final', 'Degradation', 'Result'],
                [
                    'Power (Pmax)',
                    f"{test.get('initial_pmax', 'N/A')} W",
                    f"{test.get('final_pmax', 'N/A')} W",
                    f"{test.get('power_degradation', 'N/A')} %",
                    test.get('result', 'N/A')
                ]
            ]

            result_table = Table(result_data, colWidths=[40*mm, 25*mm, 25*mm, 30*mm, 30*mm])
            result_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white]),
            ]))

            content.append(result_table)
            content.append(Spacer(1, 10))

        return content

    def _build_iec_61730_results(self, tests: List[Dict]) -> List:
        """Build IEC 61730 test results table"""
        content = []

        # Implementation similar to _build_iec_61215_results
        # Customized for safety tests
        for test in tests:
            content.append(Paragraph(
                f"<b>{test.get('test_name', 'N/A')}</b>",
                self.styles['SubHeading']
            ))

            result_text = f"""
            <b>Test Class:</b> {test.get('test_class', 'N/A')}<br/>
            <b>Insulation Resistance:</b> {test.get('insulation_resistance', 'N/A')} MΩ<br/>
            <b>Wet Leakage Current:</b> {test.get('wet_leakage_current', 'N/A')} mA<br/>
            <b>Result:</b> {test.get('result', 'N/A')}
            """

            content.append(Paragraph(result_text, self.styles['InfoText']))
            content.append(Spacer(1, 10))

        return content

    def _build_iec_61701_results(self, tests: List[Dict]) -> List:
        """Build IEC 61701 test results table"""
        content = []

        for test in tests:
            content.append(Paragraph(
                f"<b>{test.get('test_name', 'N/A')}</b> (Level {test.get('severity_level', 'N/A')})",
                self.styles['SubHeading']
            ))

            result_data = [
                ['Parameter', 'Initial', 'Final', 'Degradation'],
                [
                    'Power (Pmax)',
                    f"{test.get('initial_pmax', 'N/A')} W",
                    f"{test.get('final_pmax', 'N/A')} W",
                    f"{test.get('pmax_degradation', 'N/A')} %"
                ]
            ]

            result_table = Table(result_data, colWidths=[40*mm, 35*mm, 35*mm, 40*mm])
            result_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))

            content.append(result_table)
            content.append(Spacer(1, 10))

        return content

    def _build_graphs_section(self, graphs: List[Dict]) -> List:
        """Build graphs section"""
        content = []

        content.append(Paragraph("Test Graphs", self.styles['SectionHeading']))

        for graph in graphs:
            if graph.get('file_path') and os.path.exists(graph['file_path']):
                content.append(Paragraph(
                    f"<b>{graph.get('title', 'Graph')}</b>",
                    self.styles['SubHeading']
                ))

                if graph.get('description'):
                    content.append(Paragraph(graph['description'], self.styles['InfoText']))

                # Add image
                img = Image(graph['file_path'], width=140*mm, height=100*mm)
                content.append(img)
                content.append(Spacer(1, 15))

        return content

    def _build_evaluation_summary(self, report_data: Dict[str, Any]) -> List:
        """Build evaluation summary"""
        content = []

        content.append(Paragraph("Evaluation Summary", self.styles['SectionHeading']))

        # Overall result
        result = report_data.get('overall_result', 'NOT_TESTED')
        result_text = f"""
        <b>Overall Test Result:</b> <font color='{"green" if result == "PASS" else "red"}'>{result}</font><br/>
        <b>Conclusion:</b> The tested PV module has {'successfully passed' if result == 'PASS' else 'failed'}
        the {report_data.get('iec_standard', '')} test requirements.
        """

        content.append(Paragraph(result_text, self.styles['InfoText']))

        return content

    def _build_signatures(self, report_data: Dict[str, Any]) -> List:
        """Build signature section"""
        content = []

        sig_data = [
            ['Tested By:', 'Reviewed By:', 'Approved By:'],
            [
                report_data.get('tested_by', '____________________'),
                report_data.get('reviewed_by', '____________________'),
                report_data.get('approved_by', '____________________')
            ],
            ['Date: __________', 'Date: __________', 'Date: __________']
        ]

        sig_table = Table(sig_data, colWidths=[50*mm, 50*mm, 50*mm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 20),
        ]))

        content.append(sig_table)

        return content
