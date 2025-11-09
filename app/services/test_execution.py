"""
Test Execution Service
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.iec_tests import (
    TestReport, TestModule, IEC61215Test, IEC61730Test,
    IEC61701Test, TestDataPoint, TestGraph, TestCertificate,
    TestStatus, TestResult
)
from app.services.graph_generator import GraphGenerator
from app.services.pass_fail_evaluator import PassFailEvaluator
from app.services.report_generator import ReportGenerator
from app.services.certificate_generator import CertificateGenerator
import logging

logger = logging.getLogger(__name__)


class TestExecutionService:
    """Handle test execution workflow"""

    def __init__(self, db: Session):
        self.db = db
        self.graph_generator = GraphGenerator()
        self.evaluator = PassFailEvaluator()
        self.report_generator = ReportGenerator()
        self.certificate_generator = CertificateGenerator()

    def create_test_report(
        self,
        report_data: Dict[str, Any]
    ) -> TestReport:
        """
        Create new test report

        Args:
            report_data: Report creation data

        Returns:
            Created TestReport instance
        """
        report = TestReport(**report_data)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        logger.info(f"Created test report: {report.report_number}")
        return report

    def add_test_module(
        self,
        report_id: int,
        module_data: Dict[str, Any]
    ) -> TestModule:
        """
        Add module specifications to report

        Args:
            report_id: Test report ID
            module_data: Module specification data

        Returns:
            Created TestModule instance
        """
        module = TestModule(report_id=report_id, **module_data)
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)

        return module

    def add_iec_61215_test(
        self,
        report_id: int,
        test_data: Dict[str, Any]
    ) -> IEC61215Test:
        """
        Add IEC 61215 test to report

        Args:
            report_id: Test report ID
            test_data: Test data

        Returns:
            Created IEC61215Test instance
        """
        test = IEC61215Test(report_id=report_id, **test_data)
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)

        return test

    def add_iec_61730_test(
        self,
        report_id: int,
        test_data: Dict[str, Any]
    ) -> IEC61730Test:
        """
        Add IEC 61730 test to report

        Args:
            report_id: Test report ID
            test_data: Test data

        Returns:
            Created IEC61730Test instance
        """
        test = IEC61730Test(report_id=report_id, **test_data)
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)

        return test

    def add_iec_61701_test(
        self,
        report_id: int,
        test_data: Dict[str, Any]
    ) -> IEC61701Test:
        """
        Add IEC 61701 test to report

        Args:
            report_id: Test report ID
            test_data: Test data

        Returns:
            Created IEC61701Test instance
        """
        test = IEC61701Test(report_id=report_id, **test_data)
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)

        return test

    def record_data_points(
        self,
        test_type: str,
        test_id: int,
        data_points: List[Dict[str, Any]]
    ) -> List[TestDataPoint]:
        """
        Record test data points

        Args:
            test_type: Type of test (iec_61215, iec_61730, iec_61701)
            test_id: Test ID
            data_points: List of data point measurements

        Returns:
            List of created TestDataPoint instances
        """
        created_points = []

        for point_data in data_points:
            point = TestDataPoint(**point_data)

            # Link to appropriate test type
            if test_type == "iec_61215":
                point.iec_61215_test_id = test_id
            elif test_type == "iec_61730":
                point.iec_61730_test_id = test_id
            elif test_type == "iec_61701":
                point.iec_61701_test_id = test_id

            self.db.add(point)
            created_points.append(point)

        self.db.commit()

        return created_points

    def evaluate_test(
        self,
        test_id: int,
        test_type: str,
        standard: str
    ) -> Dict[str, Any]:
        """
        Evaluate test results against criteria

        Args:
            test_id: Test ID
            test_type: Type of test
            standard: IEC standard

        Returns:
            Evaluation results
        """
        # Get test data
        if test_type == "iec_61215":
            test = self.db.query(IEC61215Test).filter(IEC61215Test.id == test_id).first()
            test_data = {
                "power_degradation": test.power_degradation,
                "visual_inspection_pass": test.visual_inspection_pass,
                "insulation_resistance": getattr(test, 'insulation_resistance', None)
            }
            results = self.evaluator.evaluate_iec_61215_test(test_data)

        elif test_type == "iec_61730":
            test = self.db.query(IEC61730Test).filter(IEC61730Test.id == test_id).first()
            test_data = {
                "insulation_resistance": test.insulation_resistance,
                "wet_leakage_current": test.wet_leakage_current,
                "dielectric_strength_pass": test.dielectric_strength_pass,
                "mechanical_load_pass": test.mechanical_load_pass,
                "impact_test_pass": test.impact_test_pass
            }
            results = self.evaluator.evaluate_iec_61730_test(test_data)

        elif test_type == "iec_61701":
            test = self.db.query(IEC61701Test).filter(IEC61701Test.id == test_id).first()
            test_data = {
                "pmax_degradation": test.pmax_degradation,
                "corrosion_observed": test.corrosion_observed,
                "delamination_observed": test.delamination_observed,
                "bubble_formation": test.bubble_formation
            }
            results = self.evaluator.evaluate_iec_61701_test(test_data)

        else:
            raise ValueError(f"Unknown test type: {test_type}")

        # Update test result
        test.result = results["overall_result"]
        test.acceptance_criteria = results
        self.db.commit()

        return results

    def generate_test_graphs(
        self,
        report_id: int,
        graph_configs: List[Dict[str, Any]]
    ) -> List[TestGraph]:
        """
        Generate graphs for test report

        Args:
            report_id: Test report ID
            graph_configs: List of graph configuration dictionaries

        Returns:
            List of created TestGraph instances
        """
        created_graphs = []

        for config in graph_configs:
            graph_type = config.get("graph_type")
            data = config.get("data")

            # Generate graph based on type
            if graph_type == "iv_curve":
                file_path = self.graph_generator.generate_iv_curve(
                    voltage_data=data["voltage"],
                    current_data=data["current"],
                    output_filename=f"iv_curve_report_{report_id}.png",
                    title=config.get("title", "I-V Characteristic Curve")
                )

            elif graph_type == "power_curve":
                file_path = self.graph_generator.generate_power_curve(
                    voltage_data=data["voltage"],
                    current_data=data["current"],
                    output_filename=f"power_curve_report_{report_id}.png",
                    title=config.get("title", "P-V Power Curve")
                )

            elif graph_type == "temperature_profile":
                file_path = self.graph_generator.generate_temperature_profile(
                    time_data=data["time"],
                    temperature_data=data["temperature"],
                    output_filename=f"temp_profile_report_{report_id}.png",
                    title=config.get("title", "Temperature Profile")
                )

            elif graph_type == "degradation_chart":
                file_path = self.graph_generator.generate_degradation_chart(
                    test_names=data["test_names"],
                    degradation_values=data["degradation"],
                    output_filename=f"degradation_report_{report_id}.png",
                    title=config.get("title", "Degradation Analysis")
                )

            else:
                logger.warning(f"Unknown graph type: {graph_type}")
                continue

            # Create graph record
            graph = TestGraph(
                report_id=report_id,
                graph_type=graph_type,
                title=config.get("title"),
                description=config.get("description"),
                file_path=file_path,
                file_format="png",
                x_axis_label=config.get("x_label"),
                y_axis_label=config.get("y_label"),
                graph_config=config
            )

            self.db.add(graph)
            created_graphs.append(graph)

        self.db.commit()

        return created_graphs

    def generate_report_pdf(
        self,
        report_id: int
    ) -> str:
        """
        Generate PDF report

        Args:
            report_id: Test report ID

        Returns:
            Path to generated PDF
        """
        # Get complete report data
        report = self.db.query(TestReport).filter(TestReport.id == report_id).first()

        if not report:
            raise ValueError(f"Report {report_id} not found")

        # Prepare report data
        report_data = {
            "id": report.id,
            "report_number": report.report_number,
            "customer_name": report.customer_name,
            "sample_id": report.sample_id,
            "module_model": report.module_model,
            "iec_standard": report.iec_standard.value,
            "test_type": report.test_type,
            "test_objective": report.test_objective,
            "status": report.status.value,
            "overall_result": report.overall_result.value,
            "tested_by": report.tested_by,
            "reviewed_by": report.reviewed_by,
            "approved_by": report.approved_by,
            "test_start_date": report.test_start_date,
            "report_date": report.report_date,
            "remarks": report.remarks,
            "test_modules": [self._serialize_module(m) for m in report.test_modules],
            "iec_61215_tests": [self._serialize_iec_61215_test(t) for t in report.iec_61215_tests],
            "iec_61730_tests": [self._serialize_iec_61730_test(t) for t in report.iec_61730_tests],
            "iec_61701_tests": [self._serialize_iec_61701_test(t) for t in report.iec_61701_tests],
            "graphs": [self._serialize_graph(g) for g in report.graphs],
        }

        # Generate PDF
        output_filename = f"test_report_{report.report_number}.pdf"
        pdf_path = self.report_generator.generate_test_report(
            report_data=report_data,
            output_filename=output_filename,
            include_graphs=True
        )

        # Update report status
        report.status = TestStatus.COMPLETED
        self.db.commit()

        return pdf_path

    def generate_certificate(
        self,
        report_id: int
    ) -> TestCertificate:
        """
        Generate test certificate with QR code

        Args:
            report_id: Test report ID

        Returns:
            Created TestCertificate instance
        """
        # Get report
        report = self.db.query(TestReport).filter(TestReport.id == report_id).first()

        if not report:
            raise ValueError(f"Report {report_id} not found")

        # Prepare report data
        report_data = {
            "id": report.id,
            "report_number": report.report_number,
            "customer_name": report.customer_name,
            "module_model": report.module_model,
            "iec_standard": report.iec_standard.value,
            "test_type": report.test_type,
            "overall_result": report.overall_result.value,
            "approved_by": report.approved_by
        }

        # Generate certificate
        cert_files = self.certificate_generator.generate_certificate_from_report(
            report_data=report_data
        )

        # Extract certificate number from filename
        cert_number = self.certificate_generator._generate_certificate_number(report_data)

        # Create certificate record
        certificate = TestCertificate(
            report_id=report_id,
            certificate_number=cert_number,
            issue_date=datetime.now(),
            qr_code_data=f"https://verify.lab.com/cert/{cert_number}",
            qr_code_image_path=cert_files.get("qr_code"),
            signature_hash=cert_files.get("signature_hash"),
            signed_by=report.approved_by or "Lab Director",
            signing_timestamp=datetime.now(),
            certificate_pdf_path=cert_files.get("certificate_pdf"),
            verification_url=f"https://verify.lab.com/cert/{cert_number}",
            is_valid=True
        )

        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)

        return certificate

    def _serialize_module(self, module: TestModule) -> Dict:
        """Serialize module object to dictionary"""
        return {
            "manufacturer": module.manufacturer,
            "model_number": module.model_number,
            "serial_number": module.serial_number,
            "technology_type": module.technology_type,
            "rated_power_pmax": module.rated_power_pmax,
            "open_circuit_voltage_voc": module.open_circuit_voltage_voc,
            "short_circuit_current_isc": module.short_circuit_current_isc,
            "efficiency": module.efficiency
        }

    def _serialize_iec_61215_test(self, test: IEC61215Test) -> Dict:
        """Serialize IEC 61215 test to dictionary"""
        return {
            "test_sequence": test.test_sequence,
            "test_name": test.test_name,
            "initial_pmax": test.initial_pmax,
            "final_pmax": test.final_pmax,
            "power_degradation": test.power_degradation,
            "result": test.result.value if test.result else "NOT_TESTED"
        }

    def _serialize_iec_61730_test(self, test: IEC61730Test) -> Dict:
        """Serialize IEC 61730 test to dictionary"""
        return {
            "test_name": test.test_name,
            "test_class": test.test_class,
            "insulation_resistance": test.insulation_resistance,
            "wet_leakage_current": test.wet_leakage_current,
            "result": test.result.value if test.result else "NOT_TESTED"
        }

    def _serialize_iec_61701_test(self, test: IEC61701Test) -> Dict:
        """Serialize IEC 61701 test to dictionary"""
        return {
            "test_name": test.test_name,
            "severity_level": test.severity_level,
            "initial_pmax": test.initial_pmax,
            "final_pmax": test.final_pmax,
            "pmax_degradation": test.pmax_degradation,
            "result": test.result.value if test.result else "NOT_TESTED"
        }

    def _serialize_graph(self, graph: TestGraph) -> Dict:
        """Serialize graph to dictionary"""
        return {
            "graph_type": graph.graph_type,
            "title": graph.title,
            "description": graph.description,
            "file_path": graph.file_path
        }
