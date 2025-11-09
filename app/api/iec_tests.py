"""
IEC Test API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.iec_tests import (
    TestReportCreate, TestReportUpdate, TestReportResponse,
    TestModuleCreate, IEC61215TestCreate, IEC61730TestCreate,
    IEC61701TestCreate, TestDataPointCreate, TestExecutionRequest,
    TestExecutionResponse, TestCertificateResponse
)
from app.models.iec_tests import TestReport, TestStatus
from app.services.test_execution import TestExecutionService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/iec-tests", tags=["IEC Tests"])


@router.post("/reports", response_model=TestReportResponse, status_code=status.HTTP_201_CREATED)
def create_test_report(
    report: TestReportCreate,
    db: Session = Depends(get_db)
):
    """Create a new test report"""
    try:
        service = TestExecutionService(db)
        created_report = service.create_test_report(report.model_dump())
        return created_report
    except Exception as e:
        logger.error(f"Error creating test report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/reports", response_model=List[TestReportResponse])
def list_test_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all test reports"""
    reports = db.query(TestReport).offset(skip).limit(limit).all()
    return reports


@router.get("/reports/{report_id}", response_model=TestReportResponse)
def get_test_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific test report"""
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test report {report_id} not found"
        )
    return report


@router.put("/reports/{report_id}", response_model=TestReportResponse)
def update_test_report(
    report_id: int,
    report_update: TestReportUpdate,
    db: Session = Depends(get_db)
):
    """Update a test report"""
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test report {report_id} not found"
        )

    # Update fields
    update_data = report_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Delete a test report"""
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test report {report_id} not found"
        )

    db.delete(report)
    db.commit()
    return None


@router.post("/reports/{report_id}/modules")
def add_test_module(
    report_id: int,
    module: TestModuleCreate,
    db: Session = Depends(get_db)
):
    """Add module specifications to a test report"""
    try:
        service = TestExecutionService(db)
        created_module = service.add_test_module(report_id, module.model_dump())
        return created_module
    except Exception as e:
        logger.error(f"Error adding test module: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reports/{report_id}/iec-61215-tests")
def add_iec_61215_test(
    report_id: int,
    test: IEC61215TestCreate,
    db: Session = Depends(get_db)
):
    """Add IEC 61215 test to report"""
    try:
        service = TestExecutionService(db)
        created_test = service.add_iec_61215_test(report_id, test.model_dump())
        return created_test
    except Exception as e:
        logger.error(f"Error adding IEC 61215 test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reports/{report_id}/iec-61730-tests")
def add_iec_61730_test(
    report_id: int,
    test: IEC61730TestCreate,
    db: Session = Depends(get_db)
):
    """Add IEC 61730 test to report"""
    try:
        service = TestExecutionService(db)
        created_test = service.add_iec_61730_test(report_id, test.model_dump())
        return created_test
    except Exception as e:
        logger.error(f"Error adding IEC 61730 test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reports/{report_id}/iec-61701-tests")
def add_iec_61701_test(
    report_id: int,
    test: IEC61701TestCreate,
    db: Session = Depends(get_db)
):
    """Add IEC 61701 test to report"""
    try:
        service = TestExecutionService(db)
        created_test = service.add_iec_61701_test(report_id, test.model_dump())
        return created_test
    except Exception as e:
        logger.error(f"Error adding IEC 61701 test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/tests/{test_type}/{test_id}/data-points")
def record_test_data(
    test_type: str,
    test_id: int,
    data_points: List[TestDataPointCreate],
    db: Session = Depends(get_db)
):
    """Record test data points"""
    try:
        service = TestExecutionService(db)
        created_points = service.record_data_points(
            test_type=test_type,
            test_id=test_id,
            data_points=[dp.model_dump() for dp in data_points]
        )
        return {"recorded": len(created_points), "data_points": created_points}
    except Exception as e:
        logger.error(f"Error recording data points: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/tests/{test_type}/{test_id}/evaluate")
def evaluate_test(
    test_type: str,
    test_id: int,
    standard: str,
    db: Session = Depends(get_db)
):
    """Evaluate test results against criteria"""
    try:
        service = TestExecutionService(db)
        results = service.evaluate_test(
            test_id=test_id,
            test_type=test_type,
            standard=standard
        )
        return results
    except Exception as e:
        logger.error(f"Error evaluating test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reports/{report_id}/graphs")
def generate_graphs(
    report_id: int,
    graph_configs: List[dict],
    db: Session = Depends(get_db)
):
    """Generate graphs for test report"""
    try:
        service = TestExecutionService(db)
        created_graphs = service.generate_test_graphs(
            report_id=report_id,
            graph_configs=graph_configs
        )
        return {"generated": len(created_graphs), "graphs": created_graphs}
    except Exception as e:
        logger.error(f"Error generating graphs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reports/{report_id}/generate-pdf")
def generate_report_pdf(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Generate PDF report"""
    try:
        service = TestExecutionService(db)
        pdf_path = service.generate_report_pdf(report_id=report_id)
        return {"pdf_path": pdf_path, "status": "completed"}
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reports/{report_id}/generate-certificate", response_model=TestCertificateResponse)
def generate_certificate(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Generate test certificate with QR code"""
    try:
        service = TestExecutionService(db)
        certificate = service.generate_certificate(report_id=report_id)
        return certificate
    except Exception as e:
        logger.error(f"Error generating certificate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/execute", response_model=TestExecutionResponse)
def execute_test(
    execution_request: TestExecutionRequest,
    db: Session = Depends(get_db)
):
    """Execute test with data acquisition and auto-evaluation"""
    try:
        service = TestExecutionService(db)

        # Get report
        report = db.query(TestReport).filter(
            TestReport.id == execution_request.report_id
        ).first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {execution_request.report_id} not found"
            )

        # Update status
        report.status = TestStatus.IN_PROGRESS
        db.commit()

        # This is a simplified execution - in production, this would integrate
        # with actual test equipment and data acquisition systems

        response = {
            "report_id": execution_request.report_id,
            "status": "completed",
            "tests_executed": 1,
            "data_points_recorded": len(execution_request.test_data_points),
            "evaluation_results": None
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
