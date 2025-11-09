"""Business logic for CAPA management."""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from backend.database.models import CAPAAction, CAPAStatus, CAPAType
from backend.api.schemas import CAPAActionCreate, CAPAActionUpdate
from datetime import datetime
from typing import List, Optional


class CAPAService:
    """Service class for CAPA operations."""

    @staticmethod
    def generate_capa_number(db: Session) -> str:
        """
        Generate CAPA number in format: CAPA-YYYY-XXX

        Args:
            db: Database session

        Returns:
            str: Generated CAPA number
        """
        current_year = datetime.now().year

        # Get count of CAPAs for current year
        count = db.query(func.count(CAPAAction.id)).filter(
            extract('year', CAPAAction.created_at) == current_year
        ).scalar()

        # Increment for next number
        next_number = (count or 0) + 1

        return f"CAPA-{current_year}-{next_number:03d}"

    @staticmethod
    def create_capa(db: Session, capa_data: CAPAActionCreate) -> CAPAAction:
        """
        Create a new CAPA Action.

        Args:
            db: Database session
            capa_data: CAPA creation data

        Returns:
            CAPAAction: Created CAPA record
        """
        capa_number = CAPAService.generate_capa_number(db)

        # Convert resources_required to JSON if it's a list
        capa_dict = capa_data.model_dump(exclude_unset=True)
        if 'resources_required' in capa_dict and isinstance(capa_dict['resources_required'], list):
            capa_dict['resources_required'] = capa_dict['resources_required']

        capa = CAPAAction(
            capa_number=capa_number,
            **capa_dict
        )

        db.add(capa)
        db.commit()
        db.refresh(capa)

        return capa

    @staticmethod
    def get_capa_by_id(db: Session, capa_id: int) -> Optional[CAPAAction]:
        """Get CAPA by ID."""
        return db.query(CAPAAction).filter(CAPAAction.id == capa_id).first()

    @staticmethod
    def get_capa_by_number(db: Session, capa_number: str) -> Optional[CAPAAction]:
        """Get CAPA by CAPA number."""
        return db.query(CAPAAction).filter(CAPAAction.capa_number == capa_number).first()

    @staticmethod
    def get_capas_by_nc(db: Session, nc_id: int) -> List[CAPAAction]:
        """Get all CAPAs for a specific NC."""
        return db.query(CAPAAction).filter(CAPAAction.nc_id == nc_id).all()

    @staticmethod
    def get_all_capas(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CAPAStatus] = None,
        capa_type: Optional[CAPAType] = None
    ) -> List[CAPAAction]:
        """
        Get all CAPAs with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            capa_type: Filter by CAPA type

        Returns:
            List[CAPAAction]: List of CAPA records
        """
        query = db.query(CAPAAction)

        if status:
            query = query.filter(CAPAAction.status == status)
        if capa_type:
            query = query.filter(CAPAAction.capa_type == capa_type)

        return query.order_by(CAPAAction.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_capa(db: Session, capa_id: int, capa_update: CAPAActionUpdate) -> Optional[CAPAAction]:
        """
        Update a CAPA Action.

        Args:
            db: Database session
            capa_id: CAPA ID
            capa_update: Update data

        Returns:
            CAPAAction: Updated CAPA record
        """
        capa = CAPAService.get_capa_by_id(db, capa_id)
        if not capa:
            return None

        update_data = capa_update.model_dump(exclude_unset=True)

        # Handle resources_required conversion
        if 'resources_required' in update_data and isinstance(update_data['resources_required'], list):
            update_data['resources_required'] = update_data['resources_required']

        for field, value in update_data.items():
            setattr(capa, field, value)

        db.commit()
        db.refresh(capa)

        return capa

    @staticmethod
    def delete_capa(db: Session, capa_id: int) -> bool:
        """
        Delete a CAPA Action.

        Args:
            db: Database session
            capa_id: CAPA ID

        Returns:
            bool: True if deleted, False if not found
        """
        capa = CAPAService.get_capa_by_id(db, capa_id)
        if not capa:
            return False

        db.delete(capa)
        db.commit()

        return True

    @staticmethod
    def get_overdue_capas(db: Session) -> List[CAPAAction]:
        """
        Get all overdue CAPA actions.

        Returns:
            List[CAPAAction]: List of overdue CAPAs
        """
        today = datetime.now().date()
        return db.query(CAPAAction).filter(
            CAPAAction.due_date < today,
            CAPAAction.status.in_([CAPAStatus.PENDING, CAPAStatus.IN_PROGRESS])
        ).all()

    @staticmethod
    def get_capa_statistics(db: Session) -> dict:
        """
        Get CAPA statistics.

        Returns:
            dict: Statistics about CAPAs
        """
        total = db.query(func.count(CAPAAction.id)).scalar()
        pending = db.query(func.count(CAPAAction.id)).filter(
            CAPAAction.status == CAPAStatus.PENDING
        ).scalar()
        in_progress = db.query(func.count(CAPAAction.id)).filter(
            CAPAAction.status == CAPAStatus.IN_PROGRESS
        ).scalar()
        completed = db.query(func.count(CAPAAction.id)).filter(
            CAPAAction.status == CAPAStatus.COMPLETED
        ).scalar()

        # Count by type
        type_counts = db.query(
            CAPAAction.capa_type,
            func.count(CAPAAction.id)
        ).group_by(CAPAAction.capa_type).all()

        # Count overdue
        overdue = len(CAPAService.get_overdue_capas(db))

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "overdue": overdue,
            "by_type": {str(capa_type): count for capa_type, count in type_counts}
        }
