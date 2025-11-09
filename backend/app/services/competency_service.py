"""
Competency Gap Analysis Service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case
from datetime import date, timedelta
from typing import List, Dict, Optional
from ..models.training import TrainingMaster, EmployeeTrainingMatrix
from ..schemas.training import CompetencyGap, CompetencyGapSummary


class CompetencyService:
    """Service for competency gap analysis"""

    @staticmethod
    def analyze_competency_gaps(
        db: Session,
        department: Optional[str] = None,
        employee_id: Optional[str] = None,
        gap_status_filter: Optional[str] = None
    ) -> CompetencyGapSummary:
        """
        Perform comprehensive competency gap analysis

        Args:
            db: Database session
            department: Filter by department
            employee_id: Filter by specific employee
            gap_status_filter: Filter by gap status (Expired, Expiring Soon, Not Trained, Gap Exists)

        Returns:
            CompetencyGapSummary with detailed gap analysis
        """
        # Build query with joins
        query = db.query(
            EmployeeTrainingMatrix.employee_id,
            EmployeeTrainingMatrix.employee_name,
            EmployeeTrainingMatrix.department,
            EmployeeTrainingMatrix.job_role,
            TrainingMaster.training_name,
            TrainingMaster.category,
            EmployeeTrainingMatrix.current_level,
            EmployeeTrainingMatrix.target_level,
            EmployeeTrainingMatrix.status,
            EmployeeTrainingMatrix.competency_status,
            EmployeeTrainingMatrix.last_trained_date,
            EmployeeTrainingMatrix.certificate_valid_until
        ).join(
            TrainingMaster,
            EmployeeTrainingMatrix.training_id == TrainingMaster.id
        ).filter(
            EmployeeTrainingMatrix.required == True
        )

        # Apply filters
        if department:
            query = query.filter(EmployeeTrainingMatrix.department == department)
        if employee_id:
            query = query.filter(EmployeeTrainingMatrix.employee_id == employee_id)

        results = query.all()

        # Analyze gaps
        gaps = []
        not_trained = 0
        expired = 0
        expiring_soon = 0
        gap_exists = 0
        competent = 0

        today = date.today()

        for row in results:
            # Determine gap status
            gap_status = CompetencyService._determine_gap_status(
                row.certificate_valid_until,
                row.current_level,
                row.target_level,
                today
            )

            # Calculate days until expiry
            days_until_expiry = None
            if row.certificate_valid_until:
                days_until_expiry = (row.certificate_valid_until - today).days

            # Create gap entry
            gap = CompetencyGap(
                employee_id=row.employee_id,
                employee_name=row.employee_name,
                department=row.department,
                job_role=row.job_role,
                training_name=row.training_name,
                category=row.category,
                current_level=row.current_level,
                target_level=row.target_level,
                status=row.status,
                competency_status=row.competency_status,
                last_trained_date=row.last_trained_date,
                certificate_valid_until=row.certificate_valid_until,
                gap_status=gap_status,
                days_until_expiry=days_until_expiry
            )

            # Apply gap status filter if specified
            if gap_status_filter and gap_status != gap_status_filter:
                continue

            gaps.append(gap)

            # Count by gap status
            if gap_status == "Expired":
                expired += 1
            elif gap_status == "Expiring Soon":
                expiring_soon += 1
            elif gap_status == "Not Trained":
                not_trained += 1
            elif gap_status == "Gap Exists":
                gap_exists += 1
            elif gap_status == "Competent":
                competent += 1

        # Get unique employee count
        unique_employees = len(set(gap.employee_id for gap in gaps))

        return CompetencyGapSummary(
            total_employees=unique_employees,
            total_training_requirements=len(gaps),
            not_trained_count=not_trained,
            expired_count=expired,
            expiring_soon_count=expiring_soon,
            gap_exists_count=gap_exists,
            competent_count=competent,
            gaps=gaps
        )

    @staticmethod
    def _determine_gap_status(
        cert_valid_until: Optional[date],
        current_level: Optional[str],
        target_level: Optional[str],
        today: date
    ) -> str:
        """Determine the gap status based on certificate validity and competency levels"""
        # Check if certificate expired
        if cert_valid_until and cert_valid_until < today:
            return "Expired"

        # Check if expiring soon (within 30 days)
        if cert_valid_until and (cert_valid_until - today).days <= 30:
            return "Expiring Soon"

        # Check if not trained
        if not current_level or current_level == "Untrained":
            return "Not Trained"

        # Check if gap exists between current and target
        if target_level and current_level != target_level:
            return "Gap Exists"

        # Otherwise competent
        return "Competent"

    @staticmethod
    def get_employee_development_plan(
        db: Session,
        employee_id: str
    ) -> Dict:
        """
        Generate individual development plan for an employee

        Args:
            db: Database session
            employee_id: Employee ID

        Returns:
            Dictionary with development plan details
        """
        # Get all training requirements for employee
        matrix_entries = db.query(EmployeeTrainingMatrix).join(
            TrainingMaster,
            EmployeeTrainingMatrix.training_id == TrainingMaster.id
        ).filter(
            and_(
                EmployeeTrainingMatrix.employee_id == employee_id,
                EmployeeTrainingMatrix.required == True
            )
        ).all()

        if not matrix_entries:
            return {
                "employee_id": employee_id,
                "message": "No training requirements found"
            }

        required_trainings = []
        completed_trainings = []
        expiring_soon = []

        today = date.today()

        for entry in matrix_entries:
            training_info = {
                "training_name": entry.training.training_name,
                "category": entry.training.category,
                "current_level": entry.current_level,
                "target_level": entry.target_level,
                "status": entry.status,
                "last_trained": entry.last_trained_date,
                "valid_until": entry.certificate_valid_until
            }

            if entry.status in ["Required", "In Progress"]:
                required_trainings.append(training_info)
            elif entry.status == "Completed":
                if entry.certificate_valid_until and (entry.certificate_valid_until - today).days <= 30:
                    expiring_soon.append(training_info)
                else:
                    completed_trainings.append(training_info)

        return {
            "employee_id": employee_id,
            "employee_name": matrix_entries[0].employee_name if matrix_entries else "",
            "department": matrix_entries[0].department if matrix_entries else "",
            "job_role": matrix_entries[0].job_role if matrix_entries else "",
            "required_trainings": required_trainings,
            "completed_trainings": completed_trainings,
            "expiring_soon": expiring_soon,
            "total_required": len(required_trainings),
            "total_completed": len(completed_trainings),
            "total_expiring": len(expiring_soon)
        }

    @staticmethod
    def get_department_competency_overview(
        db: Session,
        department: str
    ) -> Dict:
        """
        Get competency overview for a department

        Args:
            db: Database session
            department: Department name

        Returns:
            Dictionary with department competency statistics
        """
        # Get all employees in department
        employees = db.query(
            EmployeeTrainingMatrix.employee_id,
            EmployeeTrainingMatrix.employee_name
        ).filter(
            EmployeeTrainingMatrix.department == department
        ).distinct().all()

        # Get competency gap analysis for department
        gap_analysis = CompetencyService.analyze_competency_gaps(
            db,
            department=department
        )

        # Calculate compliance percentage
        total_requirements = gap_analysis.total_training_requirements
        compliance_count = gap_analysis.competent_count
        compliance_rate = (compliance_count / total_requirements * 100) if total_requirements > 0 else 0

        return {
            "department": department,
            "total_employees": len(employees),
            "total_training_requirements": total_requirements,
            "compliance_rate": round(compliance_rate, 2),
            "competent_count": gap_analysis.competent_count,
            "not_trained_count": gap_analysis.not_trained_count,
            "expired_count": gap_analysis.expired_count,
            "expiring_soon_count": gap_analysis.expiring_soon_count,
            "gap_exists_count": gap_analysis.gap_exists_count
        }
