"""
IEC Test Report Generation API (Session 6)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.iec_reports import IECTestExecution, IECTestData, IECReport


router = APIRouter()


class IECTestExecutionCreate(BaseModel):
    sample_id: int
    test_standard: str
    test_sequence: str
    test_description: str
    performed_by_id: int


class IECTestDataCreate(BaseModel):
    test_execution_id: int
    measurement_time: datetime
    parameter_name: str
    measured_value: float
    unit: str
    acceptance_min: float = None
    acceptance_max: float = None


@router.post("/executions")
def create_test_execution(execution: IECTestExecutionCreate, db: Session = Depends(get_db)):
    """Start IEC test execution"""

    db_execution = IECTestExecution(
        **execution.dict(),
        start_date=datetime.now(),
        status="in_progress"
    )

    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)

    return {"message": "Test execution started", "id": db_execution.id}


@router.post("/data")
def record_test_data(data: IECTestDataCreate, db: Session = Depends(get_db)):
    """Record IEC test data point"""

    # Determine pass/fail
    result = "Pass"
    if data.acceptance_min is not None and data.measured_value < data.acceptance_min:
        result = "Fail"
    if data.acceptance_max is not None and data.measured_value > data.acceptance_max:
        result = "Fail"

    db_data = IECTestData(**data.dict(), result=result)
    db.add(db_data)
    db.commit()

    return {"message": "Test data recorded", "result": result}


@router.post("/executions/{execution_id}/complete")
def complete_test_execution(execution_id: int, reviewed_by_id: int, db: Session = Depends(get_db)):
    """Complete test execution"""

    execution = db.query(IECTestExecution).filter(IECTestExecution.id == execution_id).first()
    if not execution:
        return {"error": "Test execution not found"}

    execution.status = "completed"
    execution.end_date = datetime.now()
    execution.reviewed_by_id = reviewed_by_id

    db.commit()

    return {"message": "Test execution completed"}


@router.post("/generate-report")
def generate_iec_report(
    sample_id: int,
    test_standard: str,
    generated_by_id: int,
    db: Session = Depends(get_db)
):
    """Generate IEC test report with graphs and certificate"""

    # Generate report number
    year = datetime.now().year
    last_report = db.query(IECReport).filter(
        IECReport.report_number.like(f"IEC-{year}-%")
    ).order_by(IECReport.id.desc()).first()

    if last_report:
        last_num = int(last_report.report_number.split("-")[-1])
        report_number = f"IEC-{year}-{last_num + 1:04d}"
    else:
        report_number = f"IEC-{year}-0001"

    # Get all test executions for this sample
    executions = db.query(IECTestExecution).filter(
        IECTestExecution.sample_id == sample_id,
        IECTestExecution.test_standard == test_standard
    ).all()

    # Determine overall result
    overall_result = "Pass"
    for execution in executions:
        test_data = db.query(IECTestData).filter(
            IECTestData.test_execution_id == execution.id
        ).all()

        for data in test_data:
            if data.result == "Fail":
                overall_result = "Fail"
                break

    # Create report record
    db_report = IECReport(
        report_number=report_number,
        sample_id=sample_id,
        test_standard=test_standard,
        report_date=date.today(),
        overall_result=overall_result,
        generated_by_id=generated_by_id
    )

    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    # TODO: Generate PDF report with graphs
    # TODO: Generate digital certificate with QR code

    return {
        "message": "Report generated",
        "report_number": report_number,
        "overall_result": overall_result
    }


@router.get("/reports")
def list_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all IEC reports"""
    reports = db.query(IECReport).offset(skip).limit(limit).all()
    return reports


@router.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get report details"""
    report = db.query(IECReport).filter(IECReport.id == report_id).first()
    return report
