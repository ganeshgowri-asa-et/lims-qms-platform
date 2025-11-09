"""Business logic for Non-Conformance management."""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from backend.database.models import NonConformance, NCStatus
from backend.api.schemas import NonConformanceCreate, NonConformanceUpdate
from datetime import datetime
from typing import List, Optional


class NCService:
    """Service class for Non-Conformance operations."""

    @staticmethod
    def generate_nc_number(db: Session) -> str:
        """
        Generate NC number in format: NC-YYYY-XXX

        Args:
            db: Database session

        Returns:
            str: Generated NC number
        """
        current_year = datetime.now().year

        # Get count of NCs for current year
        count = db.query(func.count(NonConformance.id)).filter(
            extract('year', NonConformance.created_at) == current_year
        ).scalar()

        # Increment for next number
        next_number = (count or 0) + 1

        return f"NC-{current_year}-{next_number:03d}"

    @staticmethod
    def create_nc(db: Session, nc_data: NonConformanceCreate) -> NonConformance:
        """
        Create a new Non-Conformance.

        Args:
            db: Database session
            nc_data: NC creation data

        Returns:
            NonConformance: Created NC record
        """
        nc_number = NCService.generate_nc_number(db)

        nc = NonConformance(
            nc_number=nc_number,
            **nc_data.model_dump(exclude_unset=True)
        )

        db.add(nc)
        db.commit()
        db.refresh(nc)

        return nc

    @staticmethod
    def get_nc_by_id(db: Session, nc_id: int) -> Optional[NonConformance]:
        """Get NC by ID."""
        return db.query(NonConformance).filter(NonConformance.id == nc_id).first()

    @staticmethod
    def get_nc_by_number(db: Session, nc_number: str) -> Optional[NonConformance]:
        """Get NC by NC number."""
        return db.query(NonConformance).filter(NonConformance.nc_number == nc_number).first()

    @staticmethod
    def get_all_ncs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[NCStatus] = None,
        severity: Optional[str] = None
    ) -> List[NonConformance]:
        """
        Get all NCs with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            severity: Filter by severity

        Returns:
            List[NonConformance]: List of NC records
        """
        query = db.query(NonConformance)

        if status:
            query = query.filter(NonConformance.status == status)
        if severity:
            query = query.filter(NonConformance.severity == severity)

        return query.order_by(NonConformance.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_nc(db: Session, nc_id: int, nc_update: NonConformanceUpdate) -> Optional[NonConformance]:
        """
        Update a Non-Conformance.

        Args:
            db: Database session
            nc_id: NC ID
            nc_update: Update data

        Returns:
            NonConformance: Updated NC record
        """
        nc = NCService.get_nc_by_id(db, nc_id)
        if not nc:
            return None

        update_data = nc_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(nc, field, value)

        db.commit()
        db.refresh(nc)

        return nc

    @staticmethod
    def delete_nc(db: Session, nc_id: int) -> bool:
        """
        Delete a Non-Conformance.

        Args:
            db: Database session
            nc_id: NC ID

        Returns:
            bool: True if deleted, False if not found
        """
        nc = NCService.get_nc_by_id(db, nc_id)
        if not nc:
            return False

        db.delete(nc)
        db.commit()

        return True

    @staticmethod
    def get_nc_statistics(db: Session) -> dict:
        """
        Get NC statistics.

        Returns:
            dict: Statistics about NCs
        """
        total = db.query(func.count(NonConformance.id)).scalar()
        open_count = db.query(func.count(NonConformance.id)).filter(
            NonConformance.status == NCStatus.OPEN
        ).scalar()
        closed_count = db.query(func.count(NonConformance.id)).filter(
            NonConformance.status == NCStatus.CLOSED
        ).scalar()

        # Count by severity
        severity_counts = db.query(
            NonConformance.severity,
            func.count(NonConformance.id)
        ).group_by(NonConformance.severity).all()

        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "by_severity": {str(severity): count for severity, count in severity_counts}
        }
